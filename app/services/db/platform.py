import logging
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.models.platform import Platform
from app.models.opportunity import Opportunity

async def get_all_platforms(db: AsyncSession, search: str | None = None, page: int = 1, limit: int = 10):
    try:
        query = select(
            Platform.id.label('platform_id'),
            Platform.name,
            Platform.is_account_linked,
            func.count(Opportunity.opportunityID).label('count')
        ).outerjoin(
            Opportunity, Platform.name == Opportunity.platform
        ).group_by(
            Platform.id, Platform.name, Platform.is_account_linked
        )

        if search:
            query = query.where(Platform.name.ilike(f"%{search.strip()}%"))

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.scalar(count_query)

        query = query.offset((page - 1) * limit).limit(limit)

        result = await db.execute(query)
        rows = result.fetchall()
        items = [
            {
                "platform_id": row.platform_id,
                "name": row.name,
                "is_account_linked": row.is_account_linked,
                "count": row.count,
            }
            for row in rows
        ]
        return items, total or 0
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not find Platforms")
        raise e


async def get_platform_by_id(db: AsyncSession, platform_id: UUID):
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


async def update_platform(db: AsyncSession, update_data: dict, platform_id: UUID):
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


async def delete_platform(db: AsyncSession, platform_id: UUID):
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
