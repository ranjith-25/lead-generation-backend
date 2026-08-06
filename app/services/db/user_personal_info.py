import logging
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_personal_info import UserPersonalInfo


async def create_user_personal_info(db: AsyncSession, personal_info: UserPersonalInfo) -> UserPersonalInfo:
    try:
        db.add(personal_info)
        await db.commit()
        await db.refresh(personal_info)
        return personal_info
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not create User Personal Info")
        raise e


async def get_user_personal_info_by_user_id(db: AsyncSession, user_id: UUID) -> UserPersonalInfo | None:
    try:
        result = await db.execute(
            select(UserPersonalInfo).where(UserPersonalInfo.user_id == user_id)
        )
        return result.scalars().first()
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception(f"Could not fetch User Personal Info for user_id: {user_id}")
        raise e


async def update_user_personal_info(db: AsyncSession, update_data: dict, user_id: UUID) -> UserPersonalInfo | None:
    try:
        result = await db.execute(
            select(UserPersonalInfo).where(UserPersonalInfo.user_id == user_id)
        )
        db_personal_info = result.scalars().first()

        if not db_personal_info:
            return None

        for key, value in update_data.items():
            if hasattr(db_personal_info, key):
                setattr(db_personal_info, key, value)

        await db.commit()
        await db.refresh(db_personal_info)
        return db_personal_info
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception(f"Could not update User Personal Info for user_id: {user_id}")
        raise e


async def delete_user_personal_info(db: AsyncSession, user_id: UUID) -> UserPersonalInfo | None:
    try:
        result = await db.execute(select(UserPersonalInfo).where(UserPersonalInfo.user_id == user_id))
        db_personal_info = result.scalars().first()
        
        if not db_personal_info:
            return None
            
        await db.delete(db_personal_info)
        await db.commit()
        return db_personal_info
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception(f"Could not delete User Personal Info for user_id: {user_id}")
        raise e
