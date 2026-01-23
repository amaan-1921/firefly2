"""
Alerts Module API layer.

Exposes FastAPI endpoints for the Alerts Module.
"""

from fastapi import APIRouter, HTTPException
from typing import List
from .schemas import Alert
from .pipeline import run_alerts_pipeline

# Create a router for alerts endpoints
router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/run-mock", response_model=List[Alert])
async def run_mock_alerts_pipeline():
    """
    Execute the full alerts pipeline using mock data.
    
    This endpoint:
    - Loads mock MonitoringSignal objects
    - Runs them through the complete pipeline
    - Returns generated Alert objects
    
    Returns:
        List of Alert objects derived from mock signals
        
    Raises:
        HTTPException: If pipeline execution fails
    """
    try:
        alerts = run_alerts_pipeline()
        return alerts
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Pipeline execution failed: {str(e)}"
        )
