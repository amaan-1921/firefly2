from datetime import datetime

from .models import StallSignal
from .config import EXPECTED_UPDATE_INTERVALS
from .rules import calculate_delay_hours, classify_severity
from .confidence import calculate_confidence


def detect_stall(shipment):
    """
    Detect whether a single shipment is potentially stalled.

    This function combines configuration, domain rules, and
    confidence scoring to produce an enriched stall signal.
    """

    # Current time (UTC)
    now = datetime.utcnow()

    # Determine expected update interval based on route type
    expected_interval_hours = EXPECTED_UPDATE_INTERVALS.get(
        shipment.route_type, 12
    )

    # Calculate how long it has been since the last update
    delay_hours = calculate_delay_hours(
        shipment.last_event_time, now
    )

    # Classify severity based on delay vs expected interval
    severity = classify_severity(
        delay_hours, expected_interval_hours
    )

    # Decide whether this counts as a stall
    stalled = severity != "normal"

    # Calculate confidence score
    confidence = calculate_confidence(
        delay_hours, expected_interval_hours
    )

    # Human-readable explanation for dashboards / alerts
    explanation = (
        f"No carrier update for {delay_hours:.1f} hours "
        f"(expected every {expected_interval_hours} hours). "
        f"Last event: {shipment.last_event_type}"
    )

    return StallSignal(
        shipment_id=shipment.shipment_id,
        stalled=stalled,
        delay_hours=delay_hours,
        expected_interval_hours=expected_interval_hours,
        severity=severity,
        confidence=confidence,
        explanation=explanation,
    )
