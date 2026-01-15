"""
News Intelligence Agent for Supply Chain Disruption Monitoring

This agent fetches Google RSS feeds and identifies supply chain disruption news
with strict relevance filtering. It emits structured MonitoringSignal objects
for high-confidence disruption events.

Key characteristics:
- Ingest RSS feeds (Google News Business topic)
- Normalize and deduplicate articles
- Apply strict relevance filtering (precision over recall)
- Emit MonitoringSignal objects for relevant events
- Stateless operation: no database writes, no alert triggering
- No LLM calls: evidence text is factual, LLM-ready

Output: JSONL file containing MonitoringSignal objects
"""

import json
import logging
import uuid
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple, Optional, Set
import feedparser

try:
    from . import config
    from .schemas import MonitoringSignal, SignalType, SeverityLevel, NormalizedArticle
    from .normalization import normalize_article, strip_html, clean_text
    from .deduplication import deduplicate_articles
except ImportError:
    import config
    from schemas import MonitoringSignal, SignalType, SeverityLevel, NormalizedArticle
    from normalization import normalize_article, strip_html, clean_text
    from deduplication import deduplicate_articles

# Configure logging
logger = logging.getLogger(__name__)




def _contains_false_positive(text: str) -> bool:
    """
    Check if text contains false positive patterns.
    
    Args:
        text: Lowercased text to check
        
    Returns:
        True if false positive pattern detected, False otherwise
    """
    for pattern in config.FALSE_POSITIVE_PATTERNS:
        if pattern in text:
            logger.debug(f"    False positive pattern detected: '{pattern}'")
            return True
    return False


def _extract_entity_from_text(text: str) -> Optional[str]:
    """
    Extract the most relevant logistics entity or location from article text.
    
    Args:
        text: Lowercased article text
        
    Returns:
        The entity name, or None if no entity found
    """
    # Check all entity categories
    for category, entities in config.LOGISTICS_ENTITIES.items():
        for entity in entities:
            if entity in text:
                return entity.title()  # Return title-cased version
    
    return None


def _determine_signal_type(text: str) -> Optional[SignalType]:
    """
    Determine the most appropriate signal type based on article content.
    
    Args:
        text: Lowercased article text
        
    Returns:
        SignalType enum value, or None if indeterminate
    """
    # Map keywords to signal types
    type_mappings = [
        (["port congestion", "port backlog"], SignalType.PORT_CONGESTION_NEWS),
        (["port strike", "port labor", "port dispute"], SignalType.PORT_STRIKE_NEWS),
        (["shipping delay", "cargo delay"], SignalType.SHIPPING_DELAY_NEWS),
        (["logistics disruption", "supply chain disruption"], SignalType.LOGISTICS_DISRUPTION_NEWS),
        (["factory shutdown", "production halt"], SignalType.FACTORY_SHUTDOWN_NEWS),
        (["strike"], SignalType.LABOR_STRIKE_NEWS),  # General strike
        (["maritime incident", "cargo incident"], SignalType.CARGO_INCIDENT_NEWS),
        (["supply disruption"], SignalType.SUPPLY_DISRUPTION_NEWS),
    ]
    
    for keywords, signal_type in type_mappings:
        for keyword in keywords:
            if keyword in text:
                return signal_type
    
    # Default
    return SignalType.SUPPLY_DISRUPTION_NEWS


def is_supply_chain_relevant(article: NormalizedArticle) -> Tuple[bool, Optional[str], Optional[SignalType]]:
    """
    Determine if an article is relevant to supply chain disruption.
    
    Strict filtering rules:
    1. MUST contain at least one DISRUPTION_KEYWORD
    2. MUST mention at least one LOGISTICS_ENTITY
    3. MUST NOT match FALSE_POSITIVE_PATTERNS
    4. No LLM inference - pure keyword matching only
    
    Args:
        article: Normalized article to check
        
    Returns:
        Tuple of (is_relevant: bool, entity_reference: str or None, signal_type: SignalType or None)
    """
    text = article.get_text()
    logger.debug(f"\n--- Checking relevance: {article.title[:60]}...")
    
    # Check for false positives first
    if _contains_false_positive(text):
        logger.debug(f"    ✗ REJECTED: Contains false positive pattern")
        return False, None, None
    
    # Check for disruption keywords (MUST have at least one)
    has_disruption_keyword = False
    matched_disruption_keywords = []
    
    for keyword in config.DISRUPTION_KEYWORDS:
        if keyword in text:
            has_disruption_keyword = True
            matched_disruption_keywords.append(keyword)
    
    logger.debug(f"    Disruption keywords: {matched_disruption_keywords if matched_disruption_keywords else 'NONE'}")
    
    if not has_disruption_keyword:
        logger.debug(f"    ✗ REJECTED: No disruption keywords found")
        return False, None, None
    
    # Check for logistics entities (MUST have at least one)
    entity = _extract_entity_from_text(text)
    
    logger.debug(f"    Logistics entity: {entity if entity else 'NONE'}")
    
    if not entity:
        logger.debug(f"    ✗ REJECTED: No logistics entity mentioned")
        return False, None, None
    
    # All checks passed
    signal_type = _determine_signal_type(text)
    logger.debug(f"    ✓ ACCEPTED: Signal type = {signal_type.value if signal_type else 'UNKNOWN'}")
    
    return True, entity, signal_type


