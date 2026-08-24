from fastapi import Depends
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.models.user import User
from app.responses.ai_usage import AIUsageMetricsResponse, AIUsageLogsResponse
from app.services.ai_usage import get_cost_token_calls_service, get_logs_service
from app.core.connections.postgres import get_db

router = APIRouter(prefix="/ai-usage", tags=["AI usage"])


@router.get("/metrics", response_model=AIUsageMetricsResponse)
async def get_cost_token_calls(
    current_user: User = Depends(get_current_user),
) -> AIUsageMetricsResponse:
    return await get_cost_token_calls_service()


@router.get("/logs", response_model=AIUsageLogsResponse)
async def get_logs(
    db: AsyncSession = Depends(get_db),
) -> AIUsageLogsResponse:
    return await get_logs_service(db)