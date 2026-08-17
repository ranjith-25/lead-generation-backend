from fastapi import Depends
from fastapi.routing import APIRouter

from app.api.deps import get_current_user
from app.models.user import User
from app.responses.ai_usage import AIUsageMetricsResponse, AIUsageLogsResponse
from app.services.ai_usage import get_cost_token_calls_service, get_logs_service

router = APIRouter(prefix="/asi-usage", tags=["AI usage"])


@router.get("/metrics", response_model=AIUsageMetricsResponse)
async def get_cost_token_calls(
    current_user: User = Depends(get_current_user),
) -> AIUsageMetricsResponse:
    return await get_cost_token_calls_service()


@router.get("/logs", response_model=AIUsageLogsResponse)
async def get_logs(
    current_user: User = Depends(get_current_user),
) -> AIUsageLogsResponse:
    return await get_logs_service()