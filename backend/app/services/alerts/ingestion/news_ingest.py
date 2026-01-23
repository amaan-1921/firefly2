"""
News signal ingestion module.

Handles conversion of news articles (from JSONL) to MonitoringSignal objects.
Maps article fields to standardized signal format.
"""

from typing import List, Optional
from datetime import datetime
from ..schemas import MonitoringSignal, SignalType, SourceType, SeverityLevel
from .jsonl_loader import load_jsonl_file
from ..config import ingestion_config


def ingest_news_signals(
    file_path: Optional[str] = None
) -> List[MonitoringSignal]:
    """
    Ingest and normalize news signals from articles JSONL file.
    
    Converts article records to MonitoringSignal objects using:
    - Article relevance_score → confidenceScore
    - Article title + content → evidence
    - Article metadata → sourceReference
    
    Args:
        file_path: Path to articles JSONL file.
                  If None, uses default path:
                  backend/app/services/monitoring/news_intelligence/agent_test/scraped_articles.jsonl
        
    Returns:
        List of MonitoringSignal objects derived from articles.
        Returns empty list if file not found or contains no valid articles.
    """
    # Use default path if not provided
    if file_path is None:
        file_path = ingestion_config.default_news_file
    
    # Load raw JSON records from file
    raw_records = load_jsonl_file(file_path)
    
    normalized = []
    
    for idx, record in enumerate(raw_records):
        try:
            # Convert article record to MonitoringSignal
            signal = convert_article_to_signal(record, idx)
            if signal:
                normalized.append(signal)
                
        except Exception as e:
            if ingestion_config.log_parse_errors:
                print(f"[News Ingestion] Warning: Failed to convert article to signal: {e}")
            if not ingestion_config.skip_invalid_records:
                raise
            continue
    
    print(f"[News Ingestion] Processed {len(normalized)} valid news signals")
    return normalized


def convert_article_to_signal(article: dict, index: int) -> Optional[MonitoringSignal]:
    """
    Convert a single article record to a MonitoringSignal.
    
    Args:
        article: Article record from JSONL
        index: Article index (for unique sourceReference)
        
    Returns:
        MonitoringSignal object or None if conversion fails
    """
    # Extract article fields
    title = article.get('title', 'Untitled')
    content = article.get('content', '')
    url = article.get('url', '')
    publisher = article.get('publisher', 'Unknown')
    relevance_score = article.get('relevance_score', 0.7)
    relevance_reason = article.get('relevance_reason', '')
    published_date = article.get('published_date', '')
    
    # Build sourceReference from publisher and index
    source_ref = f"NEWS-{publisher.replace(' ', '-').upper()}_{index}"
    
    # Build evidence from article metadata
    evidence_parts = []
    if title:
        evidence_parts.append(f"Title: {title}")
    if relevance_reason:
        evidence_parts.append(f"Relevance: {relevance_reason}")
    if published_date:
        evidence_parts.append(f"Published: {published_date}")
    
    evidence = ". ".join(evidence_parts)
    if not evidence:
        evidence = f"News article from {publisher}"
    
    # Determine severity based on relevance score
    # High relevance (>= 0.8) = HIGH severity
    # Medium relevance (0.6-0.8) = MEDIUM severity
    # Lower relevance (< 0.6) = LOW severity
    try:
        rel_score = float(relevance_score)
        if rel_score >= 0.8:
            severity = SeverityLevel.HIGH
        elif rel_score >= 0.6:
            severity = SeverityLevel.MEDIUM
        else:
            severity = SeverityLevel.LOW
    except (ValueError, TypeError):
        severity = SeverityLevel.MEDIUM
    
    # Ensure confidence score is in valid range
    try:
        confidence = float(relevance_score)
        confidence = max(0.0, min(1.0, confidence))
    except (ValueError, TypeError):
        confidence = 0.7
    
    # Parse timestamp if available
    timestamp = None
    if 'scraped_at' in article:
        try:
            timestamp = article['scraped_at']
        except Exception:
            pass
    
    # Create MonitoringSignal
    try:
        signal = MonitoringSignal(
            signalType=SignalType.NEWS_RISK,
            sourceType=SourceType.NEWS_AGENT,
            sourceReference=source_ref,
            severityLevel=severity,
            confidenceScore=confidence,
            expectedImpactWindow="1–7 days",
            evidence=evidence,
            timestamp=timestamp
        )
        return signal
    except Exception as e:
        print(f"[News Ingestion] Failed to create MonitoringSignal: {e}")
        return None
