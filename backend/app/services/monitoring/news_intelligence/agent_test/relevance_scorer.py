"""
LLM-based relevance scoring for scraped articles.

Reuses LLMFilter pattern from other_rss module.
"""

import logging
from typing import Any, Dict, List

try:
    from . import config
except ImportError:
    import config

# Import LLMFilter from other_rss or use local implementation
try:
    import sys
    from pathlib import Path
    # Try relative import first
    from ..other_rss.llm_filter import LLMFilter, LLMFilterError, ScoredResult
except ImportError:
    try:
        # Fallback: try absolute import
        import sys
        from pathlib import Path
        other_rss_path = Path(__file__).parent.parent / "other_rss"
        sys.path.insert(0, str(other_rss_path))
        from llm_filter import LLMFilter, LLMFilterError, ScoredResult
    except ImportError:
        # Fallback: create local implementation
        import json
        import os
        import re
        import time
        from dataclasses import dataclass
        from typing import Optional
        
        from dotenv import find_dotenv, load_dotenv
        from openai import OpenAI
        from openai import RateLimitError
        
        logger = logging.getLogger(__name__)
        
        class LLMFilterError(RuntimeError):
            pass
        
        @dataclass(frozen=True)
        class ScoredResult:
            relevance_score: float
            reason: str | None = None
        
        def _clamp_score(x: Any) -> float:
            try:
                v = float(x)
            except Exception:
                return 0.0
            if v < 0.0:
                return 0.0
            if v > 1.0:
                return 1.0
            return v
        
        def _extract_json_array(text: str) -> list[Any]:
            if not text:
                raise ValueError("Empty model response")
            stripped = text.strip()
            if stripped.startswith("[") and stripped.endswith("]"):
                return json.loads(stripped)
            m = re.search(r"\[[\s\S]*\]", text)
            if not m:
                raise ValueError("No JSON array found in model response")
            return json.loads(m.group(0))
        
        def _build_prompt(keywords: List[str], articles: List[Dict[str, Any]]) -> str:
            keyword_str = ", ".join(keywords)
            lines: list[str] = []
            lines.append(
                "You are a strict relevance scorer. Given KEYWORDS and ARTICLES, "
                "return a JSON array of objects in the SAME ORDER as ARTICLES."
            )
            lines.append("")
            lines.append("KEYWORDS:")
            lines.append(keyword_str)
            lines.append("")
            lines.append(
                "For each article, output an object: "
                '{"relevance_score": number between 0 and 1, "reason": "short"}'
            )
            lines.append("Return ONLY valid JSON (no markdown, no extra text).")
            lines.append("")
            lines.append("ARTICLES:")
            
            for idx, a in enumerate(articles, start=1):
                title = (a.get("title") or "").strip()
                content = (a.get("content") or "").strip()[:500]  # Limit content length
                url = (a.get("url") or "").strip()
                lines.append(f"{idx}. Title: {title}")
                lines.append(f"   Content: {content}")
                lines.append(f"   URL: {url}")
            return "\n".join(lines)
        
        class LLMFilter:
            def __init__(
                self,
                *,
                api_key_env: str,
                base_url: str,
                model: str,
                timeout_s: float = 30.0,
                max_retries: int = 2,
                initial_backoff_s: float = 1.0,
                max_backoff_s: float = 120.0,
                rate_limit_backoff_multiplier: float = 2.0,
            ):
                dotenv_path = find_dotenv()
                if dotenv_path:
                    load_dotenv(dotenv_path)
                else:
                    load_dotenv()
                
                api_key = os.getenv(api_key_env)
                if not api_key:
                    raise LLMFilterError(
                        f"Missing API key: set `{api_key_env}` in your .env file (project root)."
                    )
                
                self._client = OpenAI(api_key=api_key, base_url=base_url)
                self._model = model
                self._timeout_s = timeout_s
                self._max_retries = max_retries
                self._initial_backoff_s = initial_backoff_s
                self._max_backoff_s = max_backoff_s
                self._rate_limit_backoff_multiplier = rate_limit_backoff_multiplier
            
            def score_articles_batch(
                self,
                *,
                keywords: List[str],
                articles: List[Dict[str, Any]],
            ) -> List[ScoredResult]:
                if not articles:
                    return []
                if not keywords:
                    return [ScoredResult(relevance_score=0.0, reason="No keywords configured")] * len(articles)
                
                prompt = _build_prompt(keywords, articles)
                backoff = self._initial_backoff_s
                last_err: Optional[Exception] = None
                
                for attempt in range(self._max_retries + 1):
                    try:
                        resp = self._client.chat.completions.create(
                            model=self._model,
                            messages=[
                                {"role": "system", "content": "Return only valid JSON."},
                                {"role": "user", "content": prompt},
                            ],
                            temperature=0,
                            timeout=self._timeout_s,
                        )
                        text = (resp.choices[0].message.content or "").strip()
                        arr = _extract_json_array(text)
                        if len(arr) != len(articles):
                            raise ValueError(f"Expected {len(articles)} results, got {len(arr)}")
                        
                        results: list[ScoredResult] = []
                        for item in arr:
                            if isinstance(item, dict):
                                score = _clamp_score(item.get("relevance_score"))
                                reason_val = item.get("reason")
                                reason = str(reason_val) if reason_val is not None else None
                            else:
                                score = _clamp_score(item)
                                reason = None
                            results.append(ScoredResult(relevance_score=score, reason=reason))
                        return results
                    except RateLimitError as e:
                        last_err = e
                        if attempt >= self._max_retries:
                            break
                        backoff = min(backoff * self._rate_limit_backoff_multiplier, self._max_backoff_s)
                        logger.warning(f"Rate limit error (429) on attempt {attempt + 1}/{self._max_retries + 1}. Waiting {backoff:.1f} seconds...")
                        time.sleep(backoff)
                    except Exception as e:
                        last_err = e
                        if attempt >= self._max_retries:
                            break
                        error_str = str(e).lower()
                        if "429" in error_str or "too many requests" in error_str or "rate limit" in error_str:
                            backoff = min(backoff * self._rate_limit_backoff_multiplier, self._max_backoff_s)
                        else:
                            backoff = min(backoff * 2, self._max_backoff_s)
                        logger.warning(f"Error on attempt {attempt + 1}/{self._max_retries + 1}: {e}. Waiting {backoff:.1f} seconds...")
                        time.sleep(backoff)
                
                raise LLMFilterError(f"LLM scoring failed after {self._max_retries + 1} attempts: {last_err}")

