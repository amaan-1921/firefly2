"""
Configuration for Google RSS Feed Ingestion Agent
Supply Chain focused keyword filtering
"""

# Supply Chain Keywords
SUPPLY_CHAIN_KEYWORDS = {
    "locations": [
        "port", "harbor", "terminal", "warehouse", "distribution",
        "logistics hub", "supply hub", "facility", "plant",
        "Shanghai", "Rotterdam", "Singapore", "Hamburg", "Los Angeles",
        "Long Beach", "Dubai", "Hong Kong"
    ],
    "materials": [
        "semiconductor", "chip", "microchip", "lithium", "cobalt",
        "rare earth", "aluminum", "steel", "copper", "container",
        "freight", "cargo", "shipment", "goods"
    ],
    "ports": [
        "port", "port strike", "port closure", "port congestion",
        "port disruption", "shipping delay", "maritime", "blockade"
    ],
    "supply_chain_events": [
        "disruption", "delay", "bottleneck", "shortage", "outage",
        "blockade", "strike", "closure", "accident", "incident",
        "congestion", "risk", "threat", "damage", "loss"
    ]
}

# More specific relevance keywords (multi-word phrases work better)
SUPPLY_CHAIN_RELEVANCE_KEYWORDS = [
    # Multi-word phrases (best)
    "supply chain", "supply-chain",
    "port strike", "port closure", "port congestion", "port disruption",
    "shipping lane", "shipping route", "shipping delay",
    "cargo ship", "freight transport", "freight rate",
    "customs delay", "trade route",
    "warehouse shortage", "inventory shortage",
    "manufacturing delay", "production halt",
    "component shortage", "delivery delay", "shipment delay",
    
    # Single words that are highly specific (add back carefully)
    "logistics", "procurement", "tariff", "semiconductor shortage",
    "container ship", "bottleneck"
]
# Google RSS feed URLs for ingestion
FEED_URLS = [
    "https://news.google.com/rss?gl=US&ceid=US:en&topic=b",  # Business news
]

# Polling configuration
POLLING_WINDOW_DAYS = 30  # Lookback duration in days

# Output configuration
OUTPUT_PATH = "test_output"  # Base output directory
