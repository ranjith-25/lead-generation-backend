import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, func, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notifications import Notifications
from app.schemas.notification import NotificationType, NotificationFilterRequest
from app.services.db.filters import apply_sort, apply_time_range

# Field names the API accepts for `sort_by`, mapped to the column each one sorts on.
NOTIFICATION_SORTABLE = {
    "created_at": Notifications.created_at,
    "updated_at": Notifications.updated_at,
    "read_at": Notifications.read_at,
    "is_read": Notifications.is_read,
    "notification_type": Notifications.notification_type,
    "title": Notifications.title,
}

async def get_all_notification(
    db: AsyncSession,
    filters: NotificationFilterRequest,
    user_id: UUID | None = None,
) -> dict:
    try:
        query = select(Notifications)

        if user_id:
            query = query.where(Notifications.user_id == user_id)
        
        if filters.time_filter:
            query = apply_time_range(query, Notifications.created_at, filters.time_filter)

        if filters.is_read is not None:
            query = query.where(Notifications.is_read == filters.is_read)

        total_count = await db.scalar(select(func.count()).select_from(query.subquery())) or 0

        if user_id:
            unread_count = await get_unread_notification_count_db(db, user_id)
        else:
            unread_count = await db.scalar(
                select(func.count())
                .select_from(Notifications)
                .where(Notifications.is_read == False)
            ) or 0

        query = apply_sort(
            query,
            NOTIFICATION_SORTABLE,
            filters.sort_by,
            filters.order_by,
            default_column=Notifications.created_at,
        )

        if filters.page and filters.limit:
            query = query.offset((filters.page - 1) * filters.limit).limit(filters.limit)

        notifications = (await db.execute(query)).scalars().all()

        return {
            "notifications": list(notifications),
            "unread_count": unread_count,
            "total_count": total_count,
        }
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not fetch notifications")
        raise e


async def get_notification_by_id(
    db: AsyncSession, notification_id: UUID, user_id: UUID | None = None
) -> Notifications | None:
    try:
        query = select(Notifications).where(Notifications.id == notification_id)

        if user_id:
            query = query.where(Notifications.user_id == user_id)

        return (await db.execute(query)).scalars().first()
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception(f"Could not fetch notification: {notification_id}")
        raise e


async def get_unread_notification_count_db(db: AsyncSession, user_id: UUID) -> int:
    try:
        count = await db.scalar(
            select(func.count())
            .select_from(Notifications)
            .where(Notifications.user_id == user_id, Notifications.is_read == False)
        )
        return count or 0
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception(f"Could not count unread notifications for user_id: {user_id}")
        raise e


async def create_notification_db(db: AsyncSession, notification_data: dict) -> Notifications:
    try:
        notification = Notifications(**notification_data)
        db.add(notification)
        await db.commit()
        await db.refresh(notification)
        return notification
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not create notification")
        raise e


async def create_notifications_db(
    db: AsyncSession, notifications_data: list[dict]
) -> list[Notifications]:
    try:
        notifications = [Notifications(**data) for data in notifications_data]

        if not notifications:
            return []

        db.add_all(notifications)
        await db.commit()

        for notification in notifications:
            await db.refresh(notification)

        return notifications
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not create notifications")
        raise e


async def update_notification_db(
    db: AsyncSession, notification: Notifications, update_data: dict
) -> Notifications:
    try:
        for key, value in update_data.items():
            setattr(notification, key, value)

        await db.commit()
        await db.refresh(notification)
        return notification
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception(f"Could not update notification: {notification.id}")
        raise e


async def mark_all_notifications_read_db(db: AsyncSession, user_id: UUID) -> int:
    try:
        result = await db.execute(
            update(Notifications)
            .where(Notifications.user_id == user_id, Notifications.is_read == False)
            .values(
                is_read=True,
                read_at=datetime.now(timezone.utc).replace(tzinfo=None),
                updated_by=user_id,
            )
        )
        await db.commit()
        return result.rowcount or 0
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception(f"Could not mark notifications as read for user_id: {user_id}")
        raise e
