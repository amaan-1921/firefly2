"""
Alert explainer module.

Converts RiskContexts into human-readable Alert objects.
Generates clear, concise explanations without using LLMs.
"""

import uuid
from typing import List, Tuple
from datetime import datetime
from ..schemas import Alert, AlertPriority, RiskContext, SignalType


def build_alerts(
    ranked_contexts: List[Tuple[RiskContext, AlertPriority]]
) -> List[Alert]:
    """
    Convert ranked RiskContexts into human-readable Alert objects.
    
    Args:
        ranked_contexts: List of (RiskContext, AlertPriority) tuples
        
    Returns:
        List of Alert objects ready for presentation to users
    """
    alerts = []
    
    for context, priority in ranked_contexts:
        alert = build_alert_from_context(context, priority)
        alerts.append(alert)
    
    return alerts


def build_alert_from_context(context: RiskContext, priority: AlertPriority) -> Alert:
    """
    Build a single Alert from a RiskContext and priority.
    
    Args:
        context: RiskContext containing related signals
        priority: AlertPriority level
        
    Returns:
        Alert object with human-readable explanation
    """
    alert_id = f"ALERT-{uuid.uuid4().hex[:8].upper()}"
    
    # Collect signal types for reference
    signal_types = list(set(s.signalType for s in context.signals))
    
    # Generate title based on entity and signal types
    title = generate_title(context.relatedEntity, signal_types)
    
    # Generate summary explanation
    summary = generate_summary(context)
    
    # Calculate average confidence
    avg_confidence = sum(s.confidenceScore for s in context.signals) / len(context.signals)
    
    alert = Alert(
        alertId=alert_id,
        title=title,
        summary=summary,
        priority=priority,
        confidenceScore=avg_confidence,
        relatedSignals=signal_types,
        createdAt=datetime.utcnow()
    )
    
    return alert


def generate_title(entity_reference: str, signal_types: List[SignalType]) -> str:
    """
    Generate a concise, clear alert title.
    
    Handles:
    - PO references (PO-123)
    - Supplier references (SUP-45)
    - Weather locations (Chennai, Mumbai)
    - News sources (NEWS-PUBLISHER)
    - Generic entity references
    
    Args:
        entity_reference: The related entity (PO-123, SUP-45, Chennai, NEWS-PUBLISHER)
        signal_types: List of signal types in this context
        
    Returns:
        Human-readable title
    """
    # Categorize by entity type
    if entity_reference.startswith("PO-"):
        entity_label = f"Purchase Order {entity_reference}"
    elif entity_reference.startswith("SUP-"):
        entity_label = f"Supplier {entity_reference}"
    elif entity_reference.startswith("REGION-"):
        region = entity_reference.replace("REGION-", "")
        entity_label = f"Region: {region}"
    elif entity_reference.startswith("NEWS-"):
        # Extract publisher from NEWS-PUBLISHER_INDEX format
        publisher = entity_reference.replace("NEWS-", "").split("_")[0].replace("-", " ")
        entity_label = f"News: {publisher}"
    else:
        # Assume it's a weather location or generic reference
        entity_label = entity_reference
    
    # Describe the risks
    if len(signal_types) == 1:
        risk_desc = describe_signal_type(signal_types[0])
        return f"{risk_desc} - {entity_label}"
    else:
        return f"Multiple Risks Detected - {entity_label}"


def describe_signal_type(signal_type: SignalType) -> str:
    """
    Convert signal type to human-readable risk description.
    
    Args:
        signal_type: SignalType enum value
        
    Returns:
        Human-readable description
    """
    descriptions = {
        SignalType.WEATHER_DISRUPTION: "Weather Disruption Risk",
        SignalType.PO_DELAY_RISK: "Delivery Delay Risk",
        SignalType.SUPPLIER_PERFORMANCE_DROP: "Supplier Performance Concern",
        SignalType.NEWS_RISK: "Supply Chain Alert",
    }
    return descriptions.get(signal_type, "Risk Alert")


def generate_summary(context: RiskContext) -> str:
    """
    Generate a clear, non-technical explanation of the alert.
    
    Uses signal evidence field directly and adapts context message
    based on entity type (PO, supplier, weather location, news source).
    
    Args:
        context: RiskContext with related signals
        
    Returns:
        Human-readable summary
    """
    signals = context.signals
    
    # Collect evidence statements directly from signal evidence field
    evidence_lines = []
    for signal in signals:
        # Use the evidence field directly from the signal
        evidence_lines.append(
            f"{signal.evidence} (Impact Window: {signal.expectedImpactWindow})"
        )
    
    # Combine evidence
    if len(evidence_lines) == 1:
        explanation = evidence_lines[0]
    else:
        explanation = "\n".join([f"• {line}" for line in evidence_lines])
    
    # Add context about what's being impacted
    entity = context.relatedEntity
    if entity.startswith("PO-"):
        context_msg = f"\nThis affects the procurement for {entity}."
        recommendation = "Review related purchase orders and consider expedited alternatives."
    elif entity.startswith("SUP-"):
        context_msg = f"\nThis affects supplier {entity} and related orders."
        recommendation = "Review supplier performance and consider backup suppliers."
    elif entity.startswith("REGION-"):
        context_msg = f"\nThis affects the {entity.replace('REGION-', '').lower()} region."
        recommendation = "Review shipments in this region and consider route alternatives."
    elif entity.startswith("NEWS-"):
        # News source
        context_msg = f"\nThis is relevant news information affecting supply chain."
        recommendation = "Review the details and assess impact on ongoing operations."
    else:
        # Assume weather location
        context_msg = f"\nThis weather risk affects the {entity} location."
        recommendation = "Monitor conditions and prepare contingency logistics plans."
    
    # Final summary - cleaner format without emojis
    summary = f"{explanation}{context_msg}\n\nRecommendation: {recommendation}"
    
    return summary


def get_severity_emoji(severity_level) -> str:
    """
    DEPRECATED: Kept for backward compatibility only.
    Emojis have been removed from alert formatting.
    
    Args:
        severity_level: SeverityLevel enum value
        
    Returns:
        Emoji string (empty string for cleaner output)
    """
    return ""
