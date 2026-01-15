from datetime import datetime
from .models import Shipment


def normalize_raw_event(raw_event: dict) -> Shipment:
    """
    Convert a raw ERP / carrier shipment event into a normalized Shipment object.

    This function isolates external schema differences so the rest of the
    system can work with a clean, consistent data model.
    """

    return Shipment(
        shipment_id=raw_event["shipmentId"],
        carrier=raw_event.get("carrier", "UNKNOWN"),
        route_type=raw_event.get("routeType", "road"),
        last_event_time=datetime.fromisoformat(raw_event["lastEventTime"]),
        last_event_type=raw_event.get("lastEventType", "UNKNOWN"),
        origin=raw_event.get("origin", "UNKNOWN"),
        destination=raw_event.get("destination", "UNKNOWN"),
    )
