from fastapi import FastAPI
from app.routers.mahajana_sampatha import router as mahajana_router
import logging
import os

from app.core import scheduler as app_scheduler

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="NLB Lottery API")
app.include_router(mahajana_router)


@app.on_event("startup")
def startup_event():
    # Prevent double scheduler in reload mode
    if os.environ.get("RUN_MAIN") == "true":
        app_scheduler.start_scheduler()


@app.on_event("shutdown")
def shutdown_event():
    app_scheduler.shutdown_scheduler()
