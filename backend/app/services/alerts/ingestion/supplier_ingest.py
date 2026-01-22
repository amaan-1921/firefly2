"""
Supplier signal ingestion module.

Handles validation and normalization of supplier performance-related signals.
"""

from typing import List
from ..schemas import MonitoringSignal, SourceType, SignalType


def ingest_supplier_signals(signals: List[MonitoringSignal]) -> List[MonitoringSignal]:
    """
    Ingest and normalize supplier performance signals.
    
    Args:
        signals: List of raw monitoring signals
        
    Returns:
        List of validated and normalized supplier signals
        
    Raises:
        ValueError: If signal validation fails
    """
    normalized = []
    
    for signal in signals:
        # Validate this is a supplier signal
        if signal.sourceType != SourceType.SUPPLIER_AGENT:
            continue
            
        if signal.signalType != SignalType.SUPPLIER_PERFORMANCE_DROP:
            continue
        
        # Validate schema (Pydantic already does this)
        # Add any supplier-specific validation here
        if signal.confidenceScore < 0.0 or signal.confidenceScore > 1.0:
            raise ValueError(f"Invalid confidence score: {signal.confidenceScore}")
        
        # Validate supplier reference format
        if not signal.sourceReference.startswith("SUP-"):
            raise ValueError(f"Invalid supplier reference: {signal.sourceReference}")
        
        # Tag source and normalize
        normalized.append(signal)
    
    return normalized
