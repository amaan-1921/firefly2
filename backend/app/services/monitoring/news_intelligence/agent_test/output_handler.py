"""
Output handler for writing articles to JSONL format.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Set

try:
    from . import config
except ImportError:
    import config

logger = logging.getLogger(__name__)


def normalize_url(url: str) -> str:
    """
    Normalize URL for comparison (lowercase, remove trailing slash).
    
    Args:
        url: URL string
        
    Returns:
        Normalized URL string
    """
    if not url:
        return ""
    url = url.strip().lower()
    # Remove trailing slash for comparison
    if url.endswith('/'):
        url = url[:-1]
    return url


def read_existing_urls(output_path: Path) -> Set[str]:
    """
    Read existing article URLs from JSONL file.
    
    Args:
        output_path: Path to JSONL file
        
    Returns:
        Set of normalized existing URLs
    """
    existing_urls = set()
    
    if not output_path.exists():
        logger.debug(f"File {output_path} does not exist, no existing URLs to read")
        return existing_urls
    
    try:
        count = 0
        with open(output_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    article = json.loads(line)
                    url = article.get("url")
                    if url:
                        normalized_url = normalize_url(url)
                        existing_urls.add(normalized_url)
                        count += 1
                except json.JSONDecodeError:
                    logger.warning(f"Skipping invalid JSON line in {output_path}")
                    continue
        
        logger.info(f"Read {count} existing URLs from {output_path}")
    except Exception as e:
        logger.warning(f"Error reading existing URLs from {output_path}: {e}")
    
    return existing_urls


def filter_unique_articles(
    articles: List[Dict[str, Any]],
    existing_urls: Set[str],
) -> List[Dict[str, Any]]:
    """
    Filter out articles that already exist based on URL.
    Also deduplicates within the batch (first occurrence wins).
    
    Args:
        articles: List of article dictionaries
        existing_urls: Set of normalized existing URLs from file
        
    Returns:
        List of unique articles (not in existing_urls or seen in this batch)
    """
    unique_articles = []
    duplicates = 0
    seen_in_batch = set()  # Track URLs in this batch to avoid duplicates within batch
    
    logger.debug(f"Filtering {len(articles)} articles against {len(existing_urls)} existing URLs")
    
    for article in articles:
        url = article.get("url")
        if not url:
            # Articles without URLs are considered unique (might be errors)
            unique_articles.append(article)
            continue
        
        normalized_url = normalize_url(url)
        
        # Check if URL already exists in file OR in this batch
        if normalized_url not in existing_urls and normalized_url not in seen_in_batch:
            unique_articles.append(article)
            seen_in_batch.add(normalized_url)  # Track in current batch only
        else:
            duplicates += 1
            logger.debug(f"Duplicate found: {url}")
    
    if duplicates > 0:
        logger.info(f"Filtered out {duplicates} duplicate article(s) (already exist in file or within batch)")
    
    return unique_articles


def write_articles_jsonl(
    articles: List[Dict[str, Any]],
    output_path: Path | str,
    append: bool = True,
) -> None:
    """
    Write articles to JSONL file.
    
    Args:
        articles: List of article dictionaries
        output_path: Path to output JSONL file
        append: If True, append to existing file; if False, overwrite (default: True)
    """
    output_path = Path(output_path)
    
    try:
        mode = 'a' if append else 'w'
        with open(output_path, mode, encoding='utf-8') as f:
            for article in articles:
                json_line = json.dumps(article, ensure_ascii=False)
                f.write(json_line + '\n')
        
        action = "appended" if append else "wrote"
        logger.info(f"Successfully {action} {len(articles)} articles to {output_path}")
    except Exception as e:
        logger.error(f"Error writing to {output_path}: {e}")
        raise


def write_scraped_articles(
    articles: List[Dict[str, Any]],
    output_file: str = None,
    append: bool = True,
    deduplicate: bool = True,
) -> Path:
    """
    Write scraped articles to JSONL file with optional deduplication.
    
    Args:
        articles: List of article dictionaries
        output_file: Output filename (default from config)
        append: If True, append to existing file; if False, overwrite (default: True)
        deduplicate: If True, filter out articles that already exist (by URL) (default: True)
        
    Returns:
        Path to output file
    """
    if output_file is None:
        output_file = config.OUTPUT_FILE
    
    output_path = Path(__file__).parent / output_file
    
    # Deduplicate if requested and appending
    if deduplicate and append:
        if output_path.exists():
            logger.info(f"Deduplicating against existing file: {output_path}")
            existing_urls = read_existing_urls(output_path)
            original_count = len(articles)
            articles = filter_unique_articles(articles, existing_urls)
            logger.info(f"After deduplication: {len(articles)} unique article(s) to add (filtered {original_count - len(articles)} duplicates)")
        else:
            logger.info(f"Output file does not exist yet, skipping deduplication")
    
    if articles:
        write_articles_jsonl(articles, output_path, append=append)
    else:
        logger.info("No new unique articles to write")
    
    return output_path
