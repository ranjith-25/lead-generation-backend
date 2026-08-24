import logging
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.models.opportunity_status import OpportunityStatus
from app.models.opportunity import Opportunity
from app.config import OpportunityStatusKey
from app.exceptions.custom import SystemRowMissingException
from app.services.db.system_refs import resolve_opportunity_status_id


async def get_all_opportunity_statuses(db: AsyncSession, search: str | None = None, page: int = 1, limit: int = 10):
    try:
        query = select(
            OpportunityStatus.id,
            OpportunityStatus.status,
            func.count(Opportunity.opportunityID).label('count')
        ).outerjoin(
            Opportunity, OpportunityStatus.id == Opportunity.status_id
        ).where(
            OpportunityStatus.is_active == True
        ).group_by(
            OpportunityStatus.id, OpportunityStatus.status
        )

        if search:
            query = query.where(OpportunityStatus.status.ilike(f"%{search.strip()}%"))

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
        logging.exception("Could not find Opportunity Statuses")
        raise e


async def get_opportunity_status_by_id(db: AsyncSession, opportunity_status_id: UUID):
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


async def update_opportunity_status(db: AsyncSession, update_data: dict, opportunity_status_id: UUID):
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


async def delete_opportunity_status(db: AsyncSession, opportunity_status_id: UUID):
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


async def fetch_new_opportunity_status_id(db: AsyncSession) -> UUID:
    """The id of the `new` opportunity status.

    Matched on `status_key`, so renaming the status in the UI does not break opportunity
    creation. Raises rather than returning None: the caller has no sensible fallback, and a
    named error beats the AttributeError this used to raise when the row was absent.
    """
    status_id = await resolve_opportunity_status_id(db, OpportunityStatusKey.NEW)
    if status_id is None:
        raise SystemRowMissingException("opportunity_status", OpportunityStatusKey.NEW.value)
    return status_id
