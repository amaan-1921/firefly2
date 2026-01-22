#!/usr/bin/env python3
"""
RSS Feed Aggregator

Fetches news articles from multiple free RSS feeds concurrently,
filters them by publication date within a configurable time window,
and outputs structured results in JSONL format.
"""

import argparse
import json
import logging
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from html.parser import HTMLParser
from typing import Dict, List, Optional, Any
import feedparser

# Import configuration
try:
    from . import config
except ImportError:
    # Fallback for direct script execution
    import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Default RSS feed URLs (free sources)
DEFAULT_RSS_FEEDS = [
    "https://feeds.bbci.co.uk/news/rss.xml",  # BBC News
    "https://feeds.reuters.com/reuters/topNews",  # Reuters Top News
    "http://rss.cnn.com/rss/edition.rss",  # CNN
    "https://feeds.npr.org/1001/rss.xml",  # NPR News
    "https://feeds.apnews.com/rss/topnews",  # Associated Press
    "https://news.google.com/rss?gl=US&ceid=US:en&topic=b",  # Google News Business
]

# Default time window (days) if not present in config.py
DEFAULT_TIME_WINDOW = 3


class HTMLStripper(HTMLParser):
    """Simple HTML tag stripper"""
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = []

    def handle_data(self, d):
        self.text.append(d)

    def get_data(self):
        return ''.join(self.text)


def strip_html(html_text: str) -> str:
    """
    Remove HTML tags from text while preserving content.
    
    Args:
        html_text: Text potentially containing HTML
        
    Returns:
        Cleaned text without HTML tags
    """
    if not html_text:
        return ""
    
    try:
        stripper = HTMLStripper()
        stripper.feed(html_text)
        return stripper.get_data()
    except Exception as e:
        logger.debug(f"Failed to strip HTML: {e}")
        # Fallback: regex-based removal
        return re.sub(r'<[^>]+>', '', html_text)


