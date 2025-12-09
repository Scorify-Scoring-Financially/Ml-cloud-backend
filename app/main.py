from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.backend.db import  Base, engine
from app.ml.ml_service import run_batch_job
from apscheduler.schedulers.background import BackgroundScheduler
import logging

from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor


logging.basicConfig(level=logging.INFO)


# Scheduler instance
scheduler = BackgroundScheduler()
@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    print("✅ STARTUP TRIGGERED")

    # Run once at startup
    run_batch_job()

    # Start scheduler (runs every 3 minutes)
    scheduler.add_job(run_batch_job, "interval", minutes=24)
    scheduler.start()

    try:
        yield  # <-- FastAPI will serve requests here
    finally:
        # Optional cleanup (shutdown scheduler)
        scheduler.shutdown()
        print("🛑 Scheduler stopped")

app = FastAPI(title="Scorify Backend", lifespan=lifespan)

