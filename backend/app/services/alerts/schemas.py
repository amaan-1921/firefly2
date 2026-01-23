"""
Pydantic schemas for the Alerts Module.

Defines core data structures:
- MonitoringSignal: Raw signal from monitoring agents
- RiskContext: Grouped related signals
- Alert: Human-facing alert output
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from datetime import datetime


class SeverityLevel(str, Enum):
    """Severity levels for monitoring signals."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SignalType(str, Enum):
    """Types of monitoring signals."""
    WEATHER_DISRUPTION = "WEATHER_DISRUPTION"
    PO_DELAY_RISK = "PO_DELAY_RISK"
    SUPPLIER_PERFORMANCE_DROP = "SUPPLIER_PERFORMANCE_DROP"
    NEWS_RISK = "NEWS_RISK"


class SourceType(str, Enum):
    """Source agents emitting signals."""
    WEATHER_AGENT = "WEATHER_AGENT"
    NEWS_AGENT = "NEWS_AGENT"
    PO_AGENT = "PO_AGENT"
    SUPPLIER_AGENT = "SUPPLIER_AGENT"


class AlertPriority(str, Enum):
    """Alert priority levels."""
    P1 = "P1"  # High urgency
    P2 = "P2"  # Medium urgency
    P3 = "P3"  # Low urgency


class MonitoringSignal(BaseModel):
    """
    Represents a signal emitted by a monitoring agent.
    
    This is the raw input to the Alerts Module.
    """
    signalType: SignalType
    sourceType: SourceType
    sourceReference: str = Field(..., description="Reference ID (e.g., PO-123, SUP-45)")
    severityLevel: SeverityLevel
    confidenceScore: float = Field(..., ge=0.0, le=1.0, description="0.0 to 1.0")
    expectedImpactWindow: str = Field(..., description="e.g., '2 hours', '1 day'")
    evidence: str = Field(..., description="Brief explanation of why this signal was raised")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class RiskContext(BaseModel):
    """
    Groups related signals by a common entity.
    
    Example: Weather + PO Delay both affecting PO-123 are grouped in one RiskContext.
    """
    contextId: str = Field(..., description="Unique identifier for this risk context")
    relatedEntity: str = Field(..., description="Common entity (PO ID, supplier ID, region)")
    signals: List[MonitoringSignal]
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        arbitrary_types_allowed = True


class Alert(BaseModel):
    """
    Human-facing alert derived from one or more signals.
    
    This is the final output of the Alerts Module.
    """
    alertId: str = Field(..., description="Unique alert identifier")
    title: str = Field(..., description="Short, clear title for the alert")
    summary: str = Field(..., description="Concise explanation understandable by non-technical users")
    priority: AlertPriority
    confidenceScore: float = Field(..., ge=0.0, le=1.0)
    relatedSignals: List[SignalType] = Field(default_factory=list)
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        arbitrary_types_allowed = True
