import logging
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.platform import Platform


async def get_all_platforms(db: AsyncSession):
    try:
        result = await db.execute(select(Platform))
        return result.scalars().all()
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not find Platforms")
        raise e


async def get_platform_by_id(db: AsyncSession, platform_id: int):
    try:
        result = await db.execute(select(Platform).where(Platform.id == platform_id))
        return result.scalars().first()
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not find Platform")
        raise e


async def create_platform(db: AsyncSession, platform: Platform):
    try:
        db.add(platform)
        await db.commit()
        await db.refresh(platform)
        return platform
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not create Platform")
        raise e


async def update_platform(db: AsyncSession, update_data: dict, platform_id: int):
    try:
        result = await db.execute(select(Platform).where(Platform.id == platform_id))
        db_platform = result.scalars().first()

        if not db_platform:
            return None

        for key, value in update_data.items():
            if key != "id":
                setattr(db_platform, key, value)

        await db.commit()
        await db.refresh(db_platform)
        return db_platform
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not update Platform")
        raise e


async def delete_platform(db: AsyncSession, platform_id: int):
    try:
        result = await db.execute(select(Platform).where(Platform.id == platform_id))
        db_platform = result.scalars().first()
        if not db_platform:
            return None
        await db.delete(db_platform)
        await db.commit()
        return db_platform
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not delete Platform")
        raise e
