"""
LLM-powered search query generation.

Generates targeted search queries based on supply chain topics and keywords.
"""

import logging
import os
from datetime import datetime
from typing import List

from dotenv import find_dotenv, load_dotenv
from openai import OpenAI

try:
    from . import config
except ImportError:
    import config

logger = logging.getLogger(__name__)


class QueryGeneratorError(RuntimeError):
    pass


class QueryGenerator:
    """Generates search queries using LLM."""
    
    def __init__(
        self,
        *,
        api_key_env: str,
        base_url: str,
        model: str,
        timeout_s: float = 30.0,
        max_retries: int = 2,
    ):
        dotenv_path = find_dotenv()
        if dotenv_path:
            load_dotenv(dotenv_path)
        else:
            load_dotenv()
        
        api_key = os.getenv(api_key_env)
        if not api_key:
            raise QueryGeneratorError(
                f"Missing API key: set `{api_key_env}` in your .env file (project root)."
            )
        
        self._client = OpenAI(api_key=api_key, base_url=base_url)
        self._model = model
        self._timeout_s = timeout_s
        self._max_retries = max_retries
    
    def generate_queries(
        self,
        topics: List[str],
        num_queries: int = 5,
    ) -> List[str]:
        """
        Generate search queries from topics.
        
        Args:
            topics: List of search topics
            num_queries: Number of queries to generate
            
        Returns:
            List of search query strings
        """
        if not topics:
            return []
        
        current_date = datetime.utcnow().strftime("%Y-%m-%d")
        topics_str = ", ".join(topics)
        
        prompt = f"""You are a search query generator for supply chain intelligence.

Given the following topics and current date, generate {num_queries} specific, targeted search queries that would find recent news articles about supply chain, shipments, ports, and trade.

Topics: {topics_str}
Current Date: {current_date}

Requirements:
- Each query should be specific and actionable
- Focus on recent events, disruptions, and updates
- Include relevant keywords like "supply chain", "port", "shipping", "trade", etc.
- Make queries concise (5-10 words each)
- Avoid overly broad queries

Return ONLY a JSON array of query strings, one per line, no other text.
Example format: ["query 1", "query 2", "query 3"]
"""
        
        try:
            resp = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": "Return only valid JSON arrays."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                timeout=self._timeout_s,
            )
            
            text = (resp.choices[0].message.content or "").strip()
            
            # Extract JSON array
            import json
            import re
            
            # Try to find JSON array in response
            match = re.search(r'\[.*?\]', text, re.DOTALL)
            if match:
                queries = json.loads(match.group(0))
            else:
                # Fallback: try parsing entire response
                queries = json.loads(text)
            
            if not isinstance(queries, list):
                raise ValueError("Response is not a list")
            
            # Ensure all items are strings
            queries = [str(q).strip() for q in queries if q]
            
            logger.info(f"Generated {len(queries)} search queries")
            return queries[:num_queries]
            
        except Exception as e:
            logger.error(f"Failed to generate queries: {e}")
            # Fallback: return topics as queries
            logger.warning("Falling back to topics as queries")
            return topics[:num_queries]


def generate_search_queries(topics: List[str], num_queries: int = 5) -> List[str]:
    """
    Convenience function to generate search queries.
    
    Args:
        topics: List of search topics
        num_queries: Number of queries to generate
        
    Returns:
        List of search query strings
    """
    generator = QueryGenerator(
        api_key_env=config.LLM_API_KEY_ENV,
        base_url=config.LLM_BASE_URL,
        model=config.LLM_MODEL,
    )
    return generator.generate_queries(topics, num_queries)
