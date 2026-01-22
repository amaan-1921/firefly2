from datetime import datetime
from .config import SEVERITY_THRESHOLDS


def calculate_delay_hours(last_event_time: datetime, current_time: datetime) -> float:
    """
    Calculate how many hours have passed since the last shipment event.
    """
    delta = current_time - last_event_time
    return delta.total_seconds() / 3600


def classify_severity(delay_hours: float, expected_interval_hours: int) -> str:
    """
    Classify severity based on how much the expected update interval
    has been breached.
    """
    ratio = delay_hours / expected_interval_hours

    if ratio < SEVERITY_THRESHOLDS["warning"]:
        return "normal"
    elif ratio < SEVERITY_THRESHOLDS["high"]:
        return "warning"
    elif ratio < SEVERITY_THRESHOLDS["critical"]:
        return "high"
    else:
        return "critical"
