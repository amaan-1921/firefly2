"""
Alert urgency ranking and prioritization module.

Assigns priority levels (P1, P2, P3) to alerts based on:
- Signal severity
- Confidence score
- Expected impact window

Thresholds are controlled by prioritization_config and can be tuned at runtime.
"""

from typing import List, Tuple
from datetime import datetime, timedelta
from ..schemas import RiskContext, AlertPriority, SeverityLevel
from ..config import prioritization_config


def rank_by_urgency(contexts: List[RiskContext]) -> List[Tuple[RiskContext, AlertPriority]]:
    """
    Rank contexts by urgency and assign priority levels.
    
    Priority assignment logic:
    - P1 (High): CRITICAL severity + high confidence, or HIGH severity + confidence >= 0.85, or immediate impact
    - P2 (Medium): HIGH severity with medium confidence, or MEDIUM severity with high confidence
    - P3 (Low): MEDIUM severity with medium confidence or lower, or LOW severity
    
    Args:
        contexts: List of qualifying RiskContext objects
        
    Returns:
        List of tuples (RiskContext, AlertPriority)
    """
    ranked = []
    
    for context in contexts:
        priority = calculate_priority(context)
        ranked.append((context, priority))
    
    # Sort by priority (P1 first, then P2, then P3)
    priority_order = {AlertPriority.P1: 0, AlertPriority.P2: 1, AlertPriority.P3: 2}
    ranked.sort(key=lambda x: priority_order[x[1]])
    
    return ranked


def calculate_priority(context: RiskContext) -> AlertPriority:
    """
    Calculate the priority for a single RiskContext.
    
    Args:
        context: RiskContext to prioritize
        
    Returns:
        AlertPriority level
    """
    signals = context.signals
    
    # Get the maximum severity and confidence from all signals
    max_severity = max((s.severityLevel for s in signals), default=SeverityLevel.LOW)
    max_confidence = max((s.confidenceScore for s in signals), default=0.0)
    
    # Check impact window urgency
    has_urgent_window = any(
        is_urgent_window(s.expectedImpactWindow) 
        for s in signals
    )
    
    # P1 Assignment Rules (using configurable thresholds)
    if max_severity == SeverityLevel.CRITICAL and max_confidence >= prioritization_config.p1_critical_severity_min_confidence:
        return AlertPriority.P1
    
    if max_severity == SeverityLevel.HIGH and max_confidence >= prioritization_config.p1_high_severity_min_confidence:
        return AlertPriority.P1
    
    if prioritization_config.p1_immediate_impact_enabled and has_urgent_window and max_confidence >= 0.80:
        return AlertPriority.P1
    
    # P2 Assignment Rules (using configurable thresholds)
    if max_severity == SeverityLevel.HIGH and max_confidence >= prioritization_config.p2_high_severity_min_confidence:
        return AlertPriority.P2
    
    if max_severity == SeverityLevel.MEDIUM and max_confidence >= prioritization_config.p2_medium_severity_max_confidence:
        return AlertPriority.P2
    
    if has_urgent_window and max_confidence >= 0.70:
        return AlertPriority.P2
    
    # P3 Assignment (Default for all others)
    return AlertPriority.P3


def is_urgent_window(impact_window: str) -> bool:
    """
    Determine if an impact window indicates urgency.
    
    Urgent windows are those within 6 hours.
    
    Args:
        impact_window: String describing expected impact window (e.g., "2 hours", "1 day")
        
    Returns:
        True if the window is urgent (within 6 hours)
    """
    impact_window_lower = impact_window.lower().strip()
    
    # Parse common formats
    if "hour" in impact_window_lower:
        try:
            hours = int(impact_window_lower.split()[0])
            return hours <= 6
        except (ValueError, IndexError):
            return False
    
    if "minute" in impact_window_lower:
        return True  # Minutes are always urgent
    
    # Days and longer are not urgent
    if "day" in impact_window_lower or "week" in impact_window_lower:
        return False
    
    return False
