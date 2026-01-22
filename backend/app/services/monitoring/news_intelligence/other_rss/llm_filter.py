"""
LLM relevance scoring using Groq (OpenAI-compatible API).

This module is intentionally "pure LLM": it does not read/write JSONL and does not
batch on its own. Batching/orchestration is handled by `batch_processor.py`.
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

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
    """
    Best-effort extraction of the first JSON array from a model response.
    """
    if not text:
        raise ValueError("Empty model response")

    # Fast path: response is the array itself
    stripped = text.strip()
    if stripped.startswith("[") and stripped.endswith("]"):
        return json.loads(stripped)

    # Try to find the first [...] block
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
        summary = (a.get("summary") or "").strip()
        url = (a.get("url") or "").strip()
        lines.append(f"{idx}. Title: {title}")
        lines.append(f"   Summary: {summary}")
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
            # Still allow explicit env vars even if .env isn't found.
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
            # No keywords => everything irrelevant (caller can decide what to do)
            return [ScoredResult(relevance_score=0.0, reason="No keywords configured")] * len(
                articles
            )

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
                    raise ValueError(
                        f"Expected {len(articles)} results, got {len(arr)}"
                    )

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
                # Special handling for 429 rate limit errors
                last_err = e
                if attempt >= self._max_retries:
                    break
                # Use longer backoff for rate limit errors
                backoff = min(backoff * self._rate_limit_backoff_multiplier, self._max_backoff_s)
                logger.warning(
                    f"Rate limit error (429) on attempt {attempt + 1}/{self._max_retries + 1}. "
                    f"Waiting {backoff:.1f} seconds before retry..."
                )
                time.sleep(backoff)
            except Exception as e:
                last_err = e
                if attempt >= self._max_retries:
                    break
                # Check if it's a 429 error from the exception message/status
                error_str = str(e).lower()
                if "429" in error_str or "too many requests" in error_str or "rate limit" in error_str:
                    # Treat as rate limit error
                    backoff = min(backoff * self._rate_limit_backoff_multiplier, self._max_backoff_s)
                    logger.warning(
                        f"Rate limit detected on attempt {attempt + 1}/{self._max_retries + 1}. "
                        f"Waiting {backoff:.1f} seconds before retry..."
                    )
                else:
                    # Regular exponential backoff for other errors
                    backoff = min(backoff * 2, self._max_backoff_s)
                    logger.warning(
                        f"Error on attempt {attempt + 1}/{self._max_retries + 1}: {e}. "
                        f"Waiting {backoff:.1f} seconds before retry..."
                    )
                time.sleep(backoff)

        raise LLMFilterError(f"LLM scoring failed after {self._max_retries + 1} attempts: {last_err}")

