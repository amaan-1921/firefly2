"""
Stateless News Intelligence Ingestion Agent for Google RSS Feeds

This agent fetches Google RSS feeds and filters for supply chain related events
based on pre-defined keywords. It persists raw ingestion records to JSONL format.
It performs only basic validation and keyword filtering.
"""

import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List
import feedparser

try:
    from . import config
except ImportError:
    import config

# Configure logging
logger = logging.getLogger(__name__)


def is_supply_chain_relevant(entry: Dict[str, Any]) -> bool:
    """
    Check if an RSS entry is relevant to supply chain based on pre-defined keywords.
    
    Uses a flexible matching approach:
    - MUST contain at least one core supply chain relevance keyword, OR
    - MUST contain keywords from at least 2 different categories
    
    Args:
        entry (dict): RSS feed entry
        
    Returns:
        bool: True if entry contains supply chain relevant keywords, False otherwise
    """
    # Get text from entry (title + summary)
    title = entry.get("title", "").lower()
    summary = entry.get("summary", "").lower()
    text = f"{title} {summary}"
    
    # Load keywords from config
    relevance_keywords = config.SUPPLY_CHAIN_RELEVANCE_KEYWORDS
    keyword_categories = config.SUPPLY_CHAIN_KEYWORDS
    
    # Log what we're checking
    logger.debug(f"\n--- Checking: {title[:80]}")
    logger.debug(f"    Text sample: {text[:150]}...")
    
    # Check if text contains relevance keywords (must have at least one)
    matched_relevance_keywords = [kw for kw in relevance_keywords if kw.lower() in text]
    has_relevance_keyword = len(matched_relevance_keywords) > 0
    
    logger.debug(f"    Relevance keywords found: {matched_relevance_keywords if matched_relevance_keywords else 'NONE'}")
    
    # If has core relevance keyword, accept immediately
    if has_relevance_keyword:
        logger.debug(f"    ✓ ACCEPTED: Has relevance keywords")
        return True
    
    # Check which categories have matches
    matching_categories = []
    matched_keywords = []
    
    for category, keywords in keyword_categories.items():
        for keyword in keywords:
            if keyword.lower() in text:
                matching_categories.append(category)
                matched_keywords.append(f"{keyword}")
                break  # Only count one match per category
    
    logger.debug(f"    Category matches: {list(set(matching_categories)) if matching_categories else 'NONE'}")
    logger.debug(f"    Keywords matched: {matched_keywords if matched_keywords else 'NONE'}")
    
    # Check for common false positive patterns
    false_positive_terms = [
        "nfl", "nba", "nhl", "mlb", "sports", "game", "season", "draft",
        "movie", "film", "golden globe", "oscar", "emmy", "telecast",
        "video game", "call of duty", "playstation", "xbox", "nintendo"
    ]
    
    has_false_positive = any(term in text for term in false_positive_terms)
    
    if has_false_positive:
        logger.debug(f"    False positive pattern detected")
    
    # Consider relevant if has at least 2 category matches (and no false positives)
    is_relevant = len(matching_categories) >= 2 and not has_false_positive
    
    if is_relevant:
        logger.debug(f"    ✓ ACCEPTED: Has 2+ category matches")
    else:
        logger.debug(f"    ✗ REJECTED: Insufficient matches ({len(matching_categories)} categories)")
    
    return is_relevant

