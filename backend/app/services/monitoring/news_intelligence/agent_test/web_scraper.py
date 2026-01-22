"""
Web scraping utilities using BeautifulSoup and requests.

Handles scraping article content from various website structures.
"""

import logging
import time
from typing import Optional, Dict
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

try:
    from . import config
except ImportError:
    import config

logger = logging.getLogger(__name__)


class ScrapingError(Exception):
    pass


class WebScraper:
    """Web scraper for extracting article content."""
    
    def __init__(
        self,
        timeout_s: float = 30.0,
        max_retries: int = 3,
        delay_between_requests_s: float = 1.0,
        user_agent: Optional[str] = None,
    ):
        self.timeout_s = timeout_s
        self.max_retries = max_retries
        self.delay_between_requests_s = delay_between_requests_s
        self.user_agent = user_agent or config.USER_AGENT
        self._last_request_time = 0.0
    
    def _rate_limit(self):
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.delay_between_requests_s:
            time.sleep(self.delay_between_requests_s - elapsed)
        self._last_request_time = time.time()
    
    def _fetch_html(self, url: str) -> Optional[str]:
        """Fetch HTML content from URL with retries."""
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Referer": "https://www.google.com/",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Cache-Control": "max-age=0",
        }
        
        for attempt in range(self.max_retries):
            try:
                self._rate_limit()
                resp = requests.get(url, headers=headers, timeout=self.timeout_s)
                resp.raise_for_status()
                return resp.text
            except requests.exceptions.RequestException as e:
                if attempt >= self.max_retries - 1:
                    logger.error(f"Failed to fetch {url} after {self.max_retries} attempts: {e}")
                    return None
                logger.warning(f"Retry {attempt + 1}/{self.max_retries} for {url}")
                time.sleep(2 ** attempt)  # Exponential backoff
        
        return None
    
    def scrape(self, url: str) -> Optional[Dict[str, str]]:
        """
        Scrape article content from URL.
        
        Args:
            url: URL to scrape
            
        Returns:
            Dictionary with 'title', 'content', 'html' keys, or None if failed
        """
        html = self._fetch_html(url)
        if not html:
            return None
        
        try:
            soup = BeautifulSoup(html, "lxml")
            
            # Extract title
            title = self._extract_title(soup)
            
            # Extract main content
            content = self._extract_content(soup)
            
            if not title and not content:
                logger.warning(f"No content extracted from {url}")
                return None
            
            return {
                "title": title or "",
                "content": content or "",
                "html": html,
            }
        except Exception as e:
            logger.error(f"Error parsing HTML from {url}: {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article title."""
        # Try various title selectors
        selectors = [
            "h1.article-title",
            "h1.post-title",
            "h1.entry-title",
            "article h1",
            "main h1",
            ".article-header h1",
            "title",
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get_text(strip=True)
                if title:
                    return title
        
        # Fallback to <title> tag
        title_tag = soup.find("title")
        if title_tag:
            return title_tag.get_text(strip=True)
        
        return None
    
    def _extract_content(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract main article content."""
        # Remove script and style elements
        for element in soup(["script", "style", "nav", "header", "footer", "aside"]):
            element.decompose()
        
        # Try various content selectors
        selectors = [
            "article",
            ".article-content",
            ".post-content",
            ".entry-content",
            "main",
            ".content",
            "[role='main']",
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                # Get text content
                text = element.get_text(separator=" ", strip=True)
                if len(text) > 100:  # Minimum content length
                    return text
        
        # Fallback: get all paragraphs
        paragraphs = soup.find_all("p")
        if paragraphs:
            text = " ".join(p.get_text(strip=True) for p in paragraphs)
            if len(text) > 100:
                return text
        
        return None


def scrape_url(url: str) -> Optional[Dict[str, str]]:
    """
    Convenience function to scrape a URL.
    
    Args:
        url: URL to scrape
        
    Returns:
        Dictionary with scraped content or None
    """
    scraper = WebScraper(
        timeout_s=config.SCRAPER_TIMEOUT_S,
        max_retries=config.SCRAPER_MAX_RETRIES,
        delay_between_requests_s=config.SCRAPER_DELAY_BETWEEN_REQUESTS_S,
    )
    return scraper.scrape(url)


def scrape_urls(urls: list[str]) -> Dict[str, Optional[Dict[str, str]]]:
    """
    Scrape multiple URLs.
    
    Args:
        urls: List of URLs to scrape
        
    Returns:
        Dictionary mapping URL to scraped content (or None if failed)
    """
    scraper = WebScraper(
        timeout_s=config.SCRAPER_TIMEOUT_S,
        max_retries=config.SCRAPER_MAX_RETRIES,
        delay_between_requests_s=config.SCRAPER_DELAY_BETWEEN_REQUESTS_S,
    )
    
    results = {}
    for url in urls:
        logger.info(f"Scraping: {url}")
        content = scraper.scrape(url)
        results[url] = content
        if content:
            logger.info(f"Successfully scraped {url}")
        else:
            logger.warning(f"Failed to scrape {url}")
    
    return results