def _create_monitoring_signal(
    article: NormalizedArticle,
    entity_reference: str,
    signal_type: SignalType,
    confidence_score: float = 0.6
) -> MonitoringSignal:
    """
    Create a MonitoringSignal from a relevant article.
    
    Args:
        article: Normalized article
        entity_reference: Logistics entity mentioned in article
        signal_type: Type of disruption signal
        confidence_score: Confidence in the signal (0.5-0.7)
        
    Returns:
        MonitoringSignal object
    """
    # Generate signal ID
    signal_id = str(uuid.uuid4())
    
    # Create evidence: 1-2 sentence factual summary
    # Take first 150 chars of summary, or fall back to title
    evidence_base = article.summary if article.summary else article.title
    evidence = clean_text(evidence_base[:200])
    
    # Ensure evidence ends with period
    if evidence and not evidence.endswith('.'):
        evidence = evidence.rsplit(' ', 1)[0] + '.'  # Remove incomplete last word and add period
    
    # Create signal
    signal = MonitoringSignal(
        signalId=signal_id,
        signalType=signal_type,
        sourceType="External",
        sourceReference=entity_reference,
        severityLevel=SeverityLevel.LOW,
        confidenceScore=min(confidence_score, 0.7),  # Cap at 0.7
        expectedImpactWindow="3-7 days",
        evidence=evidence,
        articleTitle=article.title,
        articleUrl=article.url,
        publisher=article.publisher,
        timestamp=datetime.utcnow().isoformat(),
        articlePublishedDate=article.published_date
    )
    
    return signal


