from app.models.opportunity import Opportunity
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

async def addOpportunity(opportunity : Opportunity,db: AsyncSession) -> Opportunity:
    db.add(opportunity)
    await db.commit()
    await db.refresh(opportunity)
    return opportunity

async def get_all_opportunities(db: AsyncSession, user_id) -> list[Opportunity]:
    result = await db.execute(select(Opportunity).where(Opportunity.user_id == user_id))
    return list(result.scalars().all())


async def get_opportunity_by_id(db: AsyncSession, opportunity_id, user_id) -> Opportunity | None:
    result = await db.execute(select(Opportunity).where(Opportunity.opportunityID == opportunity_id, Opportunity.user_id == user_id))
    return result.scalars().first()

async def update_opportunity_db(db: AsyncSession, opportunity: Opportunity, update_data: dict) -> Opportunity:
    for key, value in update_data.items():
        setattr(opportunity, key, value)
    db.add(opportunity)
    await db.commit()
    await db.refresh(opportunity)
    return opportunity

async def delete_opportunity_db(db: AsyncSession, opportunity: Opportunity) -> None:
    await db.delete(opportunity)
    await db.commit()
