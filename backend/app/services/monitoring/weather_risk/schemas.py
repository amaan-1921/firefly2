"""Pydantic schemas for Weather Risk Agent."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class MonitoringSignal(BaseModel):
    """
    Standardized monitoring signal for detected weather risks.
    
    This signal represents a detected weather risk and is designed to be
    passed to other agents or orchestration logic without writing to any
    database or sending notifications directly.
    """
    
    signalType: Literal["WEATHER_DISRUPTION"] = Field(
        default="WEATHER_DISRUPTION",
        description="Type of monitoring signal"
    )
    sourceType: Literal["External"] = Field(
        default="External",
        description="Source of the signal (external data provider)"
    )
    sourceReference: str = Field(
        ...,
        description="Location name where weather risk was detected"
    )
    severityLevel: Literal["Medium", "High"] = Field(
        ...,
        description="Severity level of the weather risk"
    )
    confidenceScore: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score of the detected risk"
    )
    expectedImpactWindow: str = Field(
        ...,
        description="Expected time window for the weather impact"
    )
    evidence: str = Field(
        ...,
        description="Human-readable explanation of the detected risk"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="UTC timestamp when the signal was generated"
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "signalType": "WEATHER_DISRUPTION",
                "sourceType": "External",
                "sourceReference": "Chennai",
                "severityLevel": "High",
                "confidenceScore": 0.9,
                "expectedImpactWindow": "1–3 days",
                "evidence": "Official weather alert detected: storm warning",
                "timestamp": "2026-01-15T12:30:00"
            }
        }


class WeatherCheckResponse(BaseModel):
    """Response model for the weather check endpoint."""
    
    signals: list[MonitoringSignal] = Field(
        default_factory=list,
        description="List of detected weather risks"
    )
    locationCount: int = Field(
        ...,
        description="Number of locations checked"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp of the check"
    )
