#!/usr/bin/env python3
"""
Main agent orchestrator for web scraping LLM agent.

Orchestrates the complete pipeline:
1. Generate search queries using LLM
2. Execute searches (search engine + predefined sources)
3. Scrape article content
4. Extract metadata
5. Score relevance using LLM
6. Filter by relevance threshold
7. Write to JSONL file
"""

import argparse
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
from urllib.parse import urlparse

try:
    from . import config
    from .query_generator import generate_search_queries
    from .search_engine import search_urls
    from .web_scraper import scrape_urls
    from .metadata_extractor import extract_metadata
    from .relevance_scorer import score_and_filter_articles
    from .output_handler import write_scraped_articles
    from .schemas import ScrapedArticle
    from .rss_fetcher import fetch_from_rss_feeds
except ImportError:
    import config
    from query_generator import generate_search_queries
    from search_engine import search_urls
    from web_scraper import scrape_urls
    from metadata_extractor import extract_metadata
    from relevance_scorer import score_and_filter_articles
    from output_handler import write_scraped_articles
    from schemas import ScrapedArticle
    from rss_fetcher import fetch_from_rss_feeds

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_urls_from_sources(sources: List[str]) -> List[str]:
    """
    Get URLs from predefined sources.
    
    For now, returns the source URLs themselves.
    In a full implementation, this could scrape RSS feeds or sitemaps.
    
    Args:
        sources: List of source URLs
        
    Returns:
        List of URLs to scrape
    """
    # For now, return sources directly
    # In future, could fetch RSS feeds or scrape sitemaps
    return sources


def filter_by_time_window(
    articles: List[Dict[str, Any]],
    timewindow_days: int,
) -> List[Dict[str, Any]]:
    """
    Filter articles by publication date within time window.
    
    Args:
        articles: List of article dictionaries
        timewindow_days: Number of days to look back
        
    Returns:
        Filtered list of articles
    """
    if timewindow_days <= 0:
        return articles
    
    cutoff_date = datetime.utcnow() - timedelta(days=timewindow_days)
    filtered = []
    
    for article in articles:
        published_date_str = article.get("published_date")
        if not published_date_str:
            # Include articles without dates
            filtered.append(article)
            continue
        
        try:
            from dateparser import parse as parse_date
            published_date = parse_date(published_date_str)
            if published_date and published_date.replace(tzinfo=None) >= cutoff_date.replace(tzinfo=None):
                filtered.append(article)
        except Exception:
            # Include articles with unparseable dates
            filtered.append(article)
    
    return filtered


