"""
News signal ingestion module.

Handles validation and normalization of news-related signals.
"""

from typing import List
from ..schemas import MonitoringSignal, SourceType, SignalType


def ingest_news_signals(signals: List[MonitoringSignal]) -> List[MonitoringSignal]:
    """
    Ingest and normalize news signals.
    
    Args:
        signals: List of raw monitoring signals
        
    Returns:
        List of validated and normalized news signals
        
    Raises:
        ValueError: If signal validation fails
    """
    normalized = []
    
    for signal in signals:
        # Validate this is a news signal
        if signal.sourceType != SourceType.NEWS_AGENT:
            continue
            
        if signal.signalType != SignalType.NEWS_RISK:
            continue
        
        # Validate schema (Pydantic already does this)
        # Add any news-specific validation here
        if signal.confidenceScore < 0.0 or signal.confidenceScore > 1.0:
            raise ValueError(f"Invalid confidence score: {signal.confidenceScore}")
        
        # Tag source and normalize
        normalized.append(signal)
    
    return normalized
