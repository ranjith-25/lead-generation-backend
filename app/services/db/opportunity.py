from app.models.opportunity import Opportunity
from sqlalchemy.ext.asyncio import AsyncSession

async def addOpportunity(opportunity : Opportunity,db: AsyncSession) -> dict:
    db.add(opportunity)
    await db.commit()
    await db.refresh(opportunity)
    return opportunity