logger = logging.getLogger(__name__)


class RelevanceScorer:
    """Scores articles for relevance using LLM."""
    
    def __init__(self):
        self.llm_filter = LLMFilter(
            api_key_env=config.LLM_API_KEY_ENV,
            base_url=config.LLM_BASE_URL,
            model=config.LLM_MODEL,
            max_retries=getattr(config, 'LLM_MAX_RETRIES', 5),
            initial_backoff_s=getattr(config, 'LLM_INITIAL_BACKOFF_S', 2.0),
            max_backoff_s=getattr(config, 'LLM_MAX_BACKOFF_S', 120.0),
            rate_limit_backoff_multiplier=getattr(config, 'LLM_429_BACKOFF_MULTIPLIER', 2.0),
        )
    
    def score_articles(
        self,
        articles: List[Dict[str, Any]],
        batch_size: int = None,
    ) -> List[Dict[str, Any]]:
        """
        Score articles for relevance.
        
        Args:
            articles: List of article dictionaries
            batch_size: Batch size for LLM calls
            
        Returns:
            List of articles with relevance_score added
        """
        if not articles:
            return []
        
        batch_size = batch_size or config.LLM_BATCH_SIZE
        
        # Process in batches
        scored_articles = []
        for i in range(0, len(articles), batch_size):
            batch = articles[i:i + batch_size]
            logger.info(f"Scoring batch {i // batch_size + 1} ({len(batch)} articles)")
            
            try:
                results = self.llm_filter.score_articles_batch(
                    keywords=config.KEYWORDS,
                    articles=batch,
                )
                
                # Add scores to articles
                for article, result in zip(batch, results):
                    article["relevance_score"] = result.relevance_score
                    if result.reason:
                        article["relevance_reason"] = result.reason
                    scored_articles.append(article)
            except LLMFilterError as e:
                logger.error(f"Failed to score batch: {e}")
                # Add articles with score 0.0
                for article in batch:
                    article["relevance_score"] = 0.0
                    scored_articles.append(article)
        
        return scored_articles
    
    def filter_by_threshold(
        self,
        articles: List[Dict[str, Any]],
        threshold: float = None,
    ) -> List[Dict[str, Any]]:
        """
        Filter articles by relevance threshold.
        
        Args:
            articles: List of scored articles
            threshold: Relevance threshold (default from config)
            
        Returns:
            Filtered list of articles
        """
        threshold = threshold or config.RELEVANCE_THRESHOLD
        return [a for a in articles if a.get("relevance_score", 0.0) >= threshold]


def score_and_filter_articles(
    articles: List[Dict[str, Any]],
    threshold: float = None,
) -> List[Dict[str, Any]]:
    """
    Convenience function to score and filter articles.
    
    Args:
        articles: List of article dictionaries
        threshold: Relevance threshold
        
    Returns:
        Filtered list of scored articles
    """
    scorer = RelevanceScorer()
    scored = scorer.score_articles(articles)
    return scorer.filter_by_threshold(scored, threshold)
