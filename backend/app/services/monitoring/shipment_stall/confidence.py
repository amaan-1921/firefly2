def calculate_confidence(delay_hours: float, expected_interval_hours: int) -> float:
    """
    Calculate a confidence score indicating how likely it is that
    a shipment is genuinely stalled.

    The confidence increases monotonically as the delay grows
    relative to the expected update interval.

    Returns a value between 0.0 and 1.0.
    """

    ratio = delay_hours / expected_interval_hours

    if ratio < 1.0:
        return 0.2
    elif ratio < 2.0:
        return 0.5
    elif ratio < 3.0:
        return 0.75
    else:
        return 0.9
