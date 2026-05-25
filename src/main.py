"""
Integration Engineering Platform - FastAPI Application
SPEC.md Section 5: REST API on Azure AKS
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import (
    workflows_router,
    executions_router,
    connectors_router,
    health_router,
)
from scheduler import get_scheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    scheduler = get_scheduler()
    scheduler.start()
    logger.info("Integration Engineering Platform started")

    yield

    # Shutdown
    scheduler.stop()
    logger.info("Integration Engineering Platform stopped")


app = FastAPI(
    title="Integration Engineering Platform",
    description="Workflow orchestration for cloud-native system integrations",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(workflows_router)
app.include_router(executions_router)
app.include_router(connectors_router)
app.include_router(health_router)


@app.get("/")
async def root():
    return {
        "name": "Integration Engineering Platform",
        "version": "1.0.0",
        "engines": ["argo", "temporal", "airflow"],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)