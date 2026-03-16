"""
script/writer.py — generate a two-host podcast script using the Gemini API.

Uses the current google-genai SDK (replaces deprecated google-generativeai).

Flow:
  1. Condense scraped research into a context block (summarise if too long).
  2. Send system + user prompts to Gemini with JSON output mode enabled.
  3. Parse, validate, and return the script as a list of turn dicts.
"""

import asyncio
import json
import re
from typing import Any

from google import genai
from google.genai import types
from google.genai.errors import ClientError

import config
from script.prompts import build_system_prompt, build_user_prompt, build_summary_prompt


# ── Model config ───────────────────────────────────────────────────────────────

# Ordered preference — writer falls back down the list on quota errors
GEMINI_MODELS = [
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-2.5-flash-lite",
    "gemini-flash-lite-latest",
]

# Approximate chars per token for rough budget calculations
CHARS_PER_TOKEN = 4

# Leave headroom for prompt overhead and the response itself
MAX_RESEARCH_CHARS = 60_000   # ~15k tokens of source material

# Words per minute for spoken audio (used to calculate script length target)
WORDS_PER_MINUTE = 150

# Seconds to wait before retrying on a rate-limit response
RETRY_WAIT_SECONDS = 60


# ── Public API ─────────────────────────────────────────────────────────────────

async def generate_script(research_data: dict[str, Any]) -> list[dict[str, str]]:
    """
    Generate a two-host podcast script from research data.

    Args:
        research_data: Output from research.scraper.search_and_scrape(), containing:
                         - topic   : str
                         - sources : list of {title, url, snippet, score}
                         - content : list of {url, content}

    Returns:
        List of turn dicts: [{"host": "Ryan"|"Jenny", "line": "..."}, ...]
    """
    topic   = research_data["topic"]
    content = research_data.get("content", [])
    sources = research_data.get("sources", [])

    if not content and not sources:
        raise ValueError("No research content provided — run the research module first.")

    # ── Step 1: Build the research context block ───────────────────────────────
    print("[script] Preparing research context...")
    research_text = await _build_research_context(content, sources)

    # ── Step 2: Calculate target word count ───────────────────────────────────
    target_words = config.EPISODE_DURATION_MINUTES * WORDS_PER_MINUTE
    print(f"[script] Target: ~{target_words} words ({config.EPISODE_DURATION_MINUTES} min episode)")

    # ── Step 3: Call Gemini (with model fallback on quota errors) ──────────────
    raw_script = await _call_gemini_with_fallback(topic, research_text, target_words)

    # ── Step 4: Parse and validate ────────────────────────────────────────────
    print("[script] Parsing script...")
    script = _parse_script(raw_script)

    print(f"[script] Script generated: {len(script)} turns, "
          f"~{_count_words(script)} words.")
    return script


# ── Internal helpers ───────────────────────────────────────────────────────────

async def _build_research_context(
    content: list[dict],
    sources: list[dict],
) -> str:
    """
    Combine scraped article content into a single text block.
    If the combined length exceeds MAX_RESEARCH_CHARS, summarise each article
    individually with Gemini before combining.
    """
    if not content:
        # Fall back to search snippets if full article content isn't available
        snippets = "\n\n".join(
            f"Source: {s['url']}\n{s['snippet']}"
            for s in sources
        )
        print("[script] No full article content — using search snippets.")
        return snippets

    # Try combining full articles first
    combined = "\n\n---\n\n".join(
        f"Source: {page['url']}\n\n{page['content']}"
        for page in content
    )

    if len(combined) <= MAX_RESEARCH_CHARS:
        return combined

    # Content is too long — summarise each article individually (sequentially to
    # avoid firing multiple concurrent requests and exhausting the rate limit)
    print(f"[script] Content too long ({len(combined):,} chars) — summarising articles...")
    summaries = []
    for page in content:
        summary = await _summarise_article(page["content"], page["url"])
        summaries.append(summary)

    return "\n\n---\n\n".join(
        f"Source: {content[i]['url']}\n\n{summary}"
        for i, summary in enumerate(summaries)
    )


async def _summarise_article(raw_content: str, url: str) -> str:
    """
    Call Gemini to condense a single article down to its key points.
    Falls back through GEMINI_MODELS on quota errors.
    """
    client = genai.Client(api_key=config.GEMINI_API_KEY)
    prompt = build_summary_prompt(raw_content[:40_000], url)  # hard cap per article

    for i, model_name in enumerate(GEMINI_MODELS):
        try:
            response = await client.aio.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            return response.text.strip()
        except ClientError as exc:
            if exc.code == 429 and i < len(GEMINI_MODELS) - 1:
                print(f"[script] Quota hit on {model_name} during summarisation, "
                      f"trying {GEMINI_MODELS[i + 1]}...")
                await asyncio.sleep(RETRY_WAIT_SECONDS)
            else:
                raise
    raise RuntimeError("Exhausted all Gemini model fallbacks during summarisation.")


