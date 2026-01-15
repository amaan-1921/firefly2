"""
Deduplication module for News Intelligence Agent

Removes duplicate and near-duplicate articles using simple string matching.
Focuses on precision over recall.
"""

import logging
from typing import List, Set, Tuple
from difflib import SequenceMatcher

try:
    from .schemas import NormalizedArticle, DeduplicationKey
except ImportError:
    from schemas import NormalizedArticle, DeduplicationKey

logger = logging.getLogger(__name__)


def normalize_title_for_dedup(title: str) -> str:
    """
    Normalize a title for deduplication comparison.
    
    Args:
        title: Article title
        
    Returns:
        Normalized title for comparison
    """
    # Convert to lowercase
    normalized = title.lower()
    # Remove common prefixes (e.g., "BREAKING:", "UPDATE:", etc.)
    normalized = normalized.replace("breaking:", "").replace("update:", "")
    normalized = normalized.replace("breaking -", "").replace("update -", "")
    # Remove extra whitespace
    normalized = " ".join(normalized.split())
    return normalized


def string_similarity(a: str, b: str) -> float:
    """
    Calculate similarity between two strings (0.0 to 1.0).
    
    Args:
        a: First string
        b: Second string
        
    Returns:
        Similarity score between 0.0 and 1.0
    """
    if not a or not b:
        return 0.0
    
    # Use SequenceMatcher for efficient comparison
    matcher = SequenceMatcher(None, a, b)
    return matcher.ratio()


def are_duplicates(
    article1: NormalizedArticle,
    article2: NormalizedArticle,
    title_similarity_threshold: float = 0.85,
    content_similarity_threshold: float = 0.8
) -> bool:
    """
    Determine if two articles are duplicates based on title and content similarity.
    
    Uses a two-stage approach:
    1. If titles are very similar (>85%), likely duplicates
    2. If content is very similar (>80%) and from similar publisher, likely duplicates
    
    Args:
        article1: First normalized article
        article2: Second normalized article
        title_similarity_threshold: Threshold for title similarity (0.0-1.0)
        content_similarity_threshold: Threshold for content similarity (0.0-1.0)
        
    Returns:
        True if articles are considered duplicates, False otherwise
    """
    
    # Stage 1: Title similarity
    norm_title1 = normalize_title_for_dedup(article1.title)
    norm_title2 = normalize_title_for_dedup(article2.title)
    
    title_sim = string_similarity(norm_title1, norm_title2)
    
    if title_sim >= title_similarity_threshold:
        logger.debug(f"Duplicate detected by title similarity: {title_sim:.2f}")
        return True
    
    # Stage 2: Content similarity (only if titles are somewhat similar)
    if title_sim > 0.5:  # Only check content if titles are at least moderately similar
        content_sim = string_similarity(
            article1.get_text()[:500],  # Compare first 500 chars
            article2.get_text()[:500]
        )
        
        if content_sim >= content_similarity_threshold:
            logger.debug(f"Duplicate detected by content similarity: {content_sim:.2f}")
            return True
    
    return False


def deduplicate_articles(
    articles: List[NormalizedArticle],
) -> List[NormalizedArticle]:
    """
    Remove duplicate articles from a list.
    
    Uses a greedy approach: iterate through articles and keep only the first occurrence
    of each duplicate group.
    
    Args:
        articles: List of normalized articles
        
    Returns:
        List with duplicates removed
    """
    
    if not articles:
        return []
    
    deduped = []
    seen_keys: Set[DeduplicationKey] = set()
    
    for article in articles:
        # Create a simple dedup key
        key = DeduplicationKey(
            normalized_title=normalize_title_for_dedup(article.title),
            publisher=article.publisher.lower()
        )
        
        # Check if we've seen this key before
        if key in seen_keys:
            logger.debug(f"Skipping duplicate: {article.title[:50]}...")
            continue
        
        # Check for near-duplicates with existing articles
        is_duplicate = False
        for existing in deduped:
            if are_duplicates(article, existing):
                logger.debug(f"Skipping near-duplicate: {article.title[:50]}...")
                is_duplicate = True
                break
        
        if not is_duplicate:
            deduped.append(article)
            seen_keys.add(key)
            logger.debug(f"Added article: {article.title[:50]}...")
    
    logger.info(f"Deduplicated {len(articles)} articles -> {len(deduped)} articles")
    
    return deduped
