"""
Configuration for Web Scraping LLM Agent.

Defines predefined sources, LLM settings, search topics, and output paths.
"""

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
LLM_MAX_RETRIES = 5
LLM_INITIAL_BACKOFF_S = 2.0
LLM_MAX_BACKOFF_S = 120.0
LLM_BATCH_DELAY_S = 1.0
LLM_429_BACKOFF_MULTIPLIER = 2.0

# ============================================================================
# PREDEFINED SOURCES
# ============================================================================
SUPPLY_CHAIN_SOURCES = [
    "https://www.supplychaindive.com",
    "https://www.freightwaves.com",
    "https://www.porttechnology.org",
    "https://www.tradewindsnews.com",
    "https://www.joc.com",
    "https://www.supplychainbrain.com",
    "https://www.logisticsmgmt.com",
    "https://www.dcvelocity.com",
    "https://www.americanport.com",
    "https://www.portstrategy.com",
]

# ============================================================================
# SEARCH TOPICS
# ============================================================================
SEARCH_TOPICS = [
    # Supply chain disruptions
    "supply chain disruption",
    "port closure",
    "shipping delays",
    "trade updates",
    "maritime logistics",
    "container shortage",
    "freight delays",
    "port congestion",
    "supply chain crisis",
    "trade war impact",
    "shipping strike",
    "port backlog",
    "cargo delays",
    "logistics disruption",
    "international trade",
    
    # Natural disasters affecting supply chains
    "hurricane port closure",
    "earthquake factory shutdown",
    "flood supply chain",
    "wildfire logistics disruption",
    "natural disaster shipping",
    "typhoon port impact",
    "tsunami supply chain",
    "extreme weather logistics",
    
    # Strikes and shutdowns
    "port strike",
    "factory strike",
    "airport strike",
    "airline strike",
    "dock worker strike",
    "trucker strike",
    "factory shutdown",
    "port shutdown",
    "airport closure",
    "manufacturing shutdown",
    "plant closure",
    "labor strike supply chain",
    
    # Raw material shortages
    "raw material shortage",
    "commodity shortage",
    "material scarcity",
    "resource shortage",
    "input shortage",
    "component shortage",
    "steel shortage",
    "semiconductor shortage",
    "chip shortage",
    "mineral shortage",
    "energy shortage",
    "fuel shortage",
]

# ============================================================================
# KEYWORDS (USED FOR LLM RELEVANCE SCORING)
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
    "transportation",
    "distribution",
    
    # Disruptions and delays
    "disruption",
    "delay",
    "strike",
    "closure",
    "backlog",
    "shortage",
    "congestion",
    "shutdown",
    "halt",
    "suspension",
    "interruption",
    
    # Manufacturing and production
    "manufacturing",
    "production",
    "factory",
    "plant",
    "facility",
    "warehouse",
    
    # Natural disasters
    "hurricane",
    "typhoon",
    "earthquake",
    "flood",
    "wildfire",
    "tsunami",
    "storm",
    "natural disaster",
    "extreme weather",
    "climate event",
    
    # Strikes and labor issues
    "labor strike",
    "worker strike",
    "union strike",
    "dock strike",
    "airline strike",
    "trucker strike",
    "transportation strike",
    "industrial action",
    
    # Raw materials and commodities
    "raw material",
    "commodity",
    "resource",
    "material shortage",
    "component shortage",
    "semiconductor",
    "chip",
    "steel",
    "mineral",
    "energy",
    "fuel",
    "crude oil",
    "petroleum",
    
    # Ports and airports
    "airport",
    "airport closure",
    "airport shutdown",
    "aviation",
    "airline",
    "aircraft",
    "cargo plane",
    
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
]

# ============================================================================
# OUTPUT CONFIG
# ============================================================================
OUTPUT_FILE = "scraped_articles.jsonl"
TIME_WINDOW_DAYS = 30  # Days to look back for articles

# ============================================================================
# WEB SCRAPING CONFIG
# ============================================================================
SCRAPER_TIMEOUT_S = 30.0
SCRAPER_MAX_RETRIES = 3
SCRAPER_DELAY_BETWEEN_REQUESTS_S = 1.0
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# ============================================================================
# SEARCH ENGINE CONFIG
# ============================================================================
# Use googlesearch-python library (free, rate-limited)
USE_GOOGLE_SEARCH = True
GOOGLE_SEARCH_NUM_RESULTS = 10
GOOGLE_SEARCH_DELAY_S = 2.0  # Delay between searches to avoid rate limits

# Optional: Google Custom Search API (requires API key)
# Set GOOGLE_CSE_API_KEY and GOOGLE_CSE_ID in .env if using
GOOGLE_CSE_API_KEY_ENV = "GOOGLE_CSE_API_KEY"
GOOGLE_CSE_ID_ENV = "GOOGLE_CSE_ID"
