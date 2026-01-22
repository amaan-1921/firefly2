"""
Data schemas for News Intelligence Agent

Defines the structure of MonitoringSignal and related data types
emitted by the agent.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, List
from enum import Enum
import json


class SignalType(Enum):
    """Types of supply chain disruption signals"""
    PORT_CONGESTION_NEWS = "PORT_CONGESTION_NEWS"
    PORT_STRIKE_NEWS = "PORT_STRIKE_NEWS"
    SHIPPING_DELAY_NEWS = "SHIPPING_DELAY_NEWS"
    LOGISTICS_DISRUPTION_NEWS = "LOGISTICS_DISRUPTION_NEWS"
    FACTORY_SHUTDOWN_NEWS = "FACTORY_SHUTDOWN_NEWS"
    LABOR_STRIKE_NEWS = "LABOR_STRIKE_NEWS"
    CARGO_INCIDENT_NEWS = "CARGO_INCIDENT_NEWS"
    SUPPLY_DISRUPTION_NEWS = "SUPPLY_DISRUPTION_NEWS"


class SeverityLevel(Enum):
    """Severity levels for signals"""
    LOW = "Low"
    MEDIUM = "Medium"


@dataclass
class MonitoringSignal:
    """
    Structured monitoring signal for supply chain disruption news.
    
    This is the output contract for the News Intelligence Agent.
    Each signal represents a single credible news item indicating
    a potential supply chain or logistics disruption.
    """
    
    # Signal identification
    signalId: str  # UUID for this signal
    signalType: SignalType  # Type of disruption
    
    # Source metadata
    sourceType: str = "External"  # Always "External" for RSS news
    sourceReference: str = ""  # Port, location, or logistics entity mentioned
    
    # Signal properties
    severityLevel: SeverityLevel = SeverityLevel.LOW
    confidenceScore: float = 0.5  # 0.5-0.7 based on source credibility
    expectedImpactWindow: str = "3-7 days"  # Expected time window for impact
    
    # Evidence
    evidence: str = ""  # 1-2 sentence factual summary, LLM-friendly, no opinions
    articleTitle: str = ""  # Original article title
    articleUrl: str = ""  # Link to source article
    publisher: str = ""  # Source publication name
    
    # Temporal metadata
    timestamp: str = ""  # ISO datetime when signal was created
    articlePublishedDate: Optional[str] = None  # When the article was published
    
    def to_dict(self) -> dict:
        """Convert to dictionary, handling enums"""
        d = asdict(self)
        d['signalType'] = self.signalType.value
        d['severityLevel'] = self.severityLevel.value
        return d
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), ensure_ascii=False)


@dataclass
class NormalizedArticle:
    """
    Normalized article structure for internal processing.
    """
    
    title: str
    summary: str
    content: str  # Full text: title + summary for analysis
    url: str
    publisher: str
    published_date: Optional[str] = None
    ingestion_timestamp: str = ""
    
    def get_text(self) -> str:
        """Get combined text for keyword matching"""
        return f"{self.title} {self.summary}".lower()


@dataclass
class DeduplicationKey:
    """
    Simple deduplication key based on article content.
    """
    
    normalized_title: str  # Lowercase, cleaned title
    publisher: str
    
    def __hash__(self):
        return hash((self.normalized_title, self.publisher))
    
    def __eq__(self, other):
        if not isinstance(other, DeduplicationKey):
            return False
        return (self.normalized_title == other.normalized_title and 
                self.publisher == other.publisher)
