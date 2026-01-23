"""
FastAPI router for news intelligence endpoints.

Exposes scraped articles as MonitoringSignal-compatible API endpoints.
"""

from fastapi import APIRouter, Query
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from .schemas import ScrapedArticleSignal
from .signal_converter import get_articles_response, load_articles_from_jsonl


class ArticlesResponse(BaseModel):
    """Response wrapper for articles endpoint."""
    count: int = Field(..., description="Number of articles returned")
    articles: List[ScrapedArticleSignal] = Field(..., description="List of article signals")
    lastUpdated: str = Field(..., description="ISO format timestamp of last update")
    filters: dict = Field(..., description="Applied filters and options")


# Create a router for news intelligence endpoints
router = APIRouter(
    prefix="/news-intelligence",
    tags=["news-intelligence"]
)


@router.get("/articles", response_model=ArticlesResponse)
async def get_articles(
    min_relevance_score: float = Query(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Filter articles by minimum relevance score (0.0-1.0)"
    ),
    limit: Optional[int] = Query(
        default=None,
        ge=1,
        description="Maximum number of articles to return"
    ),
    sort_by: str = Query(
        default="relevance_score_desc",
        pattern="^(relevance_score_desc|relevance_score_asc|published_date_desc|published_date_asc|scraped_at_desc)$",
        description="Sorting order for articles"
    )
) -> ArticlesResponse:
    """
    Retrieve scraped news articles as MonitoringSignal-compatible signals.
    
    Each article is treated as an individual NEWS_RISK signal with:
    - sourceReference: Article URL (for linking in frontend)
    - confidenceScore: Relevance score from 0.0-1.0
    - evidence: Brief explanation of relevance
    - Additional metadata: title, source, publishedDate, content
    
    Fresh data is read from scraped_articles.jsonl on each request.
    
    Query Parameters:
        min_relevance_score: Filter to articles with relevance >= this value (default: 0.0)
        limit: Return at most this many articles (default: all)
        sort_by: Sort by relevance_score_desc, relevance_score_asc, published_date_desc,
                 published_date_asc, or scraped_at_desc (default: relevance_score_desc)
    
    Returns:
        ArticlesResponse with count, articles list, lastUpdated, and applied filters
    
    Example:
        GET /monitoring/news-intelligence/articles?min_relevance_score=0.7&limit=10&sort_by=relevance_score_desc
    """
    response_data = get_articles_response(
        min_relevance_score=min_relevance_score,
        limit=limit,
        sort_by=sort_by
    )
    
    return ArticlesResponse(**response_data)


@router.get("/articles/count")
async def get_articles_count(
    min_relevance_score: float = Query(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Filter articles by minimum relevance score"
    )
) -> dict:
    """
    Get total count of articles matching the given filters.
    
    Useful for pagination on the frontend without retrieving full article data.
    
    Returns:
        Dictionary with total count and applied filters
    """
    articles = load_articles_from_jsonl(min_relevance_score=min_relevance_score)
    
    return {
        "total": len(articles),
        "filters": {
            "minRelevanceScore": min_relevance_score
        },
        "lastUpdated": datetime.utcnow().isoformat()
    }
