"""
script/writer.py — generate a two-host podcast script using the Gemini API.

Model: gemini-2.5-flash (stable, structured JSON output via response_mime_type)

Flow:
  1. Combine scraped research into a single context block.
  2. Send system + user prompts to Gemini with JSON mode enabled.
  3. Parse, validate, and return the script as a list of turn dicts.
"""

import json
import re
from typing import Any

from google import genai
from google.genai import types

import config
from script.prompts import build_system_prompt, build_user_prompt


# ── Model config ───────────────────────────────────────────────────────────────

GEMINI_MODEL     = "gemini-2.5-flash"
WORDS_PER_MINUTE = 150   # used to calculate target script length


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
        List of turn dicts: [{"host": "Thomas"|"Libby", "line": "..."}, ...]
    """
    topic   = research_data["topic"]
    content = research_data.get("content", [])
    sources = research_data.get("sources", [])

    if not content and not sources:
        raise ValueError("No research content provided — run the research module first.")

    # ── Step 1: Build research context ────────────────────────────────────────
    print("[script] Preparing research context...")
    research_text = _build_research_context(content, sources)

    # ── Step 2: Calculate target word count ───────────────────────────────────
    target_words = config.EPISODE_DURATION_MINUTES * WORDS_PER_MINUTE
    print(f"[script] Target: ~{target_words} words ({config.EPISODE_DURATION_MINUTES} min episode)")

    # ── Step 3: Call Gemini ────────────────────────────────────────────────────
    print(f"[script] Calling Gemini ({GEMINI_MODEL})...")
    raw_script = _call_gemini(topic, research_text, target_words)

    # ── Step 4: Parse and validate ────────────────────────────────────────────
    print("[script] Parsing script...")
    script = _parse_script(raw_script)

    print(f"[script] Script generated: {len(script)} turns, ~{_count_words(script)} words.")
    return script


# ── Internal helpers ───────────────────────────────────────────────────────────

def _build_research_context(content: list[dict], sources: list[dict]) -> str:
    """Combine scraped pages into one text block for the prompt."""
    if not content:
        print("[script] No full article content — using search snippets.")
        return "\n\n".join(
            f"Source: {s['url']}\n{s['snippet']}"
            for s in sources
        )

    return "\n\n---\n\n".join(
        f"Source: {page['url']}\n\n{page['content']}"
        for page in content
    )


def _call_gemini(topic: str, research_text: str, target_words: int) -> str:
    """
    Send the script-writing prompt to Gemini and return the raw response text.
    response_mime_type constrains the model to return valid JSON.
    """
    client = genai.Client(api_key=config.GEMINI_API_KEY)

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=build_user_prompt(topic, research_text, target_words),
        config=types.GenerateContentConfig(
            system_instruction=build_system_prompt(),
            response_mime_type="application/json",
            temperature=0.9,
            max_output_tokens=8192,
        ),
    )
    return response.text


def _repair_truncated_json(text: str) -> list | None:
    """
    Attempt to recover a truncated JSON array by closing it after the last
    complete object. Returns the parsed list, or None if unrecoverable.
    """
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
    Parse the JSON response into a validated list of turn dicts.

    Handles:
      - Markdown code fences wrapping the JSON
      - Top-level dict wrapping the array (e.g. {"script": [...]})
      - Truncated responses (salvages all complete turns)
    """
    text = raw.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        repaired = _repair_truncated_json(text)
        if repaired is not None:
            print("[script] Warning: response truncated — salvaged partial script.")
            data = repaired
        else:
            raise ValueError(
                f"Gemini returned invalid JSON. Parse error: {exc}\n"
                f"Raw response (first 500 chars):\n{raw[:500]}"
            ) from exc

    # Unwrap {"script": [...]} if the model wraps the array
    if isinstance(data, dict):
        for key in ("script", "turns", "dialogue", "podcast"):
            if isinstance(data.get(key), list):
                data = data[key]
                break

    if not isinstance(data, list):
        raise ValueError(f"Expected a JSON array of turns, got: {type(data)}")

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
    return sum(len(turn["line"].split()) for turn in script)


# ── CLI smoke-test ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import asyncio, json, os, sys
    from research.scraper import search_and_scrape

    topic = " ".join(sys.argv[1:]) or "the rise of open source AI models"

    async def _main():
        config.validate()
        print(f"[test] Topic: '{topic}'\n")
        research_data = await search_and_scrape(topic)
        script = await generate_script(research_data)

        print("\n" + "=" * 60)
        print("GENERATED SCRIPT")
        print("=" * 60)
        for turn in script:
            print(f"\n[{turn['host'].upper()}]\n{turn['line']}")

        os.makedirs("temp", exist_ok=True)
        out = "temp/script_test.json"
        json.dump(script, open(out, "w"), indent=2)
        print(f"\n[test] Script saved to {out}")

    asyncio.run(_main())
