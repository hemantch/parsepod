"""research — web search and content scraping via Tavily."""

from .searcher import search_topic
from .scraper import scrape_urls

__all__ = ["search_topic", "scrape_urls"]
