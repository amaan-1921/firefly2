"""Configuration for Weather Risk Agent."""

from dataclasses import dataclass


@dataclass
class Location:
    """Represents a location to monitor."""
    name: str
    latitude: float
    longitude: float


# Hardcoded locations to monitor
MONITORED_LOCATIONS = [
    Location(name="Chennai", latitude=13.0827, longitude=80.2707),
    Location(name="Mumbai", latitude=19.0760, longitude=72.8777),
]

# Severity thresholds
SEVERITY_THRESHOLDS = {
    "rainfall_threshold_mm": 5,  # mm (lowered for testing - will be adjusted later)
    "wind_speed_threshold_kmh": 5,  # km/h (lowered for testing - will be adjusted later)
}

# Alert keywords for official weather alerts
ALERT_KEYWORDS = [
    "storm",
    "cyclone",
    "hurricane",
    "typhoon",
    "extreme",
    "warning",
    "alert",
    "severe",
]

# Expected impact window
EXPECTED_IMPACT_WINDOW = "1–3 days"

# Confidence scores
CONFIDENCE_SCORES = {
    "alert_present": 0.9,
    "threshold_based": 0.7,
}
