import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, func, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.schemas.notification import NotificationType, NotificationFilterRequest

async def get_all_notification(
    db: AsyncSession,
    user_id: UUID | None = None,
    filters = NotificationFilterRequest
) -> tuple[list[Notification], int]:
    try:
        query = select(Notification)

        if user_id:
            query = query.where(Notification.user_id == user_id)

        if filters.is_read is not None:
            query = query.where(Notification.is_read == filters.is_read)

        if filters.notification_type:
            query = query.where(Notification.notification_type.in_(filters.notification_type))

        total = await db.scalar(select(func.count()).select_from(query.subquery())) or 0

        query = query.order_by(Notification.created_at.desc())

        if filters.page and filters.limit:
            query = query.offset((filters.page - 1) * filters.limit).limit(filters.limit)

        notifications = (await db.execute(query)).scalars().all()
        return list(notifications), total
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not fetch notifications")
        raise e


async def get_notification_by_id(
    db: AsyncSession, notification_id: UUID, user_id: UUID | None = None
) -> Notification | None:
    try:
        query = select(Notification).where(Notification.id == notification_id)

        if user_id:
            query = query.where(Notification.user_id == user_id)

        return (await db.execute(query)).scalars().first()
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception(f"Could not fetch notification: {notification_id}")
        raise e


async def get_unread_notification_count_db(db: AsyncSession, user_id: UUID) -> int:
    try:
        count = await db.scalar(
            select(func.count())
            .select_from(Notification)
            .where(Notification.user_id == user_id, Notification.is_read == False)
        )
        return count or 0
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception(f"Could not count unread notifications for user_id: {user_id}")
        raise e


async def create_notification_db(db: AsyncSession, notification_data: dict) -> Notification:
    try:
        notification = Notification(**notification_data)
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
) -> list[Notification]:
    try:
        notifications = [Notification(**data) for data in notifications_data]

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
    db: AsyncSession, notification: Notification, update_data: dict
) -> Notification:
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
            update(Notification)
            .where(Notification.user_id == user_id, Notification.is_read == False)
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
