from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.config import LogAction, LogModule
from app.core.connections.postgres import get_db
from app.models.user import User
from app.responses.system_log import SystemLogPaginatedResponse
from app.schemas.system_log import SystemLogDetailRead, SystemLogFilterRequest
from app.services.system_log import (
    get_system_log_detail_service,
    get_system_logs_service,
)

router = APIRouter(prefix="/system-logs", tags=["System Activity Logs"])


@router.get("", response_model=SystemLogPaginatedResponse)
async def get_system_logs(
    module: LogModule | None = None,
    action: LogAction | None = None,
    performed_by: UUID | None = None,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
    search: str | None = Query(None, description="Matches description or user name"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SystemLogPaginatedResponse:
    """The activity timeline. Readable by any authenticated user."""
    return await get_system_logs_service(
        db,
        filters=SystemLogFilterRequest(
            module=module,
            action=action,
            performed_by=performed_by,
            from_date=from_date,
            to_date=to_date,
            search=search,
            page=page,
            size=size,
        ),
    )


@router.get("/{log_id}", response_model=SystemLogDetailRead)
async def get_system_log(
    log_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SystemLogDetailRead:
    """One log row with its entity pointer and `details` payload."""
    return await get_system_log_detail_service(db, log_id)
