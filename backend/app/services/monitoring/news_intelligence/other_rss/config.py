"""
Configuration for RSS Feed Aggregator + LLM relevance scoring pipeline.

`rss_aggregator.py` uses `TIME_WINDOW_DAYS` to time-filter and writes `rss_articles.jsonl`.
`batch_processor.py` reads `rss_articles.jsonl`, scores relevance via Groq, and writes
`sorted_output.jsonl`.
"""

# ============================================================================
# AGGREGATOR CONFIG
# ============================================================================
TIME_WINDOW_DAYS = 15

# Default input/output filenames (relative to this folder)
INPUT_FILE = "rss_articles.jsonl"
OUTPUT_FILE = "sorted_output.jsonl"

# ============================================================================
# LLM (GROQ) CONFIG
# ============================================================================
LLM_PROVIDER = "groq"
LLM_MODEL = "openai/gpt-oss-20b"
LLM_API_KEY_ENV = "GROQ_API_KEY"
LLM_BASE_URL = "https://api.groq.com/openai/v1"

# Batch size (number of articles per LLM call)
LLM_BATCH_SIZE = 10

# Keep articles with relevance_score >= threshold
RELEVANCE_THRESHOLD = 0.7

# Rate limiting configuration
LLM_MAX_RETRIES = 5  # Increased from default 2
LLM_INITIAL_BACKOFF_S = 2.0  # Initial backoff in seconds
LLM_MAX_BACKOFF_S = 120.0  # Maximum backoff for 429 errors (2 minutes)
LLM_BATCH_DELAY_S = 1.0  # Delay between batch requests (seconds)
LLM_429_BACKOFF_MULTIPLIER = 2.0  # Multiplier for 429 errors

# ============================================================================
# KEYWORDS (USED FOR LLM PROMPT CONTEXT)
# Keep these specific; overly broad terms will cause false positives.
# ============================================================================
KEYWORDS = [
    # Supply chain and logistics
    "supply chain",
    "logistics",
    "shipping",
    "freight",
    "cargo",
    "container",
    "port",
    "maritime",
    "trade",
    
    # Disruptions and delays
    "disruption",
    "delay",
    "strike",
    "closure",
    "backlog",
    "shortage",
    
    # Manufacturing and production
    "manufacturing",
    "production",
    "factory",
    "plant",
    
    # Economic indicators
    "economy",
    "economic",
    "inflation",
    "recession",
    "gdp",
    
    # Business and finance
    "business",
    "market",
    "stock",
    "financial",
    "investment",
    
    # Technology and innovation
    "technology",
    "innovation",
    "digital",
    "ai",
    "artificial intelligence",
    "automation",
]
