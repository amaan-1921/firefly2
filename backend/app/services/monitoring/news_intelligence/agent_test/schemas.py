"""
Data models for scraped articles and news intelligence signals.
"""

from dataclasses import dataclass
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class SeverityLevel(str, Enum):
    """Severity levels for news-based signals."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class ScrapedArticle:
    """Represents a scraped article with metadata."""
    title: str
    url: str
    source: str
    publisher: Optional[str]
    published_date: Optional[str]
    content: str
    relevance_score: float
    scraped_at: str
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "title": self.title,
            "url": self.url,
            "source": self.source,
            "publisher": self.publisher,
            "published_date": self.published_date,
            "content": self.content,
            "relevance_score": self.relevance_score,
            "scraped_at": self.scraped_at,
        }


class ScrapedArticleSignal(BaseModel):
    """
    Represents a scraped article converted to a MonitoringSignal format.
    
    Each article is treated as an individual NEWS_RISK signal with:
    - sourceType: NEWS_AGENT
    - signalType: NEWS_RISK
    - sourceReference: The article URL
    - confidenceScore: The relevance_score from the article
    - Additional metadata: title, source, publishedDate for frontend display
    """
    signalId: str = Field(..., description="Unique signal identifier (article URL hash)")
    title: str = Field(..., description="Article title")
    sourceReference: str = Field(..., description="Article URL")
    source: str = Field(..., description="Article domain/publisher source")
    publishedDate: Optional[str] = Field(None, description="ISO format publication date")
    content: str = Field(..., description="Full article content")
    confidenceScore: float = Field(..., ge=0.0, le=1.0, description="Relevance score from 0.0 to 1.0")
    evidence: str = Field(..., description="Brief explanation of relevance")
    scrapedAt: str = Field(..., description="ISO format timestamp when article was scraped")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="UTC timestamp when signal was created")
    
    class Config:
        arbitrary_types_allowed = True
