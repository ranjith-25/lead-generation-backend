from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.opportunity import OpportunityRead, OpportunityCreate
from app.services.db.opportunity import get_opportunity_by_id
from app.responses.base import BaseResponse

async def get_opportunity_service(db: AsyncSession, opportunityID: str) -> OpportunityRead:
    try:
        opp_id = UUID(opportunityID)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid Opportunity ID format")

    opportunity = await get_opportunity_by_id(db, opp_id)
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
        
    return OpportunityRead.model_validate(opportunity)

async def create_opportunity_service(db: AsyncSession, opp_data: OpportunityCreate) -> OpportunityRead:
    from app.models.opportunity import Opportunity
    from app.services.db.opportunity import addOpportunity
    
    new_opp = Opportunity(**opp_data.model_dump())
    saved_opp = await addOpportunity(new_opp, db)
    return OpportunityRead.model_validate(saved_opp)

async def update_opportunity_service(db: AsyncSession, opportunityID: str, opp_data: OpportunityCreate) -> OpportunityRead:
    from app.services.db.opportunity import update_opportunity_db
    
    try:
        opp_id = UUID(opportunityID)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid Opportunity ID format")

    opportunity = await get_opportunity_by_id(db, opp_id)
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
        
    updated_opp = await update_opportunity_db(db, opportunity, opp_data.model_dump())
    return OpportunityRead.model_validate(updated_opp)

async def delete_opportunity_service(db: AsyncSession, opportunityID: str) -> BaseResponse:
    from app.services.db.opportunity import delete_opportunity_db
    
    try:
        opp_id = UUID(opportunityID)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid Opportunity ID format")

    opportunity = await get_opportunity_by_id(db, opp_id)
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
        
    await delete_opportunity_db(db, opportunity)
    return BaseResponse(success=True, message="Opportunity deleted successfully")
