"""
Weather signal ingestion module.

Handles validation and normalization of weather-related signals.
"""

from typing import List
from ..schemas import MonitoringSignal, SourceType, SignalType


def ingest_weather_signals(signals: List[MonitoringSignal]) -> List[MonitoringSignal]:
    """
    Ingest and normalize weather signals.
    
    Args:
        signals: List of raw monitoring signals
        
    Returns:
        List of validated and normalized weather signals
        
    Raises:
        ValueError: If signal validation fails
    """
    normalized = []
    
    for signal in signals:
        # Validate this is a weather signal
        if signal.sourceType != SourceType.WEATHER_AGENT:
            continue
            
        if signal.signalType != SignalType.WEATHER_DISRUPTION:
            continue
        
        # Validate schema (Pydantic already does this)
        # Add any weather-specific validation here
        if signal.confidenceScore < 0.0 or signal.confidenceScore > 1.0:
            raise ValueError(f"Invalid confidence score: {signal.confidenceScore}")
        
        # Tag source and normalize
        normalized.append(signal)
    
    return normalized
