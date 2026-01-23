"""
Converts scraped articles from JSONL to news intelligence signals.

Reads scraped_articles.jsonl and transforms each article into a ScrapedArticleSignal
that can be integrated into the alerts pipeline and frontend.
"""

import json
import hashlib
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from .schemas import ScrapedArticleSignal


def _generate_signal_id(article_url: str) -> str:
    """Generate a unique signal ID from the article URL."""
    return hashlib.md5(article_url.encode()).hexdigest()


def load_articles_from_jsonl(
    file_path: Optional[str] = None,
    min_relevance_score: float = 0.0,
    limit: Optional[int] = None,
    sort_by: str = "relevance_score_desc"
) -> List[ScrapedArticleSignal]:
    """
    Load scraped articles from JSONL file and convert to ScrapedArticleSignal objects.
    
    Args:
        file_path: Path to scraped_articles.jsonl. If None, uses default location.
        min_relevance_score: Filter articles by minimum relevance score (0.0-1.0).
        limit: Maximum number of articles to return. None for all.
        sort_by: Sorting order. Options: 'relevance_score_desc', 'relevance_score_asc',
                 'published_date_desc', 'published_date_asc', 'scraped_at_desc'.
    
    Returns:
        List of ScrapedArticleSignal objects.
    
    Raises:
        FileNotFoundError: If JSONL file doesn't exist.
        json.JSONDecodeError: If JSONL is malformed.
    """
    # Resolve file path
    if file_path is None:
        # Use default location relative to this file
        file_path = Path(__file__).parent / "scraped_articles.jsonl"
    else:
        file_path = Path(file_path)
    
    signals = []
    
    # Return empty list if file doesn't exist (graceful degradation)
    if not file_path.exists():
        return signals
    
    # Read and parse JSONL
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, start=1):
                if not line.strip():
                    continue
                
                try:
                    article_data = json.loads(line)
                    
                    # Filter by relevance score
                    relevance_score = float(article_data.get('relevance_score', 0.0))
                    if relevance_score < min_relevance_score:
                        continue
                    
                    # Convert article to signal
                    signal = ScrapedArticleSignal(
                        signalId=_generate_signal_id(article_data.get('url', '')),
                        title=article_data.get('title', 'Untitled'),
                        sourceReference=article_data.get('url', ''),
                        source=article_data.get('source', 'Unknown'),
                        publishedDate=article_data.get('published_date'),
                        content=article_data.get('content', ''),
                        confidenceScore=relevance_score,
                        evidence=article_data.get('relevance_reason', 'Supply chain related news'),
                        scrapedAt=article_data.get('scraped_at', datetime.utcnow().isoformat()),
                    )
                    signals.append(signal)
                
                except (json.JSONDecodeError, ValueError) as e:
                    print(f"Warning: Failed to parse line {line_num} in {file_path}: {e}")
                    continue
    
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []
    
    # Sort results
    if sort_by == "relevance_score_desc":
        signals.sort(key=lambda s: s.confidenceScore, reverse=True)
    elif sort_by == "relevance_score_asc":
        signals.sort(key=lambda s: s.confidenceScore, reverse=False)
    elif sort_by == "published_date_desc":
        signals.sort(key=lambda s: s.publishedDate or '', reverse=True)
    elif sort_by == "published_date_asc":
        signals.sort(key=lambda s: s.publishedDate or '', reverse=False)
    elif sort_by == "scraped_at_desc":
        signals.sort(key=lambda s: s.scrapedAt, reverse=True)
    
    # Apply limit
    if limit is not None:
        signals = signals[:limit]
    
    return signals


def get_articles_response(
    min_relevance_score: float = 0.0,
    limit: Optional[int] = None,
    sort_by: str = "relevance_score_desc"
) -> dict:
    """
    Get articles formatted as a response object for API endpoints.
    
    Args:
        min_relevance_score: Filter articles by minimum relevance score (0.0-1.0).
        limit: Maximum number of articles to return. None for all.
        sort_by: Sorting order.
    
    Returns:
        Dictionary with count, articles, and lastUpdated timestamp.
    """
    articles = load_articles_from_jsonl(
        min_relevance_score=min_relevance_score,
        limit=limit,
        sort_by=sort_by
    )
    
    return {
        "count": len(articles),
        "articles": articles,
        "lastUpdated": datetime.utcnow().isoformat(),
        "filters": {
            "minRelevanceScore": min_relevance_score,
            "limit": limit,
            "sortBy": sort_by
        }
    }
