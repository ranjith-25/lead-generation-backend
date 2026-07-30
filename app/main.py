from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.api.sample import router as sample_router
from app.core.connections.postgres import get_connection,close_connection
from app.models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application Started")

    yield

    await engine.dispose()
    print("Application Stopped")
    


app = FastAPI(title="Lead Generation API", lifespan=lifespan)


app.include_router(sample_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
