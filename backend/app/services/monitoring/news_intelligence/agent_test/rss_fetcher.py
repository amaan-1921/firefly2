"""
RSS feed fetcher for news aggregation.

Fetches article URLs from RSS feeds without rate-limiting or anti-bot measures.
Much more reliable than Google search for news collection.
"""

import logging
from typing import List, Dict, Optional
from urllib.parse import urlparse
import feedparser

logger = logging.getLogger(__name__)


class RSSFetcher:
    """Fetches article URLs from RSS feeds."""
    
    def __init__(self, timeout_s: float = 10.0):
        self.timeout_s = timeout_s
    
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
            feed = feedparser.parse(feed_url)
            
            if feed.bozo:
                logger.warning(f"Feed parsing error for {feed_url}: {feed.bozo_exception}")
            
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
    "Supply Chain Dive": "https://www.supplychaindive.com/feeds/news",
    "Journal of Commerce": "https://www.joc.com/feeds/all",
    "Logistics Management": "https://www.logisticsmgmt.com/feeds",
    "DC Velocity": "https://www.dcvelocity.com/feeds/rss",
    "FreightWaves": "https://www.freightwaves.com/feeds",
    "Supply Chain Brain": "https://www.supplychainbrain.com/feeds",
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
    
    for source_name, feed_url in SUPPLY_CHAIN_RSS_FEEDS.items():
        articles = fetcher.fetch_feed(feed_url, max_entries=max_articles_per_feed)
        for article in articles:
            all_urls.add(article['url'])
    
    logger.info(f"Fetched {len(all_urls)} unique URLs from RSS feeds")
    return list(all_urls)
