import logging
from datetime import datetime, timezone
from math import ceil
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.notification import NotificationNotFoundException
from app.responses.notification import (
    MarkAllNotificationsReadResponse,
    MarkNotificationReadResponse,
)
from app.schemas.notification import (
    NotificationBulkCreateSchema,
    NotificationContentBase,
    NotificationCreateSchema,
    NotificationFilterRequest,
    NotificationPaginatedResponse,
    NotificationRead,
    NotificationType,
)

from app.services.db.notifications import (
    create_notification_db,
    create_notifications_db,
    get_all_notification,
    get_notification_by_id,
    get_unread_notification_count_db,
    mark_all_notifications_read_db,
    update_notification_db,
)
from app.services.notification_stream import publish_notifications
from app.services.notification_content import build_notification_content
from app.services.firebase_messaging import send_firebase_push_for_notifications


async def create_notification(
    db: AsyncSession, notification_data: NotificationCreateSchema
) -> NotificationRead:
    data_for_notification = {
        **build_notification_content(notification_data),
        "user_id": notification_data.user_id,
    }

    created_notification = await create_notification_db(db, data_for_notification)
    notification = NotificationRead.model_validate(created_notification)

    await publish_notifications(db, [notification])

    try:
        await send_firebase_push_for_notifications(
            db=db,
            user_ids=[notification_data.user_id],
            notification_type=notification_data.notification_type,
            title=data_for_notification.get("title") or "",
            body=data_for_notification.get("body") or "",
            url=data_for_notification.get("url"),
            context=notification_data.context,
        )
    except Exception:
        logging.exception("Failed to send Firebase push notification in create_notification")

    return notification


async def create_bulk_notification(
    db: AsyncSession, notification_data: NotificationBulkCreateSchema
) -> list[NotificationRead]:
    """Same content fanned out to many users, inserted in a single commit."""
    if not notification_data.user_ids:
        return []

    content = build_notification_content(notification_data)
    user_ids = list(dict.fromkeys(notification_data.user_ids))

    created_notifications = await create_notifications_db(
        db, [{**content, "user_id": user_id} for user_id in user_ids]
    )
    notifications = [
        NotificationRead.model_validate(notification) for notification in created_notifications
    ]

    await publish_notifications(db, notifications)

    try:
        await send_firebase_push_for_notifications(
            db=db,
            user_ids=user_ids,
            notification_type=notification_data.notification_type,
            title=content.get("title") or "",
            body=content.get("body") or "",
            url=content.get("url"),
            context=notification_data.context,
        )
    except Exception:
        logging.exception("Failed to send Firebase push notifications in create_bulk_notification")

    return notifications


async def get_user_notifications(
    db: AsyncSession, user_id: UUID, filters: NotificationFilterRequest
) -> NotificationPaginatedResponse:
    notifications, total = await get_all_notification(
        db,
        user_id=user_id,
        is_read=filters.is_read,
        notification_type=filters.notification_type,
        page=filters.page,
        limit=filters.limit,
    )
    unread_count = await get_unread_notification_count_db(db, user_id)

    return NotificationPaginatedResponse(
        items=[NotificationRead.model_validate(notification) for notification in notifications],
        total=total,
        unread_count=unread_count,
        page=filters.page,
        limit=filters.limit,
        total_pages=ceil(total / filters.limit) if total else 0,
    )


async def get_unread_notification_count(db: AsyncSession, user_id: UUID) -> int:
    return await get_unread_notification_count_db(db, user_id)


async def mark_notification_as_read(
    db: AsyncSession, notification_id: UUID, user_id: UUID
) -> NotificationRead:
    notification = await get_notification_by_id(db, notification_id, user_id)

    if not notification:
        raise NotificationNotFoundException(notification_id)

    if notification.is_read:
        return NotificationRead.model_validate(notification)

    updated_notification = await update_notification_db(
        db,
        notification,
        {
            "is_read": True,
            "read_at": datetime.now(timezone.utc).replace(tzinfo=None),
            "updated_by": user_id,
        },
    )
    return NotificationRead.model_validate(updated_notification)


async def mark_all_notifications_as_read(db: AsyncSession, user_id: UUID) -> int:
    """Returns how many notifications were flipped to read."""
    return await mark_all_notifications_read_db(db, user_id)


async def handle_mark_notification_as_read(
    db: AsyncSession, notification_id: UUID, user_id: UUID
) -> MarkNotificationReadResponse:
    try:
        notification = await mark_notification_as_read(db, notification_id, user_id)
        unread_count = await get_unread_notification_count(db, user_id)

        return MarkNotificationReadResponse(
            notification=notification,
            unread_count=unread_count,
            message="Notification marked as read",
        )
    except Exception as e:
        logging.exception("Some error occurred while marking notification as read")
        raise e


async def handle_mark_all_notifications_as_read(
    db: AsyncSession, user_id: UUID
) -> MarkAllNotificationsReadResponse:
    try:
        updated_count = await mark_all_notifications_as_read(db, user_id)
        unread_count = await get_unread_notification_count(db, user_id)

        return MarkAllNotificationsReadResponse(
            updated_count=updated_count,
            unread_count=unread_count,
            message="All notifications marked as read",
        )
    except Exception as e:
        logging.exception("Some error occurred while marking all notifications as read")
        raise e
