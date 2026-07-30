from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.api.sample import router as sample_router
from app.database import engine
from app.models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title="Lead Generation API", lifespan=lifespan)


app.include_router(sample_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