def run(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Entry point for the News Intelligence ingestion agent.
    
    This function is callable by an orchestrator and operates statelessly.
    It fetches Google RSS feeds, extracts raw metadata, attaches execution metadata,
    and persists all records to a JSON file.
    
    Args:
        context (dict): Context payload from orchestrator containing execution metadata
        
    Returns:
        dict: Status object with 'success' boolean and optional 'message' and 'output_file'
    """
    try:
        # Generate execution metadata
        execution_id = str(uuid.uuid4())
        execution_timestamp = datetime.utcnow().isoformat()
        
        logger.info(f"Starting ingestion agent execution: {execution_id}")
        
        # Load configuration
        feed_urls = config.FEED_URLS
        polling_window_days = config.POLLING_WINDOW_DAYS
        output_path = config.OUTPUT_PATH
        
        # Compute time window
        current_time = datetime.utcnow()
        cutoff_time = current_time - timedelta(days=polling_window_days)
        
        logger.info(f"Polling window: {polling_window_days} days (cutoff: {cutoff_time.isoformat()})")
        logger.info(f"Fetching from {len(feed_urls)} feed(s)")
        
        # Accumulate raw records
        raw_records = []
        
        # Fetch and parse each feed
        for feed_url in feed_urls:
            try:
                logger.info(f"Fetching feed: {feed_url}")
                # Add timeout and User-Agent to avoid blocking
                feed = feedparser.parse(
                    feed_url,
                    request_headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                )
                
                # Check for parsing errors
                if feed.bozo and isinstance(feed.bozo_exception, Exception):
                    logger.warning(f"Feed parsing warning for {feed_url}: {feed.bozo_exception}")
                
                # Extract feed identifier
                feed_id = feed_url
                
                # Process each entry in the feed
                for entry in feed.entries:
                    # Extract raw metadata
                    title = entry.get("title", "").strip()
                    summary = entry.get("summary", "") or entry.get("description", "")
                    summary = summary.strip()
                    
                    # Extract published timestamp
                    published_timestamp = None
                    if "published" in entry:
                        published_timestamp = entry.published
                    elif "updated" in entry:
                        published_timestamp = entry.updated
                    
                    # Extract URL
                    article_url = entry.get("link", "").strip()
                    
                    # Extract publisher/source name
                    publisher = entry.get("author", "").strip()
                    if not publisher:
                        publisher = feed.feed.get("title", "Unknown").strip()
                    
                    # Basic validation: skip entries missing title or URL
                    if not title or not article_url:
                        logger.debug(f"Skipping entry due to missing title or URL")
                        continue
                    
                    # Filter by supply chain relevance
                    if not is_supply_chain_relevant(entry):
                        logger.debug(f"Skipping entry not relevant to supply chain: {title[:50]}...")
                        continue
                    
                    # Create raw record
                    raw_record = {
                        "title": title,
                        "summary": summary,
                        "published_timestamp": published_timestamp,
                        "publisher": publisher,
                        "article_url": article_url,
                        "feed_id": feed_id,
                        "execution_metadata": {
                            "execution_id": execution_id,
                            "execution_timestamp": execution_timestamp,
                            "context_payload": context,
                        }
                    }
                    
                    raw_records.append(raw_record)
                    logger.debug(f"Added record: {title[:50]}...")
                
                logger.info(f"Successfully processed {len(feed.entries)} entries from {feed_url}")
                
            except Exception as e:
                # Log error and continue with remaining feeds
                logger.error(f"Failed to fetch feed {feed_url}: {str(e)}")
                continue
        
        # Persist records to JSON file
        output_file = persist_records(
            raw_records, 
            execution_id, 
            output_path
        )
        
        logger.info(f"Persisted {len(raw_records)} records to {output_file}")
        
        return {
            "success": True,
            "execution_id": execution_id,
            "output_file": output_file,
            "records_count": len(raw_records),
            "message": f"Successfully ingested {len(raw_records)} articles"
        }
    
    except Exception as e:
        logger.error(f"Agent execution failed: {str(e)}", exc_info=True)
        return {
            "success": False,
            "execution_id": execution_id if 'execution_id' in locals() else None,
            "message": f"Agent execution failed: {str(e)}"
        }


def persist_records(
    records: List[Dict[str, Any]], 
    execution_id: str, 
    output_path: str
) -> str:
    """
    Persist raw ingestion records to a JSONL file.
    
    Creates the output directory if it doesn't exist and appends records to a
    fixed output.jsonl file. Each run appends new records to the same file.
    The metadata line (first line) is updated with the cumulative record count.
    
    Args:
        records (list): List of raw record dictionaries
        execution_id (str): Execution identifier
        output_path (str): Base output directory path
        
    Returns:
        str: Path to the persisted JSONL file
    """
    import os
    
    # Create output directory if it doesn't exist
    os.makedirs(output_path, exist_ok=True)
    
    # Fixed output filename
    output_filename = "output.jsonl"
    output_file = os.path.join(output_path, output_filename)
    
    # Check if file exists and read existing records
    existing_records = []
    existing_metadata = None
    
    if os.path.exists(output_file):
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                first_line = f.readline()
                if first_line:
                    existing_metadata = json.loads(first_line)
                    # Read remaining records
                    for line in f:
                        if line.strip():
                            existing_records.append(json.loads(line))
        except Exception as e:
            logger.warning(f"Could not read existing output file: {e}. Will overwrite.")
    
    # Combine existing and new records
    all_records = existing_records + records
    
    # Create updated metadata
    metadata = {
        "execution_id": execution_id,
        "execution_timestamp": datetime.utcnow().isoformat(),
        "records_count": len(all_records),
        "_type": "metadata",
        "last_execution_id": execution_id
    }
    
    # Write all records to file (overwrite)
    with open(output_file, "w", encoding="utf-8") as f:
        # Write metadata as first line
        f.write(json.dumps(metadata, ensure_ascii=False) + "\n")
        
        # Write all records
        for record in all_records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    
    return output_file
