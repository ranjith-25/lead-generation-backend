from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.connections.postgres import engine
from app.models.base import Base
from app.core.security import get_password_hash
from app.exceptions.handlers import register_exception_handlers
from app.core.connections.ai_connection import connect_ai,disconnect_ai


from app.api.auth import router as auth_router
from app.api.opportunity import router as opportunity_router
from app.api.ai import router as ai_router
from app.api.sales_enablement import router as sales_enablement_router
from app.api.feature import router as feature_router
from app.api.role_permissions import router as role_permissions_router
from app.api.project import router as project_router

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


@app.get("/health")
async def health():
    return JSONResponse(status_code=status.HTTP_200_OK, content="Ok")


app.include_router(auth_router)
app.include_router(ai_router)
app.include_router(opportunity_router)
app.include_router(sales_enablement_router)
app.include_router(feature_router)
app.include_router(role_permissions_router)
app.include_router(project_router)
