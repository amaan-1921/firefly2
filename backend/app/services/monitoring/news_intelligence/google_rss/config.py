"""
Configuration for Google RSS Feed Ingestion Agent
Supply Chain focused keyword filtering with strict relevance rules
"""

# ============================================================================
# DISRUPTION KEYWORDS
# These are the primary keywords that signal potential supply chain issues.
# An article MUST contain at least one of these to be considered relevant.
# ============================================================================
DISRUPTION_KEYWORDS = [
    # Port-related
    "port congestion",
    "port strike",
    "port closure",
    "port disruption",
    "port labor",
    "port dispute",
    
    # Shipping-related
    "shipping delay",
    "shipping disruption",
    "shipping lane",
    "cargo delay",
    "container backlog",
    "maritime incident",
    
    # Logistics-related
    "logistics disruption",
    "supply chain disruption",
    "supply disruption",
    "logistics delay",
    "freight backlog",
    
    # Manufacturing/Production
    "factory shutdown",
    "production halt",
    "manufacturing shutdown",
    "production disruption",
    
    # Labor
    "strike",  # Followed by more specific validation
    "labor dispute",
    "labor action",
]

# ============================================================================
# ENTITY KEYWORDS
# These represent logistics entities and locations.
# An article MUST mention at least one disruption keyword AND at least one entity.
# ============================================================================
LOGISTICS_ENTITIES = {
    "major_ports": [
        # Container ports
        "port of shanghai",
        "port of rotterdam",
        "port of singapore",
        "port of hamburg",
        "port of los angeles",
        "port of long beach",
        "port of dubai",
        "port of hong kong",
        "port of shenzhen",
        "port of busan",
        "port of kaohsiung",
        "port of amsterdam",
        "port of antwerp",
        "port of hong kong",
        "port of new york",
        "port of savannah",
        "port of jeddah",
        # Generic port references
        "port", "container port", "cargo port", "shipping port",
        "maritime port", "seaport", "port authority",
    ],
    "shipping_routes": [
        "suez canal",
        "panama canal",
        "strait of malacca",
        "english channel",
        "strait of hormuz",
        "shipping route",
        "trade route",
        "container route",
        "asia-europe",
        "trans-pacific",
    ],
    "logistics_hubs": [
        "logistics hub",
        "distribution center",
        "warehouse",
        "logistics facility",
        "terminal",
        "container terminal",
        "cargo terminal",
        "logistics park",
        "supply hub",
    ],
    "regions_suppliers": [
        # Major manufacturing regions
        "china", "southeast asia", "vietnam", "thailand", "indonesia",
        "india", "mexico", "germany", "japan", "south korea",
        # Specific cities/areas
        "shenzhen", "shanghai", "dongguan", "long beach", "rotterdam",
        "singapore", "dubai", "hamburg",
    ]
}

# ============================================================================
# FALSE POSITIVE PATTERNS
# These prevent articles about unrelated topics from being included.
# ============================================================================
FALSE_POSITIVE_PATTERNS = [
    # Sports (not supply chain)
    "nfl", "nba", "nhl", "mlb", "fifa", "soccer", "football", "basketball",
    "sports", "game", "season", "draft", "playoff", "league",
    
    # Entertainment (not supply chain)
    "movie", "film", "cinema", "actor", "actress", "oscar", "emmy",
    "golden globe", "television", "tv show", "netflix", "streaming",
    "music", "concert", "album", "artist", "celebrity",
    
    # Gaming (not supply chain)
    "video game", "game", "playstation", "xbox", "nintendo", "steam",
    "esports", "gaming",
    
    # Political opinion/commentary (not direct supply chain events)
    "opinion", "column", "editorial", "analysis", "commentary",
    "political", "election", "campaign", "vote", "congress", "senate",
    
    # General economic/policy (unless directly tied to disruption)
    "gdp", "inflation", "interest rate", "fed chairman", "central bank",
    "tariff policy", "trade deal",  # Generic policy, not disruption events
    
    # Stock market/finance (not supply chain disruption)
    "stock market", "nasdaq", "dow jones", "s&p 500", "ipo", "merger",
    "acquisition", "earnings", "quarterly results", "profit",
    
    # General news about regulation/policy without supply chain impact
    "regulatory", "compliance", "audit", "investigation", "lawsuit",
    
    # Health/medical (unless affecting supply chain)
    "covid", "pandemic", "vaccine", "disease", "measles", "outbreak",
    "health crisis", "epidemic",
]

# ============================================================================
# GOOGLE RSS FEED URLS
# Include business news and supply chain specific searches
# ============================================================================
FEED_URLS = [
    "https://news.google.com/rss?gl=US&ceid=US:en&topic=b",  # Business news
    # Supply chain and logistics specific Google News searches
    "https://news.google.com/rss/search?q=port+congestion&hl=en&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=shipping+delay&hl=en&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=logistics+disruption&hl=en&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=port+strike&hl=en&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=supply+chain&hl=en&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=container+shortage&hl=en&gl=US&ceid=US:en",
]

# ============================================================================
# POLLING CONFIGURATION
# ============================================================================
POLLING_WINDOW_DAYS = 300  # Lookback duration in days

# ============================================================================
# OUTPUT CONFIGURATION
# ============================================================================
OUTPUT_PATH = "test_output"  # Base output directory
