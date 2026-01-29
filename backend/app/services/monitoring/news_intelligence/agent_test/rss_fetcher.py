"""
RSS feed fetcher for news aggregation.

Fetches article URLs from RSS feeds without rate-limiting or anti-bot measures.
Much more reliable than Google search for news collection.
"""

import logging
from typing import List, Dict, Optional

import feedparser
import requests

logger = logging.getLogger(__name__)


class RSSFetcher:
    """Fetches article URLs from RSS feeds."""
    
    def __init__(self, timeout_s: float = 10.0):
        self.timeout_s = timeout_s
        self.request_headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }

    def _parse_feed(self, feed_url: str):
        return feedparser.parse(
            feed_url,
            request_headers=self.request_headers,
        )

    def _parse_feed_content(self, content: bytes):
        return feedparser.parse(content)

    def _fetch_feed_content(self, feed_url: str) -> Optional[bytes]:
        try:
            response = requests.get(
                feed_url,
                headers=self.request_headers,
                timeout=self.timeout_s,
            )
            response.raise_for_status()
            return response.content
        except Exception as exc:
            logger.warning(f"HTTP fetch error for {feed_url}: {exc}")
            return None
    
    def fetch_feed(self, feed_url: str, max_entries: int = 50) -> List[Dict[str, str]]:
        """
        Fetch articles from an RSS feed.
        
        Args:
            feed_url: URL of the RSS feed
            max_entries: Maximum number of entries to fetch
            
        Returns:
            List of dicts with 'url', 'title', 'published' keys
        """
        articles = []
        
        try:
            logger.info(f"Fetching RSS feed: {feed_url}")
            feed = self._parse_feed(feed_url)
            
            if feed.bozo:
                logger.warning(f"Feed parsing warning for {feed_url}: {feed.bozo_exception}")

            if not feed.entries:
                content = self._fetch_feed_content(feed_url)
                if content:
                    feed = self._parse_feed_content(content)
                    if feed.bozo:
                        logger.warning(
                            f"Feed parsing warning after content fetch for {feed_url}: "
                            f"{feed.bozo_exception}"
                        )
            
            entries_count = min(len(feed.entries), max_entries)
            
            for entry in feed.entries[:entries_count]:
                try:
                    # Try to get URL from various possible fields
                    url = None
                    if hasattr(entry, 'link'):
                        url = entry.link
                    elif hasattr(entry, 'id'):
                        url = entry.id
                    
                    if not url:
                        continue
                    
                    title = getattr(entry, 'title', 'Untitled')
                    published = getattr(entry, 'published', '')
                    
                    articles.append({
                        'url': url,
                        'title': title,
                        'published': published,
                    })
                except Exception as e:
                    logger.warning(f"Error parsing entry from {feed_url}: {e}")
                    continue
            
            logger.info(f"Fetched {len(articles)} articles from {feed_url}")
        except Exception as e:
            logger.error(f"Error fetching RSS feed {feed_url}: {e}")
        
        return articles


# Common RSS feed URLs for supply chain news sources
SUPPLY_CHAIN_RSS_FEEDS = {
    "Supply Chain Dive": [
        "https://www.supplychaindive.com/feeds/news",
    ],
    "Journal of Commerce": [
        "https://www.joc.com/rss",
        "https://www.joc.com/feeds/all",
    ],
    "Logistics Management": [
        "https://www.logisticsmgmt.com/feeds/rss",
        "https://www.logisticsmgmt.com/feeds",
    ],
    "DC Velocity": [
        "https://www.dcvelocity.com/feeds/rss",
        "https://www.dcvelocity.com/rss",
    ],
    "FreightWaves": [
        "https://www.freightwaves.com/feed",
        "https://www.freightwaves.com/feeds",
    ],
    "Supply Chain Brain": [
        "https://www.supplychainbrain.com/rss",
        "https://www.supplychainbrain.com/feeds",
    ],
}


def fetch_from_rss_feeds(max_articles_per_feed: int = 50) -> List[str]:
    """
    Fetch article URLs from multiple RSS feeds.
    
    Args:
        max_articles_per_feed: Max articles per feed
        
    Returns:
        List of unique article URLs
    """
    fetcher = RSSFetcher()
    all_urls = set()
    
    for source_name, feed_urls in SUPPLY_CHAIN_RSS_FEEDS.items():
        if isinstance(feed_urls, str):
            feed_urls = [feed_urls]

        source_articles: List[Dict[str, str]] = []
        for feed_url in feed_urls:
            articles = fetcher.fetch_feed(feed_url, max_entries=max_articles_per_feed)
            if articles:
                source_articles = articles
                break

        if not source_articles:
            logger.warning(f"No articles fetched from {source_name} feeds")
            continue

        for article in source_articles:
            all_urls.add(article['url'])
    
    logger.info(f"Fetched {len(all_urls)} unique URLs from RSS feeds")
    return list(all_urls)
