"""
Alerts Module

A multi-layered system for processing monitoring signals and generating
human-facing alerts with appropriate urgency levels.

Pipeline: Ingestion → Aggregation → Qualification → Prioritization → Context Builder
"""

from .schemas import (
    MonitoringSignal,
    SeverityLevel,
    SignalType,
    SourceType,
    AlertPriority,
    RiskContext,
    Alert,
)
from .mock_data import get_mock_signals
from .pipeline import run_alerts_pipeline
from .api import router

__all__ = [
    "MonitoringSignal",
    "SeverityLevel",
    "SignalType",
    "SourceType",
    "AlertPriority",
    "RiskContext",
    "Alert",
    "get_mock_signals",
    "run_alerts_pipeline",
    "router",
]
