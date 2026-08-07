import logging
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_status import UserStatus
from app.models.user_personal_info import UserPersonalInfo


async def get_all_user_statuses(db: AsyncSession, search: str | None = None, page: int = 1, limit: int = 10):
    try:
        query = select(
            UserStatus.id,
            UserStatus.displayName.label('status'),
            func.count(UserPersonalInfo.id).label('count')
        ).outerjoin(
            UserPersonalInfo, UserStatus.id == UserPersonalInfo.working_status_id
        ).where(
            UserStatus.is_active == True
        ).group_by(
            UserStatus.id, UserStatus.displayName
        )

        if search:
            query = query.where(UserStatus.displayName.ilike(f"%{search.strip()}%"))

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.scalar(count_query)

        query = query.offset((page - 1) * limit).limit(limit)

        result = await db.execute(query)
        rows = result.fetchall()
        items = [
            {
                "id": row.id,
                "status": row.status,
                "count": row.count,
            }
            for row in rows
        ]
        return items, total or 0
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not find User Statuses")
        raise e


async def get_user_status_by_id(db: AsyncSession, user_status_id: int):
    try:
        result = await db.execute(
            select(UserStatus).where(
                UserStatus.id == user_status_id,
                UserStatus.is_active == True,
            )
        )
        return result.scalars().first()
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not find User Status")
        raise e


async def create_user_status(db: AsyncSession, user_status: UserStatus):
    try:
        db.add(user_status)
        await db.commit()
        await db.refresh(user_status)
        return user_status
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not create User Status")
        raise e


async def update_user_status(db: AsyncSession, update_data: dict, user_status_id: int):
    try:
        result = await db.execute(
            select(UserStatus).where(
                UserStatus.id == user_status_id,
                UserStatus.is_active == True,
            )
        )
        db_user_status = result.scalars().first()

        if not db_user_status:
            return None

        for key, value in update_data.items():
            if key != "id":
                setattr(db_user_status, key, value)

        await db.commit()
        await db.refresh(db_user_status)
        return db_user_status
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not update User Status")
        raise e


async def delete_user_status(db: AsyncSession, user_status_id: int):
    try:
        result = await db.execute(select(UserStatus).where(UserStatus.id == user_status_id))
        db_user_status = result.scalars().first()
        if not db_user_status:
            return None
        await db.delete(db_user_status)
        await db.commit()
        return db_user_status
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not delete User Status")
        raise e