async def _call_gemini_with_fallback(
    topic: str,
    research_text: str,
    target_words: int,
) -> str:
    """
    Attempt to generate the script, falling back through GEMINI_MODELS on quota errors.
    Waits RETRY_WAIT_SECONDS before each retry attempt.
    """
    user_prompt = build_user_prompt(topic, research_text, target_words)
    system_prompt = build_system_prompt()

    for i, model_name in enumerate(GEMINI_MODELS):
        try:
            print(f"[script] Calling Gemini ({model_name})...")
            return await _call_gemini(model_name, system_prompt, user_prompt)

        except ClientError as exc:
            if exc.code == 429 and i < len(GEMINI_MODELS) - 1:
                next_model = GEMINI_MODELS[i + 1]
                print(f"[script] Quota exceeded on {model_name}. "
                      f"Waiting {RETRY_WAIT_SECONDS}s then trying {next_model}...")
                await asyncio.sleep(RETRY_WAIT_SECONDS)
            else:
                raise RuntimeError(
                    "All Gemini models hit quota limits. "
                    "Please check your API key billing or wait and retry."
                ) from exc

    raise RuntimeError("Exhausted all Gemini model fallbacks.")


async def _call_gemini(model_name: str, system_prompt: str, user_prompt: str) -> str:
    """
    Send the script-writing prompt to a specific Gemini model.
    JSON output mode is enabled so Gemini constrains its response to valid JSON.
    """
    client = genai.Client(api_key=config.GEMINI_API_KEY)

    response = await client.aio.models.generate_content(
        model=model_name,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            response_mime_type="application/json",
            temperature=0.9,
            top_p=0.95,
            max_output_tokens=32768,
        ),
    )
    return response.text


def _repair_truncated_json(text: str) -> list | None:
    """
    Attempt to recover a truncated JSON array by closing it after the last
    complete object. Returns the parsed list, or None if it cannot be repaired.
    """
    # Find the last occurrence of `}` which would close a complete turn object
    last_close = text.rfind("}")
    if last_close == -1:
        return None
    candidate = text[: last_close + 1].rstrip().rstrip(",") + "\n]"
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        return None


def _parse_script(raw: str) -> list[dict[str, str]]:
    """
    Parse the JSON response from Gemini into a validated list of turn dicts.

    Handles common edge cases:
      - JSON wrapped in a markdown code fence
      - Trailing commas (non-standard JSON from some model versions)
      - Extra top-level keys wrapping the array
    """
    text = raw.strip()

    # Strip markdown code fences if present
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        # The model may have been cut off mid-response — try to salvage complete turns.
        # Find the last complete turn object (ends with `}`) before the truncation point.
        repaired = _repair_truncated_json(text)
        if repaired is not None:
            print("[script] Warning: response was truncated — salvaged partial script.")
            data = repaired
        else:
            raise ValueError(
                f"Gemini returned invalid JSON. Parse error: {exc}\n"
                f"Raw response (first 500 chars):\n{raw[:500]}"
            ) from exc

    # Unwrap if Gemini returned {"script": [...]} instead of a bare array
    if isinstance(data, dict):
        for key in ("script", "turns", "dialogue", "podcast"):
            if isinstance(data.get(key), list):
                data = data[key]
                break

    if not isinstance(data, list):
        raise ValueError(f"Expected a JSON array of turns, got: {type(data)}")

    # Validate each turn and normalise host names
    valid_hosts = {config.HOST_A_NAME, config.HOST_B_NAME}
    validated = []
    for i, turn in enumerate(data):
        if not isinstance(turn, dict):
            raise ValueError(f"Turn {i} is not a dict: {turn}")
        if "host" not in turn or "line" not in turn:
            raise ValueError(f"Turn {i} missing 'host' or 'line' key: {turn}")
        if turn["host"] not in valid_hosts:
            raise ValueError(
                f"Turn {i} has unknown host '{turn['host']}'. "
                f"Expected one of: {valid_hosts}"
            )
        validated.append({"host": turn["host"], "line": turn["line"].strip()})

    return validated


def _count_words(script: list[dict]) -> int:
    """Return the total word count across all turns."""
    return sum(len(turn["line"].split()) for turn in script)


# ── CLI smoke-test ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    from research.scraper import search_and_scrape

    topic = " ".join(sys.argv[1:]) or "the rise of open source AI models"

    async def _main():
        config.validate()
        print(f"[test] Running full pipeline for: '{topic}'\n")

        research_data = await search_and_scrape(topic)
        script = await generate_script(research_data)

        print("\n" + "=" * 60)
        print("GENERATED SCRIPT")
        print("=" * 60)
        for turn in script:
            print(f"\n[{turn['host'].upper()}]")
            print(turn["line"])

        # Save raw JSON for inspection
        import os
        os.makedirs("temp", exist_ok=True)
        out_path = "temp/script_test.json"
        with open(out_path, "w") as f:
            json.dump(script, f, indent=2)
        print(f"\n[test] Script saved to {out_path}")

    asyncio.run(_main())
