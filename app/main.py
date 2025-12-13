from fastapi import FastAPI, Header, HTTPException
from contextlib import asynccontextmanager
from app.backend.db import Base, engine
from app.ml.ml_service import run_batch_job
import os

API_KEY = os.getenv("BATCH_API_KEY")

@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    print("✅ STARTUP TRIGGERED")
    yield

app = FastAPI(title="Scorify Backend", lifespan=lifespan)

@app.post("/run-batch")
def run_batch(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    run_batch_job()
    return {"status": "batch_started"}
