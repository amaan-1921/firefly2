"""FastAPI endpoints for Weather Risk Agent."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException

from .agent import WeatherRiskAgent
from .schemas import MonitoringSignal, WeatherCheckResponse

# Create router for weather risk endpoints
router = APIRouter(prefix="/monitoring/weather", tags=["weather-risk"])


def get_weather_agent(api_key: str = None) -> WeatherRiskAgent:
    """
    Dependency to create Weather Risk Agent instance.
    
    Args:
        api_key: OpenWeatherMap API key (will be injected from config)
        
    Returns:
        Initialized WeatherRiskAgent instance
    """
    # In a real application, api_key would be injected from FastAPI Depends
    # and loaded from environment or settings
    if api_key is None:
        raise HTTPException(
            status_code=500,
            detail="OpenWeatherMap API key not configured"
        )
    return WeatherRiskAgent(api_key=api_key)


@router.post(
    "/check",
    response_model=WeatherCheckResponse,
    summary="Check for weather risks",
    description="Triggers weather risk evaluation for all monitored locations and "
                "returns detected risks as MonitoringSignal objects."
)
async def check_weather_risks(
    agent: WeatherRiskAgent = Depends(get_weather_agent)
) -> WeatherCheckResponse:
    """
    Endpoint to manually trigger weather risk evaluation.
    
    This endpoint:
    - Fetches current weather data for all monitored locations
    - Evaluates weather conditions against defined thresholds
    - Returns a list of MonitoringSignal objects for detected risks
    
    The endpoint does NOT write to any database or send notifications.
    All detected signals are returned as structured data for further
    processing by orchestration logic.
    
    Returns:
        WeatherCheckResponse containing list of detected signals
        and metadata about the check
        
    Raises:
        HTTPException: If weather data cannot be fetched or processed
    """
    try:
        signals = await agent.evaluate()
        
        return WeatherCheckResponse(
            signals=signals,
            locationCount=len(agent.locations),
            timestamp=datetime.utcnow(),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during weather risk evaluation: {str(e)}"
        )


@router.get(
    "/health",
    response_model=dict,
    summary="Health check endpoint",
    description="Returns the status of the Weather Risk Agent"
)
async def health_check() -> dict:
    """
    Health check endpoint for the Weather Risk Agent.
    
    Returns:
        Dictionary with status information
    """
    return {
        "status": "healthy",
        "service": "weather-risk-agent",
        "timestamp": datetime.utcnow().isoformat(),
    }
