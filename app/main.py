from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.connections.postgres import engine
from app.models import Base
from app.core.security import get_password_hash
from app.exceptions.handlers import register_exception_handlers

from app.api.auth import router as auth_router
from app.api.ai import aiRouter
from app.core.connections.ai_connection import connect_ai,disconnect_ai

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application Started")
    await connect_ai()

    yield
    await disconnect_ai()

    await engine.dispose()
    logger.info("Application Stopped")
    
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


app = FastAPI(title="Lead Generation API", lifespan=lifespan)

register_exception_handlers(app)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info(get_password_hash("1234"))


@app.get("/health")
async def health():
    return JSONResponse(status_code=status.HTTP_200_OK, content="Ok")


app.include_router(auth_router)
app.include_router(aiRouter)