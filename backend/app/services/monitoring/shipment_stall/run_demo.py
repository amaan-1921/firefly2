from .mock_data import generate_mock_shipments
from .service import run_shipment_stall_agent


def main():
    """
    Demo runner for the Shipment Stall Agent.

    This function simulates incoming shipment data,
    runs the agent, and prints detected stall alerts.
    """

    # Generate mock ERP / carrier shipment events
    raw_shipments = generate_mock_shipments()

    # Run the shipment stall agent
    stall_signals = run_shipment_stall_agent(raw_shipments)

    print("\n🚨 Shipment Stall Alerts\n" + "-" * 30)

    if not stall_signals:
        print("No stalled shipments detected.")
        return

    for signal in stall_signals:
        print(
            f"\nShipment ID: {signal.shipment_id}"
            f"\nSeverity: {signal.severity.upper()}"
            f"\nDelay: {signal.delay_hours:.1f} hours"
            f"\nExpected Interval: {signal.expected_interval_hours} hours"
            f"\nConfidence: {signal.confidence}"
            f"\nExplanation: {signal.explanation}"
        )


if __name__ == "__main__":
    main()
