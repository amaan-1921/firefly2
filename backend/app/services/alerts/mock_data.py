"""
Mock data for the Alerts Module.

Generates realistic MonitoringSignal objects simulating signals from different agents.
This is used for MVP testing when real monitoring data is not available.
"""

from datetime import datetime, timedelta
from typing import List
from .schemas import MonitoringSignal, SeverityLevel, SignalType, SourceType


def get_mock_signals() -> List[MonitoringSignal]:
    """
    Generate realistic mock signals for testing the Alerts Module.
    
    Returns:
        List of MonitoringSignal objects simulating various scenarios
    """
    base_time = datetime.utcnow()
    
    signals = [
        # Weather Disruption in Chennai
        MonitoringSignal(
            signalType=SignalType.WEATHER_DISRUPTION,
            sourceType=SourceType.WEATHER_AGENT,
            sourceReference="REGION-CHENNAI",
            severityLevel=SeverityLevel.HIGH,
            confidenceScore=0.92,
            expectedImpactWindow="6 hours",
            evidence="Severe thunderstorm warning issued for Chennai region. Wind speeds expected to reach 40-50 km/h with heavy rainfall.",
            timestamp=base_time
        ),
        
        # PO Delay Risk for PO-123
        MonitoringSignal(
            signalType=SignalType.PO_DELAY_RISK,
            sourceType=SourceType.PO_AGENT,
            sourceReference="PO-123",
            severityLevel=SeverityLevel.MEDIUM,
            confidenceScore=0.85,
            expectedImpactWindow="2 days",
            evidence="Supplier port delays detected. Expected delivery is at risk due to port congestion in Chennai.",
            timestamp=base_time + timedelta(minutes=5)
        ),
        
        # Supplier Performance Drop
        MonitoringSignal(
            signalType=SignalType.SUPPLIER_PERFORMANCE_DROP,
            sourceType=SourceType.SUPPLIER_AGENT,
            sourceReference="SUP-45",
            severityLevel=SeverityLevel.MEDIUM,
            confidenceScore=0.78,
            expectedImpactWindow="1 week",
            evidence="Supplier SUP-45 on-time delivery rate dropped to 65% this month, down from 92% average.",
            timestamp=base_time + timedelta(minutes=10)
        ),
        
        # News Risk - Supply Chain Disruption
        MonitoringSignal(
            signalType=SignalType.NEWS_RISK,
            sourceType=SourceType.NEWS_AGENT,
            sourceReference="REGION-SOUTHEAST-ASIA",
            severityLevel=SeverityLevel.LOW,
            confidenceScore=0.62,
            expectedImpactWindow="3 days",
            evidence="News report: Port workers in Southeast Asia announce potential strike action starting next week.",
            timestamp=base_time + timedelta(minutes=15)
        ),
        
        # Additional PO Risk - Related to PO-123
        MonitoringSignal(
            signalType=SignalType.PO_DELAY_RISK,
            sourceType=SourceType.PO_AGENT,
            sourceReference="PO-123",
            severityLevel=SeverityLevel.HIGH,
            confidenceScore=0.88,
            expectedImpactWindow="3 days",
            evidence="Updated: Supplier forecast shows 2-3 day delay due to weather impact on production facility in Chennai.",
            timestamp=base_time + timedelta(minutes=20)
        ),
    ]
    
    return signals
