"""
FastAPI application entry point.

Initializes and configures the main FastAPI app with all service routers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.services.alerts.api import router as alerts_router
from app.services.monitoring.news_intelligence.agent_test.router import router as news_intelligence_router

# Initialize FastAPI app
app = FastAPI(
    title="Alerts Module API",
    description="Supply chain alerts pipeline API",
    version="1.0.0"
)

# Add CORS middleware for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(alerts_router)
app.include_router(news_intelligence_router, prefix="/monitoring")


@app.get("/")
async def root():
    """Root endpoint returning API info."""
    return {
        "message": "Alerts Module API",
        "version": "1.0.0",
        "endpoints": {
            "alerts": {
                "mock_alerts": "/alerts/run-mock",
                "jsonl_alerts": "/alerts/run-from-jsonl"
            },
            "news_intelligence": {
                "articles": "/monitoring/news-intelligence/articles",
                "articles_count": "/monitoring/news-intelligence/articles/count"
            }
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
