"""
Main FastAPI Application Entrypoint.
Initializes FastAPI instance, configures logging, CORS middleware, and includes API routers.
"""

import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as api_router

# Configure Application Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("cloud_cost_anomaly_detector")

app = FastAPI(
    title="Cloud Cost Anomaly Detector API",
    description="Backend API for cloud cost data validation, analysis, anomaly detection, forecasting, and recommendations.",
    version="1.0.0",
)

# Configure CORS Middleware from Environment
allowed_origins_env = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
allowed_origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Router
app.include_router(api_router)


@app.on_event("startup")
async def startup_event():
    logger.info("Cloud Cost Anomaly Detector API backend started successfully.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