def run(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Entry point for the News Intelligence Agent.
    
    Workflow:
    1. Fetch RSS feeds
    2. Normalize articles
    3. Deduplicate
    4. Apply strict relevance filtering
    5. Emit MonitoringSignal objects for relevant events
    6. Persist signals to JSONL file
    
    This agent operates statelessly - no database writes, no alerts triggered.
    
    Args:
        context (dict): Context payload from orchestrator
        
    Returns:
        dict: Status object with execution details
    """
    execution_id = None
    
    try:
        # Generate execution metadata
        execution_id = str(uuid.uuid4())
        execution_timestamp = datetime.utcnow().isoformat()
        
        logger.info(f"Starting News Intelligence Agent execution: {execution_id}")
        
        # Load configuration
        feed_urls = config.FEED_URLS
        polling_window_days = config.POLLING_WINDOW_DAYS
        output_path = config.OUTPUT_PATH
        
        # Compute time window
        current_time = datetime.utcnow()
        cutoff_time = current_time - timedelta(days=polling_window_days)
        
        logger.info(f"Polling window: {polling_window_days} days (cutoff: {cutoff_time.isoformat()})")
        logger.info(f"Fetching from {len(feed_urls)} feed(s)")
        
        # Step 1: Fetch and normalize articles
        raw_articles = []
        
        for feed_url in feed_urls:
            try:
                logger.info(f"Fetching feed: {feed_url}")
                # Add timeout and User-Agent headers
                feed = feedparser.parse(
                    feed_url,
                    request_headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                )
                
                # Check for parsing errors
                if feed.bozo and isinstance(feed.bozo_exception, Exception):
                    logger.warning(f"Feed parsing warning for {feed_url}: {feed.bozo_exception}")
                
                # Process each entry in the feed
                for entry in feed.entries:
                    try:
                        # Normalize the article
                        normalized_article = normalize_article(entry)
                        raw_articles.append(normalized_article)
                        logger.debug(f"Normalized article: {normalized_article.title[:50]}...")
                    except ValueError as e:
                        logger.debug(f"Skipping entry: {e}")
                        continue
                
                logger.info(f"Successfully processed {len(feed.entries)} entries from {feed_url}")
                
            except Exception as e:
                logger.error(f"Failed to fetch feed {feed_url}: {str(e)}")
                continue
        
        logger.info(f"Fetched and normalized {len(raw_articles)} articles")
        
        # Step 2: Deduplicate articles
        deduped_articles = deduplicate_articles(raw_articles)
        logger.info(f"After deduplication: {len(deduped_articles)} unique articles")
        
        # Step 3: Apply strict relevance filtering and emit signals
        monitoring_signals: List[MonitoringSignal] = []
        
        for article in deduped_articles:
            is_relevant, entity_ref, signal_type = is_supply_chain_relevant(article)
            
            if is_relevant and entity_ref and signal_type:
                # Create and add monitoring signal
                signal = _create_monitoring_signal(
                    article=article,
                    entity_reference=entity_ref,
                    signal_type=signal_type,
                    confidence_score=0.6
                )
                monitoring_signals.append(signal)
                logger.info(f"✓ Emitted signal: {signal_type.value} for {entity_ref}")
        
        logger.info(f"Emitted {len(monitoring_signals)} monitoring signals")
        
        # Step 4: Persist signals to JSONL file
        output_file = persist_signals(
            monitoring_signals,
            execution_id,
            execution_timestamp,
            context,
            output_path
        )
        
        logger.info(f"Persisted signals to {output_file}")
        
        return {
            "success": True,
            "execution_id": execution_id,
            "output_file": output_file,
            "signals_count": len(monitoring_signals),
            "articles_processed": len(deduped_articles),
            "message": f"Successfully emitted {len(monitoring_signals)} monitoring signals from {len(deduped_articles)} articles"
        }
    
    except Exception as e:
        logger.error(f"Agent execution failed: {str(e)}", exc_info=True)
        return {
            "success": False,
            "execution_id": execution_id,
            "message": f"Agent execution failed: {str(e)}"
        }


def persist_signals(
    signals: List[MonitoringSignal],
    execution_id: str,
    execution_timestamp: str,
    context: Dict[str, Any],
    output_path: str
) -> str:
    """
    Persist monitoring signals to a JSONL file.
    
    File format:
    - Line 1: Metadata line with execution info
    - Lines 2+: One MonitoringSignal per line (JSON)
    
    Each run appends new signals to the same file.
    
    Args:
        signals: List of MonitoringSignal objects
        execution_id: Execution identifier
        execution_timestamp: When this execution ran
        context: Original context from orchestrator
        output_path: Base output directory path
        
    Returns:
        str: Path to the persisted JSONL file
    """
    import os
    
    # Create output directory if it doesn't exist
    os.makedirs(output_path, exist_ok=True)
    
    # Fixed output filename
    output_filename = "output.jsonl"
    output_file = os.path.join(output_path, output_filename)
    
    # Read existing signals (if file exists)
    existing_signals = []
    
    if os.path.exists(output_file):
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                first_line = f.readline()
                # Skip metadata line, read remaining signals
                for line in f:
                    if line.strip():
                        try:
                            signal_dict = json.loads(line)
                            existing_signals.append(signal_dict)
                        except json.JSONDecodeError:
                            logger.warning(f"Could not parse signal line: {line[:100]}")
        except Exception as e:
            logger.warning(f"Could not read existing output file: {e}. Will start fresh.")
    
    # Combine existing and new signals
    all_signals = existing_signals + [signal.to_dict() for signal in signals]
    
    # Create metadata
    metadata = {
        "execution_id": execution_id,
        "execution_timestamp": execution_timestamp,
        "signals_count": len(all_signals),
        "signals_in_this_run": len(signals),
        "_type": "metadata",
        "context_payload": context
    }
    
    # Write all signals to file (overwrite)
    with open(output_file, "w", encoding="utf-8") as f:
        # Write metadata as first line
        f.write(json.dumps(metadata, ensure_ascii=False) + "\n")
        
        # Write all signals
        for signal_dict in all_signals:
            f.write(json.dumps(signal_dict, ensure_ascii=False) + "\n")
    
    logger.info(f"Persisted {len(all_signals)} total signals to {output_file}")
    
    return output_file
