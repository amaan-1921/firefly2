from datetime import datetime


class Shipment:
    """
    Normalized internal representation of a shipment.

    This class represents shipment data after it has been
    normalized from ERP systems or carrier APIs.
    """

    def __init__(
        self,
        shipment_id: str,
        carrier: str,
        route_type: str,  # air / road / sea
        last_event_time: datetime,
        last_event_type: str,
        origin: str,
        destination: str,
    ):
        self.shipment_id = shipment_id
        self.carrier = carrier
        self.route_type = route_type
        self.last_event_time = last_event_time
        self.last_event_type = last_event_type
        self.origin = origin
        self.destination = destination


class StallSignal:
    """
    Enriched output produced by the Shipment Stall Agent.

    This represents the agent's judgement about a shipment,
    not the shipment data itself.
    """

    def __init__(
        self,
        shipment_id: str,
        stalled: bool,
        delay_hours: float,
        expected_interval_hours: int,
        severity: str,
        confidence: float,
        explanation: str,
    ):
        self.shipment_id = shipment_id
        self.stalled = stalled
        self.delay_hours = delay_hours
        self.expected_interval_hours = expected_interval_hours
        self.severity = severity
        self.confidence = confidence
        self.explanation = explanation
