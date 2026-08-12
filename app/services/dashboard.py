import logging
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.user import User
from app.schemas.dashboard import DashboardResponse, DashboardSummaryResponse
from app.services.db.dashboard import get_dashboard_metrics, get_dashboard_summary_metrics
from app.config import TimeRange


async def handle_get_dashboard_data(db: AsyncSession, current_user: User, time_range: TimeRange | None = None, platform: str | None = None) -> DashboardResponse:
    try:
        metrics = await get_dashboard_metrics(db, time_range, platform)
        return DashboardResponse(**metrics)
    except Exception as e:
        logging.exception("Some error occurred while getting dashboard data")
        raise HTTPException(status_code=500, detail="Could not fetch dashboard metrics")

async def handle_get_dashboard_summary(db: AsyncSession, current_user: User, view: str) -> DashboardSummaryResponse:
    try:
        metrics = await get_dashboard_summary_metrics(db, current_user, view)
        return DashboardSummaryResponse(**metrics)
    except Exception as e:
        logging.exception("Some error occurred while getting dashboard summary")
        raise HTTPException(status_code=500, detail="Could not fetch dashboard summary")
