"""
Alert qualification filter module.

Decides whether a RiskContext should be converted to an alert based on
signal quality and confidence thresholds.
"""

from typing import List
from ..schemas import RiskContext, SeverityLevel


def filter_qualifying_contexts(contexts: List[RiskContext]) -> List[RiskContext]:
    """
    Filter RiskContexts to identify those that should become alerts.
    
    Qualification rules (MVP):
    - Ignore single low-confidence signals (confidence < 0.7)
    - Alert if:
        * One high-confidence signal (confidence >= 0.85), OR
        * Multiple medium-confidence signals (2+ signals with confidence >= 0.75)
    
    Args:
        contexts: List of RiskContext objects
        
    Returns:
        List of RiskContexts that qualify for alert generation
    """
    qualifying_contexts = []
    
    for context in contexts:
        if should_qualify(context):
            qualifying_contexts.append(context)
    
    return qualifying_contexts


def should_qualify(context: RiskContext) -> bool:
    """
    Determine if a single RiskContext qualifies for alert generation.
    
    Args:
        context: RiskContext object to evaluate
        
    Returns:
        True if the context should generate an alert, False otherwise
    """
    signals = context.signals
    
    # Rule 1: One high-confidence signal
    high_confidence_signals = [
        s for s in signals 
        if s.confidenceScore >= 0.85
    ]
    
    if high_confidence_signals:
        return True
    
    # Rule 2: Multiple medium-confidence signals (2 or more)
    medium_confidence_signals = [
        s for s in signals 
        if s.confidenceScore >= 0.75
    ]
    
    if len(medium_confidence_signals) >= 2:
        return True
    
    # Rule 3: Reject single low-confidence signals
    if len(signals) == 1 and signals[0].confidenceScore < 0.7:
        return False
    
    # Default: No qualification
    return False
