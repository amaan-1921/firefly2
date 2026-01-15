from .normalizer import normalize_raw_event
from .detector import detect_stall


def run_shipment_stall_agent(raw_events):
    """
    Run the Shipment Stall Agent on a list of raw shipment events.

    This function orchestrates normalization and detection,
    returning only shipments that are considered stalled.
    """

    stall_signals = []

    for raw_event in raw_events:
        # Convert raw ERP / carrier data into internal model
        shipment = normalize_raw_event(raw_event)

        # Detect stall for this shipment
        signal = detect_stall(shipment)

        # Only return actionable signals
        if signal.stalled:
            stall_signals.append(signal)

    return stall_signals
