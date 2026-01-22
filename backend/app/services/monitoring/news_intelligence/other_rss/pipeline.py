#!/usr/bin/env python3
"""
Pipeline orchestrator for RSS feed aggregation and LLM relevance scoring.

This script runs the complete pipeline:
1. Fetch RSS feeds and filter by time window (rss_aggregator.py)
2. Score articles for relevance using LLM (batch_processor.py)
3. Output sorted, filtered articles

This can be imported by other modules or run directly from the command line.
"""

import argparse
import logging
import os
import sys
import time
from pathlib import Path

# #region agent log
with open('/mnt/OldVolume/internship/firefly2/.cursor/debug.log', 'a') as f:
    f.write(f'{{"sessionId":"debug-session","runId":"run1","hypothesisId":"H1,H2,H3,H4","location":"pipeline.py:17","message":"Import debug: sys.path and cwd","data":{{"sys_path":{sys.path},"cwd":"{os.getcwd()}","__file__":"{__file__}"}},"timestamp":{int(__import__("time").time()*1000)}}}\n')
# #endregion

# Import configuration
try:
    from . import config
    # #region agent log
    with open('/mnt/OldVolume/internship/firefly2/.cursor/debug.log', 'a') as f:
        f.write(f'{{"sessionId":"debug-session","runId":"run1","hypothesisId":"H1","location":"pipeline.py:22","message":"Config import: relative success","data":{{}},"timestamp":{int(__import__("time").time()*1000)}}}\n')
    # #endregion
except ImportError as e:
    # #region agent log
    with open('/mnt/OldVolume/internship/firefly2/.cursor/debug.log', 'a') as f:
        f.write(f'{{"sessionId":"debug-session","runId":"run1","hypothesisId":"H1","location":"pipeline.py:26","message":"Config import: relative failed, trying absolute","data":{{"error":"{str(e)}"}},"timestamp":{int(__import__("time").time()*1000)}}}\n')
    # #endregion
    # Fallback for direct script execution
    import config
    # #region agent log
    with open('/mnt/OldVolume/internship/firefly2/.cursor/debug.log', 'a') as f:
        f.write(f'{{"sessionId":"debug-session","runId":"run1","hypothesisId":"H1","location":"pipeline.py:30","message":"Config import: absolute success","data":{{}},"timestamp":{int(__import__("time").time()*1000)}}}\n')
    # #endregion

# Import pipeline components
try:
    # #region agent log
    with open('/mnt/OldVolume/internship/firefly2/.cursor/debug.log', 'a') as f:
        f.write(f'{{"sessionId":"debug-session","runId":"run1","hypothesisId":"H1","location":"pipeline.py:35","message":"Trying relative imports","data":{{}},"timestamp":{int(__import__("time").time()*1000)}}}\n')
    # #endregion
    from .rss_aggregator import (
        fetch_all_feeds_concurrently,
        filter_articles_by_time_window,
        write_jsonl,
        DEFAULT_RSS_FEEDS,
    )
    # #region agent log
    with open('/mnt/OldVolume/internship/firefly2/.cursor/debug.log', 'a') as f:
        f.write(f'{{"sessionId":"debug-session","runId":"run1","hypothesisId":"H1","location":"pipeline.py:42","message":"rss_aggregator relative import success","data":{{}},"timestamp":{int(__import__("time").time()*1000)}}}\n')
    # #endregion
    from .batch_processor import (
        read_articles_from_jsonl,
        write_articles_jsonl,
        _chunked,
    )
    # #region agent log
    with open('/mnt/OldVolume/internship/firefly2/.cursor/debug.log', 'a') as f:
        f.write(f'{{"sessionId":"debug-session","runId":"run1","hypothesisId":"H2","location":"pipeline.py:48","message":"batch_processor relative import success","data":{{}},"timestamp":{int(__import__("time").time()*1000)}}}\n')
    # #endregion
    from .llm_filter import LLMFilter, LLMFilterError, ScoredResult
    # #region agent log
    with open('/mnt/OldVolume/internship/firefly2/.cursor/debug.log', 'a') as f:
        f.write(f'{{"sessionId":"debug-session","runId":"run1","hypothesisId":"H1","location":"pipeline.py:52","message":"All relative imports success","data":{{}},"timestamp":{int(__import__("time").time()*1000)}}}\n')
    # #endregion
