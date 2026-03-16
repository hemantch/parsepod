"""
research/searcher.py — search the web for a topic using Tavily Search API.

Returns a list of result dicts, each containing:
  - title  : page title
  - url    : source URL
  - snippet: short excerpt from Tavily
  - score  : relevance score (0–1)
"""

import asyncio
from typing import Any

from tavily import AsyncTavilyClient

import config


# Number of search results to fetch per query
SEARCH_DEPTH  = "advanced"   # "basic" | "advanced"
MAX_RESULTS   = 8            # Tavily max per request is 10
INCLUDE_ANSWER = False       # We want raw results, not a synthesised answer


async def search_topic(topic: str) -> list[dict[str, Any]]:
    """
    Search the web for `topic` and return ranked results.

    Args:
        topic: The podcast subject, e.g. "quantum computing breakthroughs 2024"

    Returns:
        A list of result dicts sorted by relevance score (highest first).
    """
    client = AsyncTavilyClient(api_key=config.TAVILY_API_KEY)

    print(f"[research] Searching for: '{topic}'")

    response = await client.search(
        query=topic,
        search_depth=SEARCH_DEPTH,
        max_results=MAX_RESULTS,
        include_answer=INCLUDE_ANSWER,
        include_raw_content=False,   # raw HTML; we scrape separately
    )

    results = response.get("results", [])

    # Normalise into a consistent schema
    cleaned = [
        {
            "title":   r.get("title", ""),
            "url":     r.get("url", ""),
            "snippet": r.get("content", ""),
            "score":   r.get("score", 0.0),
        }
        for r in results
    ]

    # Sort highest relevance first
    cleaned.sort(key=lambda r: r["score"], reverse=True)

    print(f"[research] Found {len(cleaned)} results.")
    return cleaned


# ── CLI smoke-test ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import json
    import sys

    topic = " ".join(sys.argv[1:]) or "artificial intelligence trends 2025"
    results = asyncio.run(search_topic(topic))
    print(json.dumps(results, indent=2))