def run_agent(
    num_queries: int = 5,
    num_results_per_query: int = 10,
    timewindow_days: int = None,
    threshold: float = None,
    output_file: str = None,
    overwrite: bool = False,
) -> int:
    """
    Run the web scraping agent.
    
    Args:
        num_queries: Number of search queries to generate
        num_results_per_query: Number of results per query
        timewindow_days: Days to look back (default from config)
        threshold: Relevance threshold (default from config)
        output_file: Output filename (default from config)
        overwrite: If True, overwrite output file; if False, append (default: False, i.e., append)
        
    Returns:
        0 on success, 1 on error
    """
    logger.info("=" * 60)
    logger.info("Starting Web Scraping LLM Agent")
    logger.info("=" * 60)
    
    # Use config defaults
    timewindow_days = timewindow_days or config.TIME_WINDOW_DAYS
    threshold = threshold or config.RELEVANCE_THRESHOLD
    
    try:
        # Step 1: Generate search queries
        logger.info("=" * 60)
        logger.info("STEP 1: Generating search queries")
        logger.info("=" * 60)
        queries = generate_search_queries(config.SEARCH_TOPICS, num_queries)
        logger.info(f"Generated {len(queries)} search queries")
        
        # Step 2: Search for URLs
        logger.info("=" * 60)
        logger.info("STEP 2: Fetching article URLs from RSS feeds and search")
        logger.info("=" * 60)
        
        # Primary source: RSS feeds (no rate-limiting, most reliable)
        rss_urls = fetch_from_rss_feeds(max_articles_per_feed=50)
        logger.info(f"Found {len(rss_urls)} URLs from RSS feeds")
        
        # Secondary source: Google search (if enabled)
        search_urls_list = []
        if config.USE_GOOGLE_SEARCH:
            search_urls_list = search_urls(queries, num_results_per_query)
            logger.info(f"Found {len(search_urls_list)} URLs from search engine")
        else:
            logger.info("Google search disabled (set USE_GOOGLE_SEARCH=True to enable)")
        
        # Combine all URLs
        all_urls = list(set(rss_urls + search_urls_list))
        logger.info(f"Found {len(all_urls)} unique URLs total to scrape")
        
        if not all_urls:
            logger.warning("No URLs found. Exiting.")
            return 0
        
        # Step 3: Scrape article content
        logger.info("=" * 60)
        logger.info("STEP 3: Scraping article content")
        logger.info("=" * 60)
        scraped_content = scrape_urls(all_urls)
        
        # Step 4: Extract metadata
        logger.info("=" * 60)
        logger.info("STEP 4: Extracting metadata")
        logger.info("=" * 60)
        articles = []
        for url, content in scraped_content.items():
            if content:
                metadata = extract_metadata(url, content)
                articles.append(metadata)
            else:
                logger.debug(f"Skipping {url} (failed to scrape)")
        
        logger.info(f"Extracted metadata from {len(articles)} articles")
        
        if not articles:
            logger.warning("No articles extracted. Exiting.")
            return 0
        
        # Step 5: Filter by time window
        logger.info("=" * 60)
        logger.info("STEP 5: Filtering by time window")
        logger.info("=" * 60)
        articles = filter_by_time_window(articles, timewindow_days)
        logger.info(f"Filtered to {len(articles)} articles within {timewindow_days} day(s)")
        
        # Step 6: Score relevance and filter
        logger.info("=" * 60)
        logger.info("STEP 6: Scoring relevance and filtering")
        logger.info("=" * 60)
        logger.info(f"Relevance threshold: {threshold}")
        scored_articles = score_and_filter_articles(articles, threshold)
        logger.info(f"Filtered to {len(scored_articles)} relevant articles")
        
        # Step 7: Write to JSONL
        logger.info("=" * 60)
        logger.info("STEP 7: Writing output")
        logger.info("=" * 60)
        append = not overwrite
        output_path = write_scraped_articles(scored_articles, output_file, append=append)
        
        logger.info("=" * 60)
        logger.info("Agent completed successfully!")
        logger.info(f"Output: {output_path}")
        logger.info(f"Total relevant articles: {len(scored_articles)}")
        logger.info("=" * 60)
        
        return 0
        
    except Exception as e:
        logger.error(f"Agent failed: {e}", exc_info=True)
        return 1


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Web Scraping LLM Agent for Supply Chain Intelligence"
    )
    parser.add_argument(
        "--num-queries",
        type=int,
        default=5,
        help="Number of search queries to generate (default: 5)"
    )
    parser.add_argument(
        "--results-per-query",
        type=int,
        default=10,
        help="Number of results per query (default: 10)"
    )
    parser.add_argument(
        "--timewindow",
        type=int,
        default=None,
        help=f"Time window in days (default: {config.TIME_WINDOW_DAYS})"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=None,
        help=f"Relevance threshold (default: {config.RELEVANCE_THRESHOLD})"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help=f"Output JSONL file (default: {config.OUTPUT_FILE})"
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite output file instead of appending (default: append)"
    )
    
    args = parser.parse_args()
    
    return run_agent(
        num_queries=args.num_queries,
        num_results_per_query=args.results_per_query,
        timewindow_days=args.timewindow,
        threshold=args.threshold,
        output_file=args.output,
        overwrite=args.overwrite,
    )


if __name__ == "__main__":
    sys.exit(main())
