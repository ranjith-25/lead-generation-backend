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
from app.core.connections.notification_listener import (
    connect_notification_listener,
    disconnect_notification_listener,
)

from app.core.connections.s3 import connect_s3,disconnect_s3
from app.core.connections.firebase import connect_firebase,disconnect_firebase

from app.api.auth import router as auth_router
from app.api.opportunity import router as opportunity_router
from app.api.ai import router as ai_router
from app.api.sales_enablement import router as sales_enablement_router
from app.api.feature import router as feature_router
from app.api.role_permissions import router as role_permissions_router
from app.api.project import router as project_router
from app.api.user import router as user_router
from app.api.project_domains import project_domain_router
from app.api.techstack import techstack_router
from app.api.permissions import permission_router
from app.api.platform import platform_router
from app.api.opportunity_status import opportunity_status_router
from app.api.user_status import router as user_status_router
from app.api.job_role import router as job_role_router
from app.api.user_personal_info import router as user_personal_info_router
from app.api.notification import router as notification_router
from app.api.user_invitation import user_invitation_router
from app.api.user_management import router as user_management_router
from app.api.role import router as role_router
from app.api.branch import branch_router
from app.api.profile_variant import router as profile_variant_router
from app.api.dashboard import router as dashboard_router
from app.api.pipeline_execution_status import pipeline_execution_status_router
from app.api.pipeline_opportunity_project import pipeline_opportunity_project_router
from app.api.pipeline_opportunity_resource import pipeline_opportunity_resource_router
from app.api.pipeline_opportunity_techincal_preperation import pipeline_opportunity_technical_preperation_router
from app.api.settings import router as settings_router
from app.api.user_project import router as user_project_router
from app.api.firebase_token import firebase_token_router
from app.api.ai_usages import router as ai_usages_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application Started")
    await connect_ai()
    await connect_notification_listener()
    await connect_s3()
    connect_firebase()

    yield
    await disconnect_notification_listener()
    await disconnect_ai()
    await disconnect_s3()
    disconnect_firebase()

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

# =========================
# AI & Dashboard
# =========================

app.include_router(ai_router)
app.include_router(dashboard_router)


# =========================
# Authentication & Access
# =========================

app.include_router(auth_router)
app.include_router(permission_router)
app.include_router(role_permissions_router)
app.include_router(role_router)
app.include_router(job_role_router)


# =========================
# User Management
# =========================

app.include_router(user_router)
app.include_router(user_management_router)
app.include_router(user_personal_info_router)
app.include_router(user_status_router)
app.include_router(user_invitation_router)


# =========================
# Organization
# =========================

app.include_router(branch_router)


# =========================
# Features & Settings
# =========================

app.include_router(feature_router)
app.include_router(settings_router)
app.include_router(platform_router)


# =========================
# Notifications
# =========================

app.include_router(notification_router)
app.include_router(firebase_token_router)


# =========================
# Opportunities & Pipeline
# =========================

app.include_router(opportunity_router)
app.include_router(opportunity_status_router)
app.include_router(pipeline_execution_status_router)
app.include_router(pipeline_opportunity_project_router)
app.include_router(pipeline_opportunity_resource_router)
app.include_router(pipeline_opportunity_technical_preperation_router)


# =========================
# Projects
# =========================

app.include_router(project_router)
app.include_router(user_project_router)
app.include_router(project_domain_router)


# =========================
# Profile Variants
# =========================

app.include_router(profile_variant_router)


# =========================
# Sales Enablement
# =========================

app.include_router(sales_enablement_router)


# =========================
# Technology Stack
# =========================

app.include_router(techstack_router)
app.include_router(ai_usages_router)