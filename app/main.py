from contextlib import asynccontextmanager
from fastapi import FastAPI
import logging

from app.core.scheduler import start_scheduler, shutdown_scheduler
from app.services.db import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(application: FastAPI):
    """Startup and shutdown lifecycle for the FastAPI app."""
    # Startup 
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error("Failed to initialize database: %s", e)

    start_scheduler()
    logger.info("Scheduler started")

    yield  # app is running

    # Shutdown
    shutdown_scheduler()


app = FastAPI(title="NLB Lottery API", lifespan=lifespan)


# ── Routers ──
from app.routers.mahajana_sampatha import router as mahajana_router  # noqa: E402

app.include_router(mahajana_router)


@app.get("/", tags=["health"])
def health_check():
    """Simple health-check endpoint."""
    return {"status": "ok", "service": "NLB Lottery API"}

