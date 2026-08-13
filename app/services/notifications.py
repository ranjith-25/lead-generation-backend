import logging
from datetime import datetime, timezone
from math import ceil
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.notification import (
    NotificationNotFoundException,
    NotificationTypeNotConfiguredException,
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
from app.config import (
    NOTIFICATION_CONTENT,
    NOTIFICATION_NAVIGATION,
    NOTIFICATION_TYPE_NAVIGATION,
)


class _SafeContext(dict):
    """Keeps template rendering forgiving — an unsupplied placeholder becomes an empty string."""

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
            f"Notification type {notification_type.value} points at unknown navigation page: {page_key}"
        )
        return None

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


async def create_notification(
    db: AsyncSession, notification_data: NotificationCreateSchema
) -> NotificationRead:
    data_for_notification = {
        **build_notification_content(notification_data),
        "user_id": notification_data.user_id,
    }

    created_notification = await create_notification_db(db, data_for_notification)
    return NotificationRead.model_validate(created_notification)


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
    return [NotificationRead.model_validate(notification) for notification in created_notifications]


async def notify_users(
    db: AsyncSession,
    user_ids: list[UUID],
    notification_type: NotificationType,
    context: dict[str, Any] | None = None,
    created_by: UUID | None = None,
) -> list[NotificationRead]:
    try:
        return await create_bulk_notification(
            db,
            NotificationBulkCreateSchema(
                notification_type=notification_type,
                user_ids=user_ids,
                context=context or {},
                created_by=created_by,
            ),
        )
    except Exception:
        logging.exception(f"Could not notify users for notification type: {notification_type}")
        return []


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