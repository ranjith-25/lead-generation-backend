import logging
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.opportunity_status import OpportunityStatus


async def get_all_opportunity_statuses(db: AsyncSession):
    try:
        result = await db.execute(select(OpportunityStatus).where(OpportunityStatus.is_active == True))
        return result.scalars().all()
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not find Opportunity Statuses")
        raise e


async def get_opportunity_status_by_id(db: AsyncSession, opportunity_status_id: int):
    try:
        result = await db.execute(select(OpportunityStatus).where(OpportunityStatus.id == opportunity_status_id,OpportunityStatus.is_active == True))
        return result.scalars().first()
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not find Opportunity Status")
        raise e


async def create_opportunity_status(db: AsyncSession, opportunity_status: OpportunityStatus):
    try:
        db.add(opportunity_status)
        await db.commit()
        await db.refresh(opportunity_status)
        return opportunity_status
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not create Opportunity Status")
        raise e


async def update_opportunity_status(db: AsyncSession, update_data: dict, opportunity_status_id: int):
    try:
        result = await db.execute(select(OpportunityStatus).where(OpportunityStatus.id == opportunity_status_id,OpportunityStatus.is_active == True))
        db_opportunity_status = result.scalars().first()

        if not db_opportunity_status:
            return None

        for key, value in update_data.items():
            if key != "id":
                setattr(db_opportunity_status, key, value)

        await db.commit()
        await db.refresh(db_opportunity_status)
        return db_opportunity_status
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not update Opportunity Status")
        raise e


async def delete_opportunity_status(db: AsyncSession, opportunity_status_id: int):
    try:
        result = await db.execute(select(OpportunityStatus).where(OpportunityStatus.id == opportunity_status_id))
        db_opportunity_status = result.scalars().first()
        if not db_opportunity_status:
            return None
        await db.delete(db_opportunity_status)
        await db.commit()
        return db_opportunity_status
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not delete Opportunity Status")
        raise e
