"""
Metadata extraction from scraped content.

Extracts structured metadata (title, publisher, date, etc.) from scraped articles.
"""

import logging
from datetime import datetime
from typing import Optional, Dict
from urllib.parse import urlparse

import dateparser

try:
    from . import config
except ImportError:
    import config

logger = logging.getLogger(__name__)


class MetadataExtractor:
    """Extracts metadata from scraped content."""
    
    def extract(
        self,
        url: str,
        scraped_content: Dict[str, str],
    ) -> Dict[str, Optional[str]]:
        """
        Extract metadata from scraped content.
        
        Args:
            url: Source URL
            scraped_content: Dictionary with 'title', 'content', 'html' keys
            
        Returns:
            Dictionary with extracted metadata
        """
        from bs4 import BeautifulSoup
        
        html = scraped_content.get("html", "")
        title = scraped_content.get("title", "")
        content = scraped_content.get("content", "")
        
        # Parse HTML if available
        soup = None
        if html:
            try:
                soup = BeautifulSoup(html, "lxml")
            except Exception:
                pass
        
        # Extract source domain
        parsed_url = urlparse(url)
        source = parsed_url.netloc or url
        
        # Extract publisher/author
        publisher = self._extract_publisher(soup, html) if soup else None
        
        # Extract published date
        published_date = self._extract_published_date(soup, html) if soup else None
        
        # Use scraped_at as fallback for published_date
        scraped_at = datetime.utcnow().isoformat()
        if not published_date:
            published_date = scraped_at
        
        return {
            "title": title or "Untitled",
            "url": url,
            "source": source,
            "publisher": publisher,
            "published_date": published_date,
            "content": content,
            "scraped_at": scraped_at,
        }
    
    def _extract_publisher(self, soup, html: str) -> Optional[str]:
        """Extract publisher/author name."""
        if not soup:
            return None
        
        # Try various meta tags
        meta_selectors = [
            'meta[property="article:author"]',
            'meta[name="author"]',
            'meta[property="og:site_name"]',
            '.author',
            '.byline',
            '.publisher',
        ]
        
        for selector in meta_selectors:
            element = soup.select_one(selector)
            if element:
                value = element.get("content") or element.get_text(strip=True)
                if value:
                    return value
        
        # Try to find author in content
        author_elements = soup.find_all(class_=lambda x: x and "author" in x.lower())
        for element in author_elements:
            text = element.get_text(strip=True)
            if text and len(text) < 100:  # Reasonable author name length
                return text
        
        return None
    
    def _extract_published_date(self, soup, html: str) -> Optional[str]:
        """Extract published date."""
        if not soup:
            return None
        
        # Try various date meta tags
        date_selectors = [
            'meta[property="article:published_time"]',
            'meta[name="publish-date"]',
            'meta[name="date"]',
            'time[datetime]',
            'time[pubdate]',
        ]
        
        for selector in date_selectors:
            element = soup.select_one(selector)
            if element:
                date_str = element.get("content") or element.get("datetime") or element.get_text(strip=True)
                if date_str:
                    parsed_date = dateparser.parse(date_str)
                    if parsed_date:
                        return parsed_date.isoformat()
        
        # Try to find date in content (common patterns)
        import re
        date_patterns = [
            r'\b\d{4}-\d{2}-\d{2}\b',  # YYYY-MM-DD
            r'\b\d{2}/\d{2}/\d{4}\b',  # MM/DD/YYYY
            r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b',  # Month DD, YYYY
        ]
        
        text = html or ""
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                parsed_date = dateparser.parse(matches[0])
                if parsed_date:
                    return parsed_date.isoformat()
        
        return None


def extract_metadata(url: str, scraped_content: Dict[str, str]) -> Dict[str, Optional[str]]:
    """
    Convenience function to extract metadata.
    
    Args:
        url: Source URL
        scraped_content: Dictionary with scraped content
        
    Returns:
        Dictionary with extracted metadata
    """
    extractor = MetadataExtractor()
    return extractor.extract(url, scraped_content)
