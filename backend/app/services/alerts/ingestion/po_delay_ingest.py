"""
PO Delay signal ingestion module.

Handles validation and normalization of PO delay-related signals.
"""

from typing import List
from ..schemas import MonitoringSignal, SourceType, SignalType


def ingest_po_delay_signals(signals: List[MonitoringSignal]) -> List[MonitoringSignal]:
    """
    Ingest and normalize PO delay signals.
    
    Args:
        signals: List of raw monitoring signals
        
    Returns:
        List of validated and normalized PO delay signals
        
    Raises:
        ValueError: If signal validation fails
    """
    normalized = []
    
    for signal in signals:
        # Validate this is a PO delay signal
        if signal.sourceType != SourceType.PO_AGENT:
            continue
            
        if signal.signalType != SignalType.PO_DELAY_RISK:
            continue
        
        # Validate schema (Pydantic already does this)
        # Add any PO-specific validation here
        if signal.confidenceScore < 0.0 or signal.confidenceScore > 1.0:
            raise ValueError(f"Invalid confidence score: {signal.confidenceScore}")
        
        # Validate PO reference format
        if not signal.sourceReference.startswith("PO-"):
            raise ValueError(f"Invalid PO reference: {signal.sourceReference}")
        
        # Tag source and normalize
        normalized.append(signal)
    
    return normalized
