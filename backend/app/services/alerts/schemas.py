"""
Pydantic schemas for the Alerts Module.

Defines core data structures:
- MonitoringSignal: Raw signal from monitoring agents
- RiskContext: Grouped related signals
- Alert: Human-facing alert output
"""

from pydantic import BaseModel, Field, field_validator
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
    Flexible schema to handle variations from different monitoring sources.
    """
    signalType: SignalType
    sourceType: SourceType
    sourceReference: str = Field(..., description="Reference ID (e.g., PO-123, SUP-45, Chennai)")
    severityLevel: SeverityLevel
    confidenceScore: float = Field(..., ge=0.0, le=1.0, description="0.0 to 1.0")
    expectedImpactWindow: str = Field(..., description="e.g., '2 hours', '1 day', '1–3 days'")
    evidence: str = Field(..., description="Brief explanation of why this signal was raised")
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow, description="UTC timestamp when signal was generated")
    
    @field_validator('sourceType', mode='before')
    @classmethod
    def normalize_source_type(cls, v):
        """
        Normalize sourceType to enum.
        Accepts both enum values and string representations.
        Maps 'External' -> 'WEATHER_AGENT', handles case variations.
        """
        if v is None:
            return SourceType.WEATHER_AGENT
        
        if isinstance(v, SourceType):
            return v
        
        v_str = str(v).upper().strip()
        
        # Map common variations
        mapping = {
            'WEATHER_AGENT': SourceType.WEATHER_AGENT,
            'WEATHER': SourceType.WEATHER_AGENT,
            'EXTERNAL': SourceType.WEATHER_AGENT,  # Weather agent uses 'External'
            'NEWS_AGENT': SourceType.NEWS_AGENT,
            'NEWS': SourceType.NEWS_AGENT,
            'PO_AGENT': SourceType.PO_AGENT,
            'PO': SourceType.PO_AGENT,
            'SUPPLIER_AGENT': SourceType.SUPPLIER_AGENT,
            'SUPPLIER': SourceType.SUPPLIER_AGENT,
        }
        
        if v_str in mapping:
            return mapping[v_str]
        
        # Try direct enum match
        try:
            return SourceType[v_str]
        except KeyError:
            # Default to WEATHER_AGENT for unknown sources
            print(f"Warning: Unknown sourceType '{v}', defaulting to WEATHER_AGENT")
            return SourceType.WEATHER_AGENT
    
    @field_validator('severityLevel', mode='before')
    @classmethod
    def normalize_severity_level(cls, v):
        """
        Normalize severityLevel to enum.
        Accepts both enum values and string representations (case-insensitive).
        """
        if v is None:
            return SeverityLevel.MEDIUM
        
        if isinstance(v, SeverityLevel):
            return v
        
        v_str = str(v).upper().strip()
        
        try:
            return SeverityLevel[v_str]
        except KeyError:
            # Default to MEDIUM for unknown severity
            print(f"Warning: Unknown severityLevel '{v}', defaulting to MEDIUM")
            return SeverityLevel.MEDIUM
    
    class Config:
        arbitrary_types_allowed = True
        extra = "ignore"  # Ignore unknown fields in input


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
