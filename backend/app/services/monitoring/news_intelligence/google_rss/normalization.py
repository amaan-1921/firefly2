"""
Article normalization module for News Intelligence Agent

Normalizes RSS feed entries into a standard format for downstream processing.
"""

import re
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from html.parser import HTMLParser

try:
    from .schemas import NormalizedArticle
except ImportError:
    from schemas import NormalizedArticle

logger = logging.getLogger(__name__)


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
        logger.warning(f"Failed to strip HTML: {e}")
        # Fallback: regex-based removal
        return re.sub(r'<[^>]+>', '', html_text)


def clean_text(text: str) -> str:
    """
    Clean and normalize text.
    
    Args:
        text: Raw text
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text


def normalize_article(entry: Dict[str, Any]) -> NormalizedArticle:
    """
    Normalize an RSS feed entry into a standard article format.
    
    Args:
        entry: Raw RSS feed entry from feedparser
        
    Returns:
        NormalizedArticle object
    """
    
    # Extract title
    title = entry.get("title", "").strip()
    if not title:
        raise ValueError("Article missing title")
    
    # Extract summary/description, stripping HTML
    raw_summary = entry.get("summary", "") or entry.get("description", "")
    summary = strip_html(raw_summary)
    summary = clean_text(summary)
    
    # Extract URL
    url = entry.get("link", "").strip()
    if not url:
        raise ValueError("Article missing URL")
    
    # Extract publisher/author
    publisher = entry.get("author", "").strip()
    if not publisher:
        # Try to get from feed metadata
        if hasattr(entry, '_FeedParserMixin__parent'):
            parent = entry._FeedParserMixin__parent
            publisher = parent.feed.get("title", "Unknown Source").strip()
        else:
            publisher = "Unknown Source"
    
    # Extract published date
    published_date = None
    if "published" in entry:
        published_date = entry.get("published")
    elif "updated" in entry:
        published_date = entry.get("updated")
    
    # Create normalized article
    normalized = NormalizedArticle(
        title=clean_text(title),
        summary=summary,
        content=f"{title} {summary}",  # Combined content for analysis
        url=url,
        publisher=publisher,
        published_date=published_date,
        ingestion_timestamp=datetime.utcnow().isoformat()
    )
    
    return normalized
