"""
research/scraper.py — extract full article text from URLs using Tavily Extract API.

Takes the URLs returned by searcher.py and fetches their cleaned text content,
which is then passed to the script module for summarisation.
"""

import asyncio
from typing import Any

from tavily import AsyncTavilyClient

import config


# Maximum number of URLs to scrape (keeps Tavily costs and Gemini quota low)
MAX_URLS = 3

# Hard cap on characters kept per scraped page before passing to the LLM.
# Groq free tier TPM limit is 12k tokens; 3k chars/page keeps the total request
# well within budget (~3 pages × 3k chars ≈ 2.25k tokens of content).
MAX_CHARS_PER_PAGE = 3_000

# Minimum character length to consider a scraped result useful
MIN_CONTENT_LENGTH = 200


async def scrape_urls(urls: list[str]) -> list[dict[str, Any]]:
    """
    Extract clean text content from a list of URLs via Tavily Extract.

    Args:
        urls: List of URLs to scrape (typically from search results).

    Returns:
        List of dicts with keys:
          - url     : source URL
          - content : extracted plain-text body
        Only includes results that meet the minimum content length threshold.
    """
    if not urls:
        return []

    # Limit to avoid unnecessary API usage
    urls_to_scrape = urls[:MAX_URLS]

    client = AsyncTavilyClient(api_key=config.TAVILY_API_KEY)

    print(f"[research] Scraping {len(urls_to_scrape)} URLs...")

    response = await client.extract(urls=urls_to_scrape)

    extracted = []

    for result in response.get("results", []):
        content = result.get("raw_content", "").strip()

        if len(content) < MIN_CONTENT_LENGTH:
            print(f"[research] Skipping {result.get('url', '')} — content too short.")
            continue

        extracted.append(
            {
                "url":     result.get("url", ""),
                "content": content[:MAX_CHARS_PER_PAGE],
            }
        )

    # Log any URLs Tavily failed to extract
    for failed in response.get("failed_results", []):
        print(f"[research] Failed to extract: {failed.get('url', '')} — {failed.get('error', '')}")

    print(f"[research] Successfully scraped {len(extracted)} pages.")
    return extracted


async def search_and_scrape(topic: str) -> dict[str, Any]:
    """
    Convenience function: search for a topic then scrape the top results.

    Returns a dict with:
      - topic    : original query
      - sources  : list of {url, title, snippet, score} from search
      - content  : list of {url, content} from scraping
    """
    # Import here to avoid circular imports at module load
    from research.searcher import search_topic

    search_results = await search_topic(topic)

    # Extract URLs from search results for scraping
    urls = [r["url"] for r in search_results if r["url"]]

    scraped = await scrape_urls(urls)

    return {
        "topic":   topic,
        "sources": search_results,
        "content": scraped,
    }


# ── CLI smoke-test ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import json
    import sys

    topic = " ".join(sys.argv[1:]) or "artificial intelligence trends 2025"
    result = asyncio.run(search_and_scrape(topic))

    # Print a summary rather than the full content dump
    print(f"\nTopic   : {result['topic']}")
    print(f"Sources : {len(result['sources'])}")
    print(f"Scraped : {len(result['content'])} pages")
    for page in result["content"]:
        print(f"  • {page['url']} ({len(page['content'])} chars)")
