import logging
from datetime import datetime, timezone
from math import ceil
from typing import Any
from uuid import UUID
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import settings
from app.exceptions.notification import (
    NotificationNotFoundException,
    NotificationTypeNotConfiguredException,
)
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
from app.services.db.firebase_token import get_firebase_token_by_user_id
from app.services.firebase_messaging import send_push_notification
from app.schemas.firebase_messaging import FirebaseNotificationPayload
from app.schemas.firebase_messaging import FirebaseNotificationPayload 
from app.config import (
    AUDIENCE_ROLES,
    Audience,
    NOTIFICATION_CONTENT,
    NOTIFICATION_EVENTS,
    NOTIFICATION_NAVIGATION,
    NOTIFICATION_TYPE_NAVIGATION,
    NotificationEvent,
)


class _SafeContext(dict):
    """Keeps template rendering forgiving — missing or None placeholders become empty strings."""

    def __getitem__(self, key):
        value = super().__getitem__(key)
        if value is None:
            return ""
        return value

    def __missing__(self, key):
        logging.warning(f"Missing notification template placeholder: {key}")
        return ""


def _render(template: str | None, context: dict[str, Any]) -> str | None:
    if not template:
        return template
    try:
        return template.format_map(_SafeContext(context))
    except (IndexError, ValueError):
        # Braces that are not placeholders (json snippets, css, …) — keep the raw template.
        logging.warning("Could not render notification template, using it as-is")
        return template


def _resolve_navigation_url(notification_type: NotificationType, context: dict[str, Any]) -> str | None:
    """notification type -> page key (NOTIFICATION_TYPE_NAVIGATION) -> link (NOTIFICATION_NAVIGATION)."""
    page_key = NOTIFICATION_TYPE_NAVIGATION.get(notification_type.value)

    if not page_key:
        # Deliberately unnavigable notification type — not a misconfiguration.
        return None

    link = NOTIFICATION_NAVIGATION.get(page_key)

    if not link:
        logging.warning(
            f"Notifications type {notification_type.value} points at unknown navigation page: {page_key}"
        )
        return None

    if link.startswith("/"):
        link = f"{settings.FRONTEND_BASE_URL.rstrip('/')}{link}"

    return _render(link, context)


def build_notification_content(content: NotificationContentBase) -> dict:
    notification_type = content.notification_type
    configured = NOTIFICATION_CONTENT.get(notification_type.value)

    if configured is None:
        raise NotificationTypeNotConfiguredException(notification_type.value)

    title = content.title or _render(configured.get("title", ""), content.context)
    body = content.body or _render(configured.get("body", ""), content.context)
    url = content.url or _resolve_navigation_url(notification_type, content.context)

    return {
        "notification_type": notification_type,
        "title": title or "",
        "body": body or "",
        "url": url,
        "created_by": content.created_by,
        "updated_by": content.created_by,
    }


async def send_firebase_push_for_notifications(
    db: AsyncSession,
    user_ids: list[UUID],
    notification_type: NotificationType,
    title: str,
    body: str,
    url: str | None = None,
    context: dict[str, Any] | None = None,
) -> None:
    """Delivers Firebase push notifications to all active FCM tokens belonging to target users.

    Isolated with try-except to ensure Firebase failures never break in-app notification flows.
    """
    if not user_ids:
        return

    try:
        data: dict[str, str] = {}
        if url:
            data["url"] = str(url)
        if context:
            for k, v in context.items():
                if v is not None:
                    data[str(k)] = str(v)

        payload = FirebaseNotificationPayload(
            notification_type=notification_type,
            title=title or "",
            body=body or "",
            data=data or None,
        )

        for user_id in user_ids:
            try:
                tokens = await get_firebase_token_by_user_id(db, user_id)
                active_tokens = [
                    t.fcm_token
                    for t in tokens
                    if getattr(t, "is_active", True) and getattr(t, "fcm_token", None)
                ]

                if not active_tokens:
                    logging.info(
                        "No active FCM tokens found for user_id=%s (notification_type=%s)",
                        user_id,
                        notification_type.value if hasattr(notification_type, "value") else notification_type,
                    )
                    continue

                logging.info(
                    "Sending Firebase push notification to %d token(s) for user_id=%s (notification_type=%s)",
                    len(active_tokens),
                    user_id,
                    notification_type.value if hasattr(notification_type, "value") else notification_type,
                )

                response = send_push_notification(
                    firebase_notification=payload,
                    tokens=active_tokens,
                )

                success_count = getattr(response, "success_count", 0)
                failure_count = getattr(response, "failure_count", 0)
                logging.info(
                    "Firebase push result for user_id=%s: %d succeeded, %d failed",
                    user_id,
                    success_count,
                    failure_count,
                )
            except Exception:
                logging.exception(
                    "Error sending Firebase push notification for user_id=%s (notification_type=%s)",
                    user_id,
                    notification_type.value if hasattr(notification_type, "value") else notification_type,
                )
    except Exception:
        logging.exception(
            "Unexpected error in send_firebase_push_for_notifications for notification_type=%s",
            notification_type.value if hasattr(notification_type, "value") else notification_type,
        )


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
