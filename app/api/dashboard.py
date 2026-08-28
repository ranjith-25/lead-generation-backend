from datetime import date

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.connections.postgres import get_db
from app.core.security import require_permission
from app.models.user import User
from app.schemas.dashboard import (
    DashboardFilterRequest,
    DashboardResponse,
    DashboardSummaryFilterRequest,
    DashboardSummaryResponse,
)
from app.config import TimeRange
from app.services.dashboard import handle_get_dashboard_data, handle_get_dashboard_summary,handle_export_kpi_dashboard, handle_export_dashboard_summary
from app.responses.project import FileDownloadResponse

router = APIRouter(prefix="/dashboard", tags=["KPI Dashboard Analytics"])

@router.get("", response_model=DashboardResponse)
async def get_dashboard_metrics(
    time_range: TimeRange | None = None,
    platform: str | None = None,
    from_date: date | None = Query(None, description="Start of the created-at range (YYYY-MM-DD), inclusive; overrides time_range"),
    to_date: date | None = Query(None, description="End of the created-at range (YYYY-MM-DD), inclusive; overrides time_range"),
    current_user: User = Depends(require_permission("kpi_dashboard", "read")),
    db: AsyncSession = Depends(get_db),
) -> DashboardResponse:
    """
    Returns analytics and metrics data for the KPI dashboard.
    """
    return await handle_get_dashboard_data(
        db,
        current_user,
        DashboardFilterRequest(
            time_range=time_range,
            platform=platform,
            from_date=from_date,
            to_date=to_date,
        ),
    )


@router.get("/summary", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(
    view: str = Query("My view", description="View mode: 'My view' or 'Team view'"),
    time_range: TimeRange | None = None,
    from_date: date | None = Query(None, description="Start of the created-at range (YYYY-MM-DD), inclusive; overrides time_range"),
    to_date: date | None = Query(None, description="End of the created-at range (YYYY-MM-DD), inclusive; overrides time_range"),
    current_user: User = Depends(require_permission("kpi_dashboard", "read")),
    db: AsyncSession = Depends(get_db),
) -> DashboardSummaryResponse:
    """
    Returns summary metrics and latest opportunities for the KPI dashboard.
    """
    return await handle_get_dashboard_summary(
        db,
        current_user,
        DashboardSummaryFilterRequest(
            view=view,
            time_range=time_range,
            from_date=from_date,
            to_date=to_date,
        ),
    )


@router.get("/export")
async def export_dashboard_metrics(
    time_range: TimeRange | None = None,
    platform: str | None = None,
    from_date: date | None = Query(None, description="Start of the created-at range (YYYY-MM-DD), inclusive; overrides time_range"),
    to_date: date | None = Query(None, description="End of the created-at range (YYYY-MM-DD), inclusive; overrides time_range"),
    current_user: User = Depends(require_permission("kpi_dashboard", "export")),
    db: AsyncSession = Depends(get_db),
):
    """
    Downloads analytics and metrics data for the KPI dashboard.
    """
    response : FileDownloadResponse = await handle_export_kpi_dashboard(
        db,
        current_user,
        DashboardFilterRequest(
            time_range=time_range,
            platform=platform,
            from_date=from_date,
            to_date=to_date,
        ),
    )

    return StreamingResponse(
        response.file_stream,
        media_type=response.content_type,
        headers={
            "Content-Disposition": (
                f'attachment; filename="{response.file_name}"'
            )
        },
    )

@router.get("/summary/export")
async def export_dashboard_summary(
    view: str = Query("My view", description="View mode: 'My view' or 'Team view'"),
    time_range: TimeRange | None = None,
    from_date: date | None = Query(None, description="Start of the created-at range (YYYY-MM-DD), inclusive; overrides time_range"),
    to_date: date | None = Query(None, description="End of the created-at range (YYYY-MM-DD), inclusive; overrides time_range"),
    current_user: User = Depends(require_permission("kpi_dashboard", "read")),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns summary metrics and latest opportunities for the KPI dashboard.
    """
    response : FileDownloadResponse = await handle_export_dashboard_summary(
        db,
        current_user,
        DashboardSummaryFilterRequest(
            view=view,
            time_range=time_range,
            from_date=from_date,
            to_date=to_date,
        ),
    )

    return StreamingResponse(
        response.file_stream,
        media_type=response.content_type,
        headers={
            "Content-Disposition": (
                f'attachment; filename="{response.file_name}"'
            )
        },
    )
