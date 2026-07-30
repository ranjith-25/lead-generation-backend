from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.connections.postgres import engine
from app.models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application Started")

    yield

    await engine.dispose()
    print("Application Stopped")
    


app = FastAPI(title="Lead Generation API", lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.core.security import get_password_hash
print(get_password_hash("1234"))
from app.api.auth import router as auth_router

app.include_router(auth_router)

@app.get("/health")
async def health():
    return {"status": "ok"}