def parse_date(entry: Dict[str, Any]) -> Optional[datetime]:
    """
    Parse a date from RSS feed entry into datetime object.
    
    Uses feedparser's parsed date tuple if available, otherwise
    tries to parse the date string directly.
    
    Args:
        entry: RSS feed entry dictionary
        
    Returns:
        datetime object or None if parsing fails
    """
    # First try: use feedparser's parsed date tuple (most reliable)
    if hasattr(entry, 'published_parsed') and entry.published_parsed:
        try:
            return datetime(*entry.published_parsed[:6])
        except Exception:
            pass
    
    if hasattr(entry, 'updated_parsed') and entry.updated_parsed:
        try:
            return datetime(*entry.updated_parsed[:6])
        except Exception:
            pass
    
    # Second try: parse date string
    date_str = entry.get("published") or entry.get("updated")
    if not date_str:
        return None
    
    # Try common date formats
    date_formats = [
        "%a, %d %b %Y %H:%M:%S %z",  # RFC 822
        "%a, %d %b %Y %H:%M:%S %Z",  # RFC 822 with timezone name
        "%Y-%m-%dT%H:%M:%S%z",  # ISO 8601
        "%Y-%m-%dT%H:%M:%SZ",  # ISO 8601 UTC
        "%Y-%m-%d %H:%M:%S",  # Simple format
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    logger.debug(f"Could not parse date: {date_str}")
    return None


def fetch_rss_feed(feed_url: str) -> List[Dict[str, Any]]:
    """
    Fetch and parse a single RSS feed.
    
    Args:
        feed_url: URL of the RSS feed
        
    Returns:
        List of article dictionaries with metadata
    """
    articles = []
    
    try:
        logger.info(f"Fetching feed: {feed_url}")
        
        # Parse feed with User-Agent header
        feed = feedparser.parse(
            feed_url,
            request_headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        
        # Check for parsing errors
        if feed.bozo and isinstance(feed.bozo_exception, Exception):
            logger.warning(f"Feed parsing warning for {feed_url}: {feed.bozo_exception}")
        
        # Get feed title
        feed_title = feed.feed.get("title", "Unknown Source")
        
        # Process each entry
        for entry in feed.entries:
            try:
                # Extract article metadata
                title = entry.get("title", "").strip()
                if not title:
                    continue
                
                url = entry.get("link", "").strip()
                if not url:
                    continue
                
                # Extract summary/description
                summary = entry.get("summary", "") or entry.get("description", "")
                # Strip HTML tags
                if summary:
                    summary = strip_html(summary)
                    summary = summary.strip()
                
                # Extract published date
                parsed_date = parse_date(entry)
                published_date = None
                if parsed_date:
                    published_date = parsed_date.isoformat()
                
                article = {
                    "title": title,
                    "url": url,
                    "published_date": published_date,
                    "summary": summary,
                    "source_feed": feed_title,
                    "feed_url": feed_url
                }
                
                articles.append(article)
                
            except Exception as e:
                logger.debug(f"Error processing entry from {feed_url}: {e}")
                continue
        
        logger.info(f"Successfully fetched {len(articles)} articles from {feed_url}")
        # Debug print for number of articles fetched per RSS feed
        print(f"[DEBUG] {len(articles)} articles fetched from {feed_url}")
        
    except Exception as e:
        logger.error(f"Failed to fetch feed {feed_url}: {str(e)}")
    
    return articles


def fetch_all_feeds_concurrently(feed_urls: List[str], max_workers: int = 5) -> List[Dict[str, Any]]:
    """
    Fetch multiple RSS feeds concurrently.
    
    Args:
        feed_urls: List of RSS feed URLs
        max_workers: Maximum number of concurrent workers
        
    Returns:
        List of all articles from all feeds
    """
    all_articles = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all feed fetching tasks
        future_to_url = {
            executor.submit(fetch_rss_feed, url): url 
            for url in feed_urls
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                articles = future.result()
                all_articles.extend(articles)
            except Exception as e:
                logger.error(f"Exception occurred while fetching {url}: {e}")
    
    return all_articles


def filter_articles_by_time_window(
    articles: List[Dict[str, Any]], 
    timewindow_days: int
) -> List[Dict[str, Any]]:
    """
    Filter articles to only include those published within the time window.
    
    Args:
        articles: List of article dictionaries
        timewindow_days: Number of days to look back from current time
        
    Returns:
        Filtered list of articles within the time window
    """
    if timewindow_days <= 0:
        logger.warning("Time window is 0 or negative, returning all articles")
        return articles
    
    current_time = datetime.utcnow()
    cutoff_time = current_time - timedelta(days=timewindow_days)
    
    logger.info(f"Filtering articles published after {cutoff_time.isoformat()}")
    
    filtered_articles = []
    articles_without_date = []
    
    for article in articles:
        published_date_str = article.get("published_date")
        
        if not published_date_str:
            # Keep articles without dates (they might be recent)
            articles_without_date.append(article)
            continue
        
        try:
            # Parse the ISO format date
            published_date = datetime.fromisoformat(published_date_str.replace('Z', '+00:00'))
            
            # Convert to UTC if timezone-aware, otherwise assume UTC
            if published_date.tzinfo is None:
                published_date = published_date.replace(tzinfo=None)
            else:
                published_date = published_date.astimezone().replace(tzinfo=None)
            
            # Compare with cutoff time
            if published_date >= cutoff_time:
                filtered_articles.append(article)
            else:
                logger.debug(f"Article '{article['title'][:50]}...' published {published_date.isoformat()} is outside time window")
                
        except Exception as e:
            logger.warning(f"Error parsing date for article '{article['title'][:50]}...': {e}")
            # Include articles with unparseable dates
            articles_without_date.append(article)
    
    # Include articles without dates (assume they might be recent)
    filtered_articles.extend(articles_without_date)
    
    logger.info(f"Filtered to {len(filtered_articles)} articles within {timewindow_days} day(s) window")
    
    return filtered_articles


def write_jsonl(articles: List[Dict[str, Any]], output_file: str):
    """
    Write articles to a JSONL file (one JSON object per line).
    
    Args:
        articles: List of article dictionaries
        output_file: Path to output file
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for article in articles:
                json_line = json.dumps(article, ensure_ascii=False)
                f.write(json_line + '\n')
        
        logger.info(f"Successfully wrote {len(articles)} articles to {output_file}")
        
    except Exception as e:
        logger.error(f"Error writing to {output_file}: {e}")
        raise


def main():
    """Main entry point for the RSS aggregator script."""
    parser = argparse.ArgumentParser(
        description="Fetch and aggregate articles from multiple RSS feeds"
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        default=getattr(config, "INPUT_FILE", "rss_articles.jsonl"),
        help='Output file path (default: rss_articles.jsonl)'
    )
    
    parser.add_argument(
        '--feeds',
        type=str,
        nargs='+',
        default=None,
        help='Custom RSS feed URLs (space-separated). If not provided, uses default feeds.'
    )
    
    parser.add_argument(
        '--max-workers',
        type=int,
        default=5,
        help='Maximum number of concurrent workers (default: 5)'
    )
    
    args = parser.parse_args()
    
    # Determine which feeds to use
    feed_urls = args.feeds if args.feeds else DEFAULT_RSS_FEEDS
    timewindow_days = int(getattr(config, "TIME_WINDOW_DAYS", DEFAULT_TIME_WINDOW))
    
    logger.info(f"Starting RSS aggregator")
    logger.info(f"Time window: {timewindow_days} day(s)")
    logger.info(f"Number of feeds: {len(feed_urls)}")
    logger.info(f"Output file: {args.output}")
    
    # Fetch all feeds concurrently
    all_articles = fetch_all_feeds_concurrently(feed_urls, max_workers=args.max_workers)
    
    logger.info(f"Fetched {len(all_articles)} total articles from all feeds")
    
    # Filter by time window
    filtered_articles = filter_articles_by_time_window(all_articles, timewindow_days)
    
    # Write to JSONL file
    write_jsonl(filtered_articles, args.output)
    
    # Debug print for total number of articles written to JSONL
    print(f"[DEBUG] {len(filtered_articles)} articles written to {args.output}")
    logger.info(f"Completed! Output written to {args.output}")


if __name__ == "__main__":
    main()
