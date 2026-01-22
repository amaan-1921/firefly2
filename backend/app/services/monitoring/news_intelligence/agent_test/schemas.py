"""
Data models for scraped articles.
"""

from dataclasses import dataclass
from typing import Optional


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
