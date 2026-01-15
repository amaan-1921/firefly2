from datetime import datetime, timedelta


def generate_mock_shipments():
    """
    Generate mock shipment events simulating ERP / carrier data.

    This data intentionally represents different real-world cases:
    - A healthy shipment
    - A slightly delayed shipment (warning)
    - A severely stalled shipment (critical)
    """

    now = datetime.utcnow()

    return [
        # 1️⃣ Healthy shipment (within expected update window)
        {
            "shipmentId": "SHP_HEALTHY_001",
            "carrier": "DHL",
            "routeType": "road",
            "lastEventTime": (now - timedelta(hours=8)).isoformat(),
            "lastEventType": "Arrived at Hub",
            "origin": "Hamburg",
            "destination": "Berlin",
        },

        # 2️⃣ Warning-level delay (late but not critical)
        {
            "shipmentId": "SHP_WARNING_002",
            "carrier": "FedEx",
            "routeType": "road",
            "lastEventTime": (now - timedelta(hours=20)).isoformat(),
            "lastEventType": "Departed Hub",
            "origin": "Paris",
            "destination": "Lyon",
        },

        # 3️⃣ Critical stall (far beyond expected update window)
        {
            "shipmentId": "SHP_CRITICAL_003",
            "carrier": "Maersk",
            "routeType": "sea",
            "lastEventTime": (now - timedelta(hours=120)).isoformat(),
            "lastEventType": "Loaded on Vessel",
            "origin": "Shanghai",
            "destination": "Rotterdam",
        },
    ]
