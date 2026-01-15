"""Weather Risk Agent for detecting severe weather conditions."""

from datetime import datetime
from typing import Any

from config import (
    ALERT_KEYWORDS,
    CONFIDENCE_SCORES,
    EXPECTED_IMPACT_WINDOW,
    MONITORED_LOCATIONS,
    SEVERITY_THRESHOLDS,
)
from client import OpenWeatherMapClient
from schemas import MonitoringSignal


class WeatherRiskAgent:
    """
    Agent responsible for detecting severe weather risks.
    
    This agent:
    - Fetches weather data from OpenWeatherMap API
    - Evaluates weather conditions against defined thresholds
    - Returns standardized MonitoringSignal objects for detected risks
    - Does NOT write to databases, send notifications, or make decisions
    """
    
    def __init__(self, api_key: str):
        """
        Initialize the Weather Risk Agent.
        
        Args:
            api_key: OpenWeatherMap API key
        """
        self.client = OpenWeatherMapClient(api_key=api_key)
        self.locations = MONITORED_LOCATIONS
    
    async def evaluate(self) -> list[MonitoringSignal]:
        """
        Evaluate weather conditions for all monitored locations.
        
        Returns:
            List of MonitoringSignal objects for detected weather risks.
            Empty list if no risks detected.
        """
        signals = []
        
        for location in self.locations:
            # Fetch weather data
            raw_data = await self.client.fetch_weather_data(location)
            if raw_data is None:
                continue
            
            # Parse weather data
            weather_data = self.client.parse_weather_data(raw_data, location)
            
            # Detect weather risks
            risk_signal = self._detect_weather_risk(weather_data)
            if risk_signal:
                signals.append(risk_signal)
        
        return signals
    
    def _detect_weather_risk(
        self,
        weather_data: dict[str, Any]
    ) -> MonitoringSignal | None:
        """
        Detect weather risks based on OpenWeatherMap data.
        
        Uses two evaluation paths:
        1. Official weather alerts (high confidence)
        2. Threshold-based evaluation (medium confidence)
        
        Args:
            weather_data: Parsed weather data from OpenWeatherMap
            
        Returns:
            MonitoringSignal if risk detected, None otherwise
        """
        location_name = weather_data["location_name"]
        
        # Check for official weather alerts first
        alert_signal = self._check_official_alerts(weather_data)
        if alert_signal:
            return alert_signal
        
        # Check threshold-based risks
        threshold_signal = self._check_thresholds(weather_data)
        if threshold_signal:
            return threshold_signal
        
        return None
    
    def _check_official_alerts(
        self,
        weather_data: dict[str, Any]
    ) -> MonitoringSignal | None:
        """
        Check for official weather alerts in the data.
        
        High severity signals are generated if official alerts match
        known severe weather keywords.
        
        Args:
            weather_data: Parsed weather data
            
        Returns:
            MonitoringSignal if alert detected, None otherwise
        """
        location_name = weather_data["location_name"]
        alerts = weather_data.get("alerts", [])
        weather_description = (weather_data.get("weather_description") or "").lower()
        weather_main = (weather_data.get("weather_main") or "").lower()
        
        # Check for keyword matches in alerts
        for alert in alerts:
            event = alert.get("event", "").lower()
            for keyword in ALERT_KEYWORDS:
                if keyword in event:
                    return MonitoringSignal(
                        sourceReference=location_name,
                        severityLevel="High",
                        confidenceScore=CONFIDENCE_SCORES["alert_present"],
                        expectedImpactWindow=EXPECTED_IMPACT_WINDOW,
                        evidence=f"Official weather alert detected: {alert.get('event', 'Unknown')}. "
                                f"Description: {alert.get('description', 'N/A')}",
                        timestamp=datetime.utcnow(),
                    )
        
        # Check for severe weather keywords in description
        for keyword in ["storm", "cyclone", "hurricane", "typhoon", "extreme"]:
            if keyword in weather_description or keyword in weather_main:
                return MonitoringSignal(
                    sourceReference=location_name,
                    severityLevel="High",
                    confidenceScore=CONFIDENCE_SCORES["alert_present"],
                    expectedImpactWindow=EXPECTED_IMPACT_WINDOW,
                    evidence=f"Severe weather condition detected: {weather_data.get('weather_main')} - "
                            f"{weather_data.get('weather_description')}",
                    timestamp=datetime.utcnow(),
                )
        
        return None
    
    def _check_thresholds(
        self,
        weather_data: dict[str, Any]
    ) -> MonitoringSignal | None:
        """
        Evaluate weather conditions against defined thresholds.
        
        Medium severity signals are generated if rainfall exceeds 50 mm
        or wind speed exceeds 40 km/h.
        
        Args:
            weather_data: Parsed weather data
            
        Returns:
            MonitoringSignal if threshold exceeded, None otherwise
        """
        location_name = weather_data["location_name"]
        rainfall_mm = weather_data.get("rainfall_mm", 0)
        wind_speed_kmh = weather_data.get("wind_speed_kmh")
        
        rainfall_threshold = SEVERITY_THRESHOLDS["rainfall_threshold_mm"]
        wind_threshold = SEVERITY_THRESHOLDS["wind_speed_threshold_kmh"]
        
        evidence_parts = []
        
        # Check rainfall
        if rainfall_mm >= rainfall_threshold:
            evidence_parts.append(f"Heavy rainfall: {rainfall_mm:.1f} mm (threshold: {rainfall_threshold} mm)")
        
        # Check wind speed
        if wind_speed_kmh and wind_speed_kmh >= wind_threshold:
            evidence_parts.append(f"High wind speed: {wind_speed_kmh:.1f} km/h (threshold: {wind_threshold} km/h)")
        
        # Return signal if any threshold exceeded
        if evidence_parts:
            return MonitoringSignal(
                sourceReference=location_name,
                severityLevel="Medium",
                confidenceScore=CONFIDENCE_SCORES["threshold_based"],
                expectedImpactWindow=EXPECTED_IMPACT_WINDOW,
                evidence=". ".join(evidence_parts) + ". " + 
                        f"Weather: {weather_data.get('weather_main')} - {weather_data.get('weather_description')}",
                timestamp=datetime.utcnow(),
            )
        
        return None
