"""OpenWeatherMap API client for fetching weather data."""

import os
from typing import Any, Optional

import httpx
from dotenv import load_dotenv

from config import Location

# Load environment variables from .env file
load_dotenv()


class OpenWeatherMapClient:
    """
    Client for interacting with OpenWeatherMap API.
    
    Fetches weather data for given locations using the One Call API.
    """
    
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
    ALERTS_URL = "https://api.openweathermap.org/data/3.0/stations"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the OpenWeatherMap API client.
        
        Args:
            api_key: OpenWeatherMap API key. If not provided, reads from
                    OPENWEATHER_API_KEY environment variable.
        """
        self.api_key = api_key or os.getenv("OPENWEATHER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenWeatherMap API key must be provided or set in "
                "OPENWEATHER_API_KEY environment variable"
            )
    
    async def fetch_weather_data(self, location: Location) -> Optional[dict[str, Any]]:
        """
        Fetch current weather data for a location.
        
        Args:
            location: Location object with latitude and longitude
            
        Returns:
            Dictionary containing weather data or None if request fails
        """
        params = {
            "lat": location.latitude,
            "lon": location.longitude,
            "appid": self.api_key,
            "units": "metric",  # Use metric units for rainfall and temperature
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.BASE_URL,
                    params=params,
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
        except httpx.RequestError as e:
            print(f"Error fetching weather data for {location.name}: {e}")
            return None
        except httpx.HTTPStatusError as e:
            print(f"HTTP error fetching weather for {location.name}: {e}")
            return None
    
    def parse_weather_data(
        self,
        data: dict[str, Any],
        location: Location
    ) -> dict[str, Any]:
        """
        Parse OpenWeatherMap API response into structured data.
        
        Args:
            data: Raw API response
            location: Location object for reference
            
        Returns:
            Dictionary with parsed weather metrics
        """
        parsed = {
            "location_name": location.name,
            "latitude": location.latitude,
            "longitude": location.longitude,
            "temperature": data.get("main", {}).get("temp"),
            "feels_like": data.get("main", {}).get("feels_like"),
            "humidity": data.get("main", {}).get("humidity"),
            "pressure": data.get("main", {}).get("pressure"),
            "wind_speed_ms": data.get("wind", {}).get("speed"),  # m/s
            "wind_gust_ms": data.get("wind", {}).get("gust"),  # m/s (optional)
            "cloudiness": data.get("clouds", {}).get("all"),
            "weather_main": data.get("weather", [{}])[0].get("main"),
            "weather_description": data.get("weather", [{}])[0].get("description"),
            "rainfall_mm": data.get("rain", {}).get("1h", 0),  # 1-hour rainfall
            "alerts": data.get("alerts", []),  # OpenWeatherMap alerts (if any)
            "timestamp": data.get("dt"),
        }
        
        # Convert wind speed from m/s to km/h
        if parsed["wind_speed_ms"] is not None:
            parsed["wind_speed_kmh"] = parsed["wind_speed_ms"] * 3.6
        else:
            parsed["wind_speed_kmh"] = None
            
        if parsed["wind_gust_ms"] is not None:
            parsed["wind_gust_kmh"] = parsed["wind_gust_ms"] * 3.6
        else:
            parsed["wind_gust_kmh"] = None
        
        return parsed
