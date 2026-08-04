from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.opportunity import Opportunity
from app.models.opportunity_status import OpportunityStatus
from app.schemas.opportunity import OpportunityFilterRequest
from app.models.platform import Platform

async def addOpportunity(opportunity : Opportunity,db: AsyncSession) -> Opportunity:
    db.add(opportunity)
    await db.commit()
    await db.refresh(opportunity)
    return opportunity

async def get_all_opportunities(db: AsyncSession, user_id, filters: OpportunityFilterRequest | None = None) -> list[Opportunity]:
    query = select(Opportunity).where(Opportunity.createdBy == user_id)
    
    if filters:
        if filters.platform:
            query = query.where(Opportunity.platform.in_(filters.platform))
        if filters.company:
            query = query.where(Opportunity.company.in_(filters.company))
        if filters.role:
            query = query.where(Opportunity.role.in_(filters.role))
        if filters.location:
            query = query.where(Opportunity.location.in_(filters.location))
        if filters.status:
            query = query.join(Opportunity.status).where(OpportunityStatus.status.in_(filters.status))

    result = await db.execute(query)
    return list(result.scalars().all())

async def get_opportunity_filter_values(db: AsyncSession, user_id) -> dict:
    
    base_query = select(Opportunity).where(Opportunity.createdBy == user_id)
    
    # Fetch all available platforms and statuses from their respective tables
    platforms = await db.execute(select(Platform.name))
    companies = await db.execute(select(Opportunity.company).where(Opportunity.createdBy == user_id, Opportunity.company.is_not(None)).distinct())
    roles = await db.execute(select(Opportunity.role).where(Opportunity.createdBy == user_id, Opportunity.role.is_not(None)).distinct())
    locations = await db.execute(select(Opportunity.location).where(Opportunity.createdBy == user_id, Opportunity.location.is_not(None)).distinct())
    
    # Fetch all available statuses from the database table
    statuses = await db.execute(select(OpportunityStatus.status))
    
    return {
        "platform": [p[0] for p in platforms.all()],
        "company": [c[0] for c in companies.all()],
        "role": [r[0] for r in roles.all()],
        "location": [l[0] for l in locations.all()],
        "status": [s[0] for s in statuses.all()],
    }


async def get_opportunity_by_id(db: AsyncSession, opportunity_id, user_id) -> Opportunity | None:
    result = await db.execute(select(Opportunity).where(Opportunity.opportunityID == opportunity_id, Opportunity.createdBy == user_id))
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
