"""
Signal grouping and aggregation module.

Groups related signals by common entity (PO ID, supplier ID, region)
to create RiskContext objects.
"""

from typing import List, Dict
from ..schemas import MonitoringSignal, RiskContext, SignalType
import uuid


def group_signals_by_entity(signals: List[MonitoringSignal]) -> List[RiskContext]:
    """
    Group signals by their related entity.
    
    Groups signals that share a common entity reference (PO ID, supplier ID, region).
    This creates RiskContext objects that combine related signals.
    
    Args:
        signals: List of ingested MonitoringSignal objects
        
    Returns:
        List of RiskContext objects, each grouping related signals
    """
    # Dictionary to group signals by entity
    entity_groups: Dict[str, List[MonitoringSignal]] = {}
    
    for signal in signals:
        entity = signal.sourceReference
        
        if entity not in entity_groups:
            entity_groups[entity] = []
        
        entity_groups[entity].append(signal)
    
    # Convert groups to RiskContext objects
    risk_contexts = []
    
    for entity, group_signals in entity_groups.items():
        context_id = f"RISK-{uuid.uuid4().hex[:8].upper()}"
        
        risk_context = RiskContext(
            contextId=context_id,
            relatedEntity=entity,
            signals=group_signals
        )
        
        risk_contexts.append(risk_context)
    
    return risk_contexts
