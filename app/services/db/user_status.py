import logging
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_status import UserStatus


async def get_all_user_statuses(db: AsyncSession):
    try:
        result = await db.execute(select(UserStatus).where(UserStatus.is_active == True))
        return result.scalars().all()
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
