"""
Alert qualification filter module.

Decides whether a RiskContext should be converted to an alert based on
signal quality and confidence thresholds.
"""

from typing import List
from ..schemas import RiskContext, SeverityLevel
from ..config import qualification_config


def filter_qualifying_contexts(contexts: List[RiskContext]) -> List[RiskContext]:
    """
    Filter RiskContexts to identify those that should become alerts.
    
    Qualification rules:
    - Alert if:
        * Single signal with confidence >= threshold (configurable), OR
        * Multiple signals in same context (any confidence)
    - Multiple signals indicate correlation from different sources
    
    Thresholds are controlled by qualification_config and can be tuned at runtime.
    
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
    
    if not signals:
        return False
    
    # Rule 1: Multiple signals - any confidence level qualifies
    # (grouped signals indicate correlation from different sources/metrics)
    if len(signals) >= 2:
        return True
    
    # Rule 2: Single signal - only qualify if confidence meets threshold
    # Threshold is configurable via qualification_config.single_signal_confidence_threshold
    if len(signals) == 1:
        return signals[0].confidenceScore >= qualification_config.single_signal_confidence_threshold
    
    return False
