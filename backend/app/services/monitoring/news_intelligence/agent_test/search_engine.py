"""
Search engine integration for finding relevant URLs.

Supports Google Custom Search API and googlesearch-python library.
"""

import logging
import os
import time
from typing import List, Dict, Optional
from urllib.parse import urlparse

from dotenv import find_dotenv, load_dotenv

try:
    from . import config
except ImportError:
    import config

logger = logging.getLogger(__name__)


class SearchResult:
    """Represents a search result."""
    def __init__(self, title: str, url: str, snippet: Optional[str] = None):
        self.title = title
        self.url = url
        self.snippet = snippet
    
    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
        }


class SearchEngine:
    """Search engine interface."""
    
    def search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """
        Search for URLs matching the query.
        
        Args:
            query: Search query string
            num_results: Number of results to return
            
        Returns:
            List of SearchResult objects
        """
        raise NotImplementedError


class GoogleCustomSearchEngine(SearchEngine):
    """Google Custom Search API implementation."""
    
    def __init__(self, api_key: str, search_engine_id: str):
        self.api_key = api_key
        self.search_engine_id = search_engine_id
        self.base_url = "https://www.googleapis.com/customsearch/v1"
    
    def search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """Search using Google Custom Search API."""
        import requests
        
        results = []
        start_index = 1
        
        while len(results) < num_results:
            params = {
                "key": self.api_key,
                "cx": self.search_engine_id,
                "q": query,
                "num": min(10, num_results - len(results)),
                "start": start_index,
            }
            
            try:
                resp = requests.get(self.base_url, params=params, timeout=10)
                resp.raise_for_status()
                data = resp.json()
                
                items = data.get("items", [])
                for item in items:
                    results.append(SearchResult(
                        title=item.get("title", ""),
                        url=item.get("link", ""),
                        snippet=item.get("snippet"),
                    ))
                
                if len(items) < 10 or len(results) >= num_results:
                    break
                
                start_index += 10
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Google Custom Search API error: {e}")
                break
        
        return results[:num_results]


class GoogleSearchLibraryEngine(SearchEngine):
    """googlesearch-python library implementation (free, rate-limited)."""
    
    def __init__(self, delay_s: float = 2.0):
        self.delay_s = delay_s
    
    def search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """Search using googlesearch-python library."""
        try:
            from googlesearch import search
        except ImportError:
            logger.error("googlesearch-python not installed. Install with: pip install googlesearch-python")
            return []
        
        results = []
        
        try:
            for url in search(query, num_results=num_results, sleep_interval=self.delay_s):
                # Extract domain as title placeholder
                domain = urlparse(url).netloc
                results.append(SearchResult(
                    title=domain,
                    url=url,
                    snippet=None,
                ))
        except Exception as e:
            logger.error(f"Google search library error: {e}")
        
        return results


def create_search_engine() -> Optional[SearchEngine]:
    """
    Create appropriate search engine based on configuration.
    
    Returns:
        SearchEngine instance or None if no engine available
    """
    dotenv_path = find_dotenv()
    if dotenv_path:
        load_dotenv(dotenv_path)
    else:
        load_dotenv()
    
    # Try Google Custom Search API first
    api_key = os.getenv(config.GOOGLE_CSE_API_KEY_ENV)
    search_id = os.getenv(config.GOOGLE_CSE_ID_ENV)
    
    if api_key and search_id:
        logger.info("Using Google Custom Search API")
        return GoogleCustomSearchEngine(api_key, search_id)
    
    # Fallback to googlesearch-python library
    if config.USE_GOOGLE_SEARCH:
        logger.info("Using googlesearch-python library (free tier)")
        return GoogleSearchLibraryEngine(delay_s=config.GOOGLE_SEARCH_DELAY_S)
    
    logger.warning("No search engine configured")
    return None


def search_urls(queries: List[str], num_results_per_query: int = 10) -> List[str]:
    """
    Search for URLs using multiple queries.
    
    Args:
        queries: List of search queries
        num_results_per_query: Number of results per query
        
    Returns:
        List of unique URLs
    """
    engine = create_search_engine()
    if not engine:
        logger.warning("No search engine available, returning empty list")
        return []
    
    all_urls = set()
    
    for query in queries:
        logger.info(f"Searching: {query}")
        try:
            results = engine.search(query, num_results_per_query)
            for result in results:
                if result.url:
                    all_urls.add(result.url)
            time.sleep(config.GOOGLE_SEARCH_DELAY_S)  # Rate limiting
        except Exception as e:
            logger.error(f"Search failed for query '{query}': {e}")
            continue
    
    logger.info(f"Found {len(all_urls)} unique URLs")
    return list(all_urls)
