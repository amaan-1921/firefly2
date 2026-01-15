"""
Configuration for the Shipment Stall Agent.

This file defines business assumptions and thresholds.
There must be NO business logic in this file.
"""


# Expected carrier update intervals (in hours) by route type
# These represent what is considered "normal" behavior.
EXPECTED_UPDATE_INTERVALS = {
    "air": 6,     # Air shipments update frequently
    "road": 12,   # Road shipments update moderately
    "sea": 24     # Sea shipments update slowly
}


# Severity thresholds expressed as ratios:
# (actual delay hours) / (expected update interval)
SEVERITY_THRESHOLDS = {
    "warning": 1.5,
    "high": 2.5,
    "critical": 4.0
}