except ImportError as e:
    # #region agent log
    with open('/mnt/OldVolume/internship/firefly2/.cursor/debug.log', 'a') as f:
        f.write(f'{{"sessionId":"debug-session","runId":"run1","hypothesisId":"H1,H2","location":"pipeline.py:55","message":"Relative imports failed, trying absolute","data":{{"error":"{str(e)}","error_type":"{type(e).__name__}"}},"timestamp":{int(__import__("time").time()*1000)}}}\n')
    # #endregion
    # Fallback for direct script execution
    try:
        from rss_aggregator import (
            fetch_all_feeds_concurrently,
            filter_articles_by_time_window,
            write_jsonl,
            DEFAULT_RSS_FEEDS,
        )
        # #region agent log
        with open('/mnt/OldVolume/internship/firefly2/.cursor/debug.log', 'a') as f:
            f.write(f'{{"sessionId":"debug-session","runId":"run1","hypothesisId":"H3","location":"pipeline.py:65","message":"rss_aggregator absolute import success","data":{{}},"timestamp":{int(__import__("time").time()*1000)}}}\n')
        # #endregion
        from batch_processor import (
            read_articles_from_jsonl,
            write_articles_jsonl,
            _chunked,
        )
        # #region agent log
        with open('/mnt/OldVolume/internship/firefly2/.cursor/debug.log', 'a') as f:
            f.write(f'{{"sessionId":"debug-session","runId":"run1","hypothesisId":"H2","location":"pipeline.py:71","message":"batch_processor absolute import attempt","data":{{}},"timestamp":{int(__import__("time").time()*1000)}}}\n')
        # #endregion
        from llm_filter import LLMFilter, LLMFilterError, ScoredResult
        # #region agent log
        with open('/mnt/OldVolume/internship/firefly2/.cursor/debug.log', 'a') as f:
            f.write(f'{{"sessionId":"debug-session","runId":"run1","hypothesisId":"H1","location":"pipeline.py:75","message":"All absolute imports success","data":{{}},"timestamp":{int(__import__("time").time()*1000)}}}\n')
        # #endregion
    except ImportError as e2:
        # #region agent log
        with open('/mnt/OldVolume/internship/firefly2/.cursor/debug.log', 'a') as f:
            f.write(f'{{"sessionId":"debug-session","runId":"run1","hypothesisId":"H2,H4","location":"pipeline.py:78","message":"Absolute imports also failed","data":{{"error":"{str(e2)}","error_type":"{type(e2).__name__}"}},"timestamp":{int(__import__("time").time()*1000)}}}\n')
        # #endregion
        raise

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_pipeline(
    feed_urls=None,
    timewindow_days=None,
    batch_size=None,
    threshold=None,
    intermediate_file=None,
    output_file=None,
    max_workers=5,
) -> int:
    """
    Run the complete RSS aggregation and LLM scoring pipeline.
    
    Args:
        feed_urls: List of RSS feed URLs (default: config or DEFAULT_RSS_FEEDS)
        timewindow_days: Days to look back for articles (default: config.TIME_WINDOW_DAYS)
        batch_size: Articles per LLM batch (default: config.LLM_BATCH_SIZE)
        threshold: Relevance score threshold (default: config.RELEVANCE_THRESHOLD)
        intermediate_file: Path for intermediate JSONL (default: config.INPUT_FILE)
        output_file: Path for final output JSONL (default: config.OUTPUT_FILE)
        max_workers: Max concurrent RSS fetchers (default: 5)
        
    Returns:
        0 on success, 1 on error
    """
    folder = Path(__file__).resolve().parent
    
    # Set defaults from config
    if feed_urls is None:
        feed_urls = DEFAULT_RSS_FEEDS
    if timewindow_days is None:
        timewindow_days = config.TIME_WINDOW_DAYS
    if batch_size is None:
        batch_size = config.LLM_BATCH_SIZE
    if threshold is None:
        threshold = config.RELEVANCE_THRESHOLD
    if intermediate_file is None:
        intermediate_file = folder / config.INPUT_FILE
    else:
        intermediate_file = Path(intermediate_file).expanduser()
    if output_file is None:
        output_file = folder / config.OUTPUT_FILE
    else:
        output_file = Path(output_file).expanduser()
    
    # Step 1: Fetch and time-filter articles
    logger.info("=" * 60)
    logger.info("STEP 1: Fetching RSS feeds and filtering by time window")
    logger.info("=" * 60)
    logger.info(f"Time window: {timewindow_days} day(s)")
    logger.info(f"Number of feeds: {len(feed_urls)}")
    
    try:
        all_articles = fetch_all_feeds_concurrently(feed_urls, max_workers=max_workers)
        logger.info(f"Fetched {len(all_articles)} total articles from all feeds")
        
        filtered_articles = filter_articles_by_time_window(all_articles, timewindow_days)
        logger.info(f"Filtered to {len(filtered_articles)} articles within time window")
        
        # Write intermediate file
        logger.info(f"Writing intermediate file: {intermediate_file}")
        write_jsonl(filtered_articles, str(intermediate_file))
        
    except Exception as e:
        logger.error(f"Step 1 failed: {e}")
        return 1
    
    if not filtered_articles:
        logger.warning("No articles found after time filtering. Writing empty output.")
        write_articles_jsonl([], output_file)
        return 0
    
    # Step 2: LLM relevance scoring and filtering
    logger.info("=" * 60)
    logger.info("STEP 2: Scoring articles with LLM and filtering by relevance")
    logger.info("=" * 60)
    logger.info(f"Batch size: {batch_size}")
    logger.info(f"Relevance threshold: {threshold}")
    
    try:
        # Initialize LLM filter with rate limiting config
        llm_filter = LLMFilter(
            api_key_env=config.LLM_API_KEY_ENV,
            base_url=config.LLM_BASE_URL,
            model=config.LLM_MODEL,
            max_retries=getattr(config, 'LLM_MAX_RETRIES', 5),
            initial_backoff_s=getattr(config, 'LLM_INITIAL_BACKOFF_S', 2.0),
            max_backoff_s=getattr(config, 'LLM_MAX_BACKOFF_S', 120.0),
            rate_limit_backoff_multiplier=getattr(config, 'LLM_429_BACKOFF_MULTIPLIER', 2.0),
        )
    except LLMFilterError as e:
        logger.error(f"Failed to initialize LLM filter: {e}")
        return 1
    
    # Read articles from intermediate file
    articles = read_articles_from_jsonl(intermediate_file)
    
    # Process in batches with rate limiting
    all_scored_articles = []
    batches = _chunked(articles, batch_size)
    batch_delay = getattr(config, 'LLM_BATCH_DELAY_S', 1.0)
    logger.info(f"Processing {len(articles)} articles in {len(batches)} batch(es)")
    logger.info(f"Rate limiting: {batch_delay}s delay between batches, max {getattr(config, 'LLM_MAX_RETRIES', 5)} retries per batch")
    
    for batch_idx, batch in enumerate(batches, start=1):
        logger.info(f"Processing batch {batch_idx}/{len(batches)} ({len(batch)} articles)")
        try:
            results = llm_filter.score_articles_batch(
                keywords=config.KEYWORDS,
                articles=batch
            )
            
            # Pair articles with their scores
            for article, result in zip(batch, results):
                all_scored_articles.append((article, result))
            
            # Add delay between batches to prevent rate limiting (except for last batch)
            if batch_idx < len(batches) and batch_delay > 0:
                logger.debug(f"Waiting {batch_delay}s before next batch to avoid rate limits...")
                time.sleep(batch_delay)
                
        except LLMFilterError as e:
            logger.error(f"LLM scoring failed for batch {batch_idx}: {e}")
            # Continue with other batches, but mark these as failed
            for article in batch:
                all_scored_articles.append((
                    article,
                    ScoredResult(relevance_score=0.0, reason="LLM scoring failed")
                ))
            # Still add delay even after error to avoid compounding rate limits
            if batch_idx < len(batches) and batch_delay > 0:
                logger.debug(f"Waiting {batch_delay}s before next batch after error...")
                time.sleep(batch_delay)
    
    # Filter by threshold and add scores
    filtered_scored = []
    for article, result in all_scored_articles:
        if result.relevance_score >= threshold:
            article_with_score = article.copy()
            article_with_score["relevance_score"] = result.relevance_score
            if result.reason:
                article_with_score["relevance_reason"] = result.reason
            filtered_scored.append(article_with_score)
    
    logger.info(
        f"Filtered to {len(filtered_scored)} articles "
        f"(threshold: {threshold}, original: {len(articles)})"
    )
    
    # Sort by relevance score (descending)
    filtered_scored.sort(key=lambda a: a.get("relevance_score", 0.0), reverse=True)
    
    # Write final output
    logger.info(f"Writing final output: {output_file}")
    write_articles_jsonl(filtered_scored, output_file)
    
    logger.info("=" * 60)
    logger.info("Pipeline completed successfully!")
    logger.info(f"Final output: {output_file}")
    logger.info(f"Total relevant articles: {len(filtered_scored)}")
    logger.info("=" * 60)
    
    return 0


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Run complete RSS aggregation and LLM relevance scoring pipeline"
    )
    parser.add_argument(
        "--feeds",
        nargs="+",
        default=None,
        help="RSS feed URLs (default: use config or built-in defaults)"
    )
    parser.add_argument(
        "--timewindow",
        type=int,
        default=None,
        help=f"Time window in days (default: {config.TIME_WINDOW_DAYS})"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help=f"LLM batch size (default: {config.LLM_BATCH_SIZE})"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=None,
        help=f"Relevance threshold (default: {config.RELEVANCE_THRESHOLD})"
    )
    parser.add_argument(
        "--intermediate",
        type=str,
        default=None,
        help=f"Intermediate JSONL file (default: {config.INPUT_FILE})"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help=f"Output JSONL file (default: {config.OUTPUT_FILE})"
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=5,
        help="Max concurrent RSS fetchers (default: 5)"
    )
    
    args = parser.parse_args()
    
    return run_pipeline(
        feed_urls=args.feeds,
        timewindow_days=args.timewindow,
        batch_size=args.batch_size,
        threshold=args.threshold,
        intermediate_file=args.intermediate,
        output_file=args.output,
        max_workers=args.max_workers,
    )


if __name__ == "__main__":
    sys.exit(main())
