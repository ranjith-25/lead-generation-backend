from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.connections.postgres import get_db
from app.core.security import require_permission
from app.models.user import User
from app.schemas.dashboard import DashboardResponse, DashboardTimeRange, DashboardSummaryResponse
from app.services.dashboard import handle_get_dashboard_data, handle_get_dashboard_summary

router = APIRouter(prefix="/dashboard", tags=["KPI Dashboard Analytics"])

@router.get("", response_model=DashboardResponse)
async def get_dashboard_metrics(
    time_range: DashboardTimeRange | None = None,
    platform: str | None = None,
    current_user: User = Depends(require_permission("kpi_dashboard", "read")),
    db: AsyncSession = Depends(get_db),
) -> DashboardResponse:
    """
    Returns analytics and metrics data for the KPI dashboard.
    """
    return await handle_get_dashboard_data(db, current_user, time_range, platform)


@router.get("/summary", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(
    view: str = Query("My view", description="View mode: 'My view' or 'Team view'"),
    current_user: User = Depends(require_permission("kpi_dashboard", "read")),
    db: AsyncSession = Depends(get_db),
) -> DashboardSummaryResponse:
    """
    Returns summary metrics and latest opportunities for the KPI dashboard.
    """
    return await handle_get_dashboard_summary(db, current_user, view)
