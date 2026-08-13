from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import NotificationType, TimeRange
from app.core.security import require_permission
from app.core.connections.postgres import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.notifications import (
    get_all_notification
)
from app.schemas.notification import NotificationFilterRequest

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get('')
async def get_notifications(
    page: int | None = None,
    limit: int | None = None,
    time_filter: TimeRange | None = None,
    is_read: bool | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await get_all_notification(
        db,
        filters=NotificationFilterRequest(
            page=page,
            limit=limit,
            time_filter=time_filter,
            is_read=is_read,
        ),
        user_id=current_user.user_id,
    )
    
@router.get('/all_notification')
async def get_all_notifications(
    page: int | None = None,
    limit: int | None = None,
    time_filter: TimeRange | None = None,
    is_read: bool | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await get_all_notification(
        db,
        filters=NotificationFilterRequest(
            page=page,
            limit=limit,
            time_filter=time_filter,
            is_read=is_read,
        ),
    )