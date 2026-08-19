import asyncio
import json
from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import SortOrder, TimeRange
from app.core.security import create_stream_token, decode_stream_token
from app.core.settings import settings
from app.core.connections.postgres import AsyncSessionLocal, get_db
from app.api.deps import get_current_user, oauth2_scheme
from app.exceptions.auth import SessionExpiredException
from app.models.user import User
from app.responses.notification import (
    MarkAllNotificationsReadResponse,
    MarkNotificationReadResponse
)
from app.services.notifications import (
    get_all_notification,
    handle_mark_all_notifications_as_read,
    handle_mark_notification_as_read
)
from app.services.notification_stream import notification_events
from app.services.db.session import get_active_session_by_id, get_session_by_token
from app.schemas.notification import NotificationFilterRequest, NotificationStreamToken

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get('')
async def get_notifications(
    page: int | None = None,
    limit: int | None = None,
    time_filter: TimeRange | None = None,
    sort_by: str | None = None,
    order_by: SortOrder | None = None,
    is_read: bool | None = None,
    from_date: date | None = Query(None, description="Start of the created-at range (YYYY-MM-DD), inclusive; overrides time_filter"),
    to_date: date | None = Query(None, description="End of the created-at range (YYYY-MM-DD), inclusive; overrides time_filter"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await get_all_notification(
        db,
        filters=NotificationFilterRequest(
            page=page,
            limit=limit,
            time_filter=time_filter,
            sort_by=sort_by,
            order_by=order_by,
            is_read=is_read,
            from_date=from_date,
            to_date=to_date,
        ),
        user_id=current_user.user_id,
    )
    
@router.post('/stream-token', response_model=NotificationStreamToken)
async def issue_stream_token(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Exchange the access token for the short-lived one `/notifications/stream` accepts."""
    session = await get_session_by_token(db, token)

    if not session:
        raise SessionExpiredException()

    return NotificationStreamToken(
        token=create_stream_token(current_user.user_id, session.session_id),
        expires_in=settings.STREAM_TOKEN_EXPIRE_SECONDS,
    )


async def _assert_session_active(user_id: UUID, session_id: UUID) -> None:
    async with AsyncSessionLocal() as db:
        if not await get_active_session_by_id(db, session_id, user_id):
            raise SessionExpiredException()


async def _stream_frames(request: Request, user_id: UUID, session_id: UUID):
    loop = asyncio.get_running_loop()
    last_session_check = loop.time()
    events = notification_events(user_id, settings.STREAM_KEEPALIVE_SECONDS)

    try:
        # Confirms the stream is live and pushes the headers past any buffering proxy.
        yield ": connected\n\n"

        async for event in events:
            if await request.is_disconnected():
                break

            if event is not None:
                yield f"event: notification\ndata: {json.dumps(event)}\n\n"
                continue

            # Idle tick: cheap enough to re-authorise on, so a logout elsewhere closes this.
            now = loop.time()

            if now - last_session_check >= settings.STREAM_SESSION_RECHECK_SECONDS:
                last_session_check = now
                try:
                    await _assert_session_active(user_id, session_id)
                except SessionExpiredException:
                    # Too late for a status code — tell the client to stop reconnecting.
                    yield "event: session_expired\ndata: {}\n\n"
                    break

            yield ": ping\n\n"
    finally:
        # Breaking out of an `async for` leaves the generator suspended, so its unsubscribe
        # would not run until GC. Closing it here is what keeps the subscriber map from
        # accumulating a dead queue per closed tab.
        await events.aclose()


@router.get('/stream')
async def stream_notifications(
    request: Request,
    token: str = Query(..., description="Token from POST /notifications/stream-token"),
):
    """Server-sent events carrying this user's notifications as they are created."""
    user_id, session_id = decode_stream_token(token)
    await _assert_session_active(user_id, session_id)

    return StreamingResponse(
        _stream_frames(request, user_id, session_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            # nginx buffers proxied responses by default, which would hold every event
            # back until the buffer filled — i.e. defeat the entire feature.
            "X-Accel-Buffering": "no",
        },
    )


@router.get('/all_notification')
async def get_all_notifications(
    page: int | None = None,
    limit: int | None = None,
    time_filter: TimeRange | None = None,
    sort_by: str | None = None,
    order_by: SortOrder | None = None,
    is_read: bool | None = None,
    from_date: date | None = Query(None, description="Start of the created-at range (YYYY-MM-DD), inclusive; overrides time_filter"),
    to_date: date | None = Query(None, description="End of the created-at range (YYYY-MM-DD), inclusive; overrides time_filter"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await get_all_notification(
        db,
        filters=NotificationFilterRequest(
            page=page,
            limit=limit,
            time_filter=time_filter,
            sort_by=sort_by,
            order_by=order_by,
            is_read=is_read,
            from_date=from_date,
            to_date=to_date,
        ),
    )


@router.patch('/read-all', response_model=MarkAllNotificationsReadResponse)
async def mark_all_notifications_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MarkAllNotificationsReadResponse:
    """Mark every notification belonging to the current user as read."""
    return await handle_mark_all_notifications_as_read(db, current_user.user_id)


@router.patch('/{notification_id}/read', response_model=MarkNotificationReadResponse)
async def mark_notification_read(
    notification_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MarkNotificationReadResponse:
    """Mark a single notification owned by the current user as read."""
    return await handle_mark_notification_as_read(db, notification_id, current_user.user_id)