import logging
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import AUDIENCE_ROLES, Audience, NotificationEvent, NotificationType
from app.schemas.notification import NotificationBulkCreateSchema, NotificationRead
from app.services.db.user import get_user_ids_by_role_names


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
        from app.config import NOTIFICATION_EVENTS

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


async def notify_users(
    db: AsyncSession,
    user_ids: list[UUID],
    notification_type: NotificationType,
    context: dict[str, Any] | None = None,
    created_by: UUID | None = None,
) -> list[NotificationRead]:
    from app.services.notifications import create_bulk_notification

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
