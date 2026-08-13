import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from math import ceil
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

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
from app.services.db.user import get_user_ids_by_role_names
from app.services.notification_stream import publish_notifications
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
            f"Notifications type {notification_type.value} points at unknown navigation page: {page_key}"
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
    notification = NotificationRead.model_validate(created_notification)

    await publish_notifications(db, [notification])

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

    return notifications


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


@dataclass
class NotificationEventContext:
    """Everything an event needs to resolve its audiences, plus the shared template context.

    Carries plain ids rather than ORM objects on purpose: that keeps this shared service free
    of any dependency on the pipeline/opportunity models, so the caller owns the loading and
    the dispatcher stays usable from any feature.
    """

    actor_id: UUID
    content: dict[str, Any]
    subject_id: UUID | None = None
    subject_reporting_to: UUID | None = None
    opportunity_owner_id: UUID | None = None


async def _resolve_audience(
    db: AsyncSession,
    audience: Audience,
    ctx: NotificationEventContext,
    role_cache: dict[str, list[UUID]],
) -> list[UUID]:
    """Audience -> user ids, memoising role lookups in `role_cache` for the current dispatch."""
    role_name = AUDIENCE_ROLES.get(audience)

    if role_name is not None:
        if role_name not in role_cache:
            role_cache[role_name] = await get_user_ids_by_role_names(db, [role_name])
        return role_cache[role_name]

    # Absent from AUDIENCE_ROLES means a relationship audience — read off the event context,
    # never from a role.
    relationship_ids = {
        Audience.SUBJECT: ctx.subject_id,
        Audience.SUBJECT_REPORTING_TO: ctx.subject_reporting_to,
        Audience.OPPORTUNITY_OWNER: ctx.opportunity_owner_id,
    }
    user_id = relationship_ids.get(audience)

    return [user_id] if user_id else []


async def dispatch_notification_event(
    db: AsyncSession,
    event: NotificationEvent,
    ctx: NotificationEventContext,
) -> None:
    """Fan one event out to its configured audiences — at most one notification per person.

    Audiences are walked in registry order and the first one to match a person claims them, so
    a more specific message always wins over a later role-wide blast.
    """
    try:
        audiences = NOTIFICATION_EVENTS.get(event)

        if not audiences:
            logging.warning(f"No audiences configured for notification event: {event}")
            return

        claimed: set[UUID] = {ctx.actor_id}
        role_cache: dict[str, list[UUID]] = {}

        for audience, notification_type in audiences:
            user_ids = await _resolve_audience(db, audience, ctx, role_cache)
            fresh = [user_id for user_id in user_ids if user_id and user_id not in claimed]

            if not fresh:
                continue

            claimed.update(fresh)
            await notify_users(
                db,
                user_ids=fresh,
                notification_type=notification_type,
                context=ctx.content,
                created_by=ctx.actor_id,
            )
    except Exception:
        # The status change that raised this event has already committed — a notification
        # failure must never turn it into a 500.
        logging.exception("Could not dispatch notification event %s", event)


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