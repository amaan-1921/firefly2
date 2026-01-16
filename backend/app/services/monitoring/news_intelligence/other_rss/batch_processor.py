#!/usr/bin/env python3
"""
Batch processor for RSS articles with LLM relevance scoring.

Reads articles from `rss_articles.jsonl`, batches them, scores relevance using Groq LLM,
filters by threshold, sorts by score, and writes to `sorted_output.jsonl`.
"""

import argparse
import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List

# Import configuration
try:
    from . import config
except ImportError:
    # Fallback for direct script execution
    import config

# #region agent log
import os
import sys
with open('/mnt/OldVolume/internship/firefly2/.cursor/debug.log', 'a') as f:
    f.write(f'{{"sessionId":"debug-session","runId":"run1","hypothesisId":"H2","location":"batch_processor.py:22","message":"About to import llm_filter","data":{{"sys_path":{sys.path},"cwd":"{os.getcwd()}"}},"timestamp":{int(__import__("time").time()*1000)}}}\n')
# #endregion

try:
    from .llm_filter import LLMFilter, LLMFilterError, ScoredResult
    # #region agent log
    with open('/mnt/OldVolume/internship/firefly2/.cursor/debug.log', 'a') as f:
        f.write(f'{{"sessionId":"debug-session","runId":"run1","hypothesisId":"H2","location":"batch_processor.py:26","message":"llm_filter relative import success","data":{{}},"timestamp":{int(__import__("time").time()*1000)}}}\n')
    # #endregion
except ImportError as e:
    # #region agent log
    with open('/mnt/OldVolume/internship/firefly2/.cursor/debug.log', 'a') as f:
        f.write(f'{{"sessionId":"debug-session","runId":"run1","hypothesisId":"H2","location":"batch_processor.py:30","message":"llm_filter relative import failed, trying absolute","data":{{"error":"{str(e)}","error_type":"{type(e).__name__}"}},"timestamp":{int(__import__("time").time()*1000)}}}\n')
    # #endregion
    # Fallback for direct script execution
    from llm_filter import LLMFilter, LLMFilterError, ScoredResult
    # #region agent log
    with open('/mnt/OldVolume/internship/firefly2/.cursor/debug.log', 'a') as f:
        f.write(f'{{"sessionId":"debug-session","runId":"run1","hypothesisId":"H2","location":"batch_processor.py:34","message":"llm_filter absolute import success","data":{{}},"timestamp":{int(__import__("time").time()*1000)}}}\n')
    # #endregion

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def _chunked(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split a list into chunks of specified size."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def read_articles_from_jsonl(file_path: Path) -> List[Dict[str, Any]]:
    """Read articles from a JSONL file."""
    articles = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    article = json.loads(line)
                    articles.append(article)
                except json.JSONDecodeError as e:
                    logger.warning(f"Skipping invalid JSON on line {line_num}: {e}")
                    continue
        return articles
    except FileNotFoundError:
        logger.error(f"Input file not found: {file_path}")
        raise
    except Exception as e:
        logger.error(f"Error reading {file_path}: {e}")
        raise


def write_articles_jsonl(articles: List[Dict[str, Any]], file_path: Path) -> None:
    """Write articles to a JSONL file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            for article in articles:
                json_line = json.dumps(article, ensure_ascii=False)
                f.write(json_line + '\n')
        logger.info(f"Successfully wrote {len(articles)} articles to {file_path}")
    except Exception as e:
        logger.error(f"Error writing to {file_path}: {e}")
        raise


def main() -> int:
    """Main entry point for batch processing."""
    folder = Path(__file__).resolve().parent
    
    parser = argparse.ArgumentParser(
        description="Batch-process RSS articles with Groq LLM relevance scoring"
    )
    parser.add_argument(
        "--input",
        type=str,
        default=None,
        help=f"Input JSONL filename/path (default: {config.INPUT_FILE})"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help=f"Output JSONL filename/path (default: {config.OUTPUT_FILE})"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help=f"Override config.LLM_BATCH_SIZE (default: {config.LLM_BATCH_SIZE})"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=None,
        help=f"Override config.RELEVANCE_THRESHOLD (default: {config.RELEVANCE_THRESHOLD})"
    )
    args = parser.parse_args()
    
    # Determine file paths
    input_path = Path(args.input).expanduser() if args.input else (folder / config.INPUT_FILE)
    output_path = Path(args.output).expanduser() if args.output else (folder / config.OUTPUT_FILE)
    
    # Get configuration values
    batch_size = int(args.batch_size) if args.batch_size is not None else int(config.LLM_BATCH_SIZE)
    threshold = float(args.threshold) if args.threshold is not None else float(config.RELEVANCE_THRESHOLD)
    
    logger.info(f"Reading input: {input_path}")
    articles = read_articles_from_jsonl(input_path)
    logger.info(f"Loaded {len(articles)} article(s)")
    
    if not articles:
        logger.warning("No articles to process. Writing empty output file.")
        write_articles_jsonl([], output_path)
        return 0
    
    # Initialize LLM filter with rate limiting config
    try:
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
    
    # Process articles in batches with rate limiting
    all_scored_articles: List[tuple[Dict[str, Any], ScoredResult]] = []
    batches = _chunked(articles, batch_size)
    batch_delay = getattr(config, 'LLM_BATCH_DELAY_S', 1.0)
    logger.info(f"Processing {len(articles)} articles in {len(batches)} batch(es) of size {batch_size}")
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
    
    # Filter by threshold and add scores to articles
    filtered_articles: List[Dict[str, Any]] = []
    for article, result in all_scored_articles:
        if result.relevance_score >= threshold:
            # Add score and reason to article dict
            article_with_score = article.copy()
            article_with_score["relevance_score"] = result.relevance_score
            if result.reason:
                article_with_score["relevance_reason"] = result.reason
            filtered_articles.append(article_with_score)
    
    logger.info(
        f"Filtered to {len(filtered_articles)} articles "
        f"(threshold: {threshold}, original: {len(articles)})"
    )
    
    # Sort by relevance score (descending)
    filtered_articles.sort(key=lambda a: a.get("relevance_score", 0.0), reverse=True)
    
    # Write output
    logger.info(f"Writing output: {output_path}")
    write_articles_jsonl(filtered_articles, output_path)
    
    logger.info("Batch processing completed successfully!")
    return 0


if __name__ == "__main__":
    exit(main())
