from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.opportunity import OpportunityRead, OpportunityListRead, OpportunityCreate, OpportunityFilterRequest, OpportunityFilterValuesResponse, OpportunityPaginatedResponse, OpportunityStatusRead
from app.services.db.opportunity import Opportunity, get_opportunity_by_id, get_all_opportunities, addOpportunity, update_opportunity_db, delete_opportunity_db, get_opportunity_filter_values
from app.responses.base import BaseResponse
from app.responses.opportunity import CreateOpportunityResponse
from app.schemas.ai import AIManualJDRequest
from app.services.ai import handleGetManualScrapedData
import math
from fastapi import BackgroundTasks

async def get_all_opportunities_service(db: AsyncSession, user_id: UUID, filters: OpportunityFilterRequest | None = None) -> OpportunityPaginatedResponse:

    opportunities, total = await get_all_opportunities(db, user_id, filters)
    data = [OpportunityListRead.model_validate(opp) for opp in opportunities]
    
    page = filters.page if filters else 1
    size = filters.size if filters else 10
    total_pages = math.ceil(total / size) if total > 0 else 1

    return OpportunityPaginatedResponse(
        data=data,
        total=total,
        page=page,
        size=size,
        total_pages=total_pages
    )

async def get_opportunity_filter_values_service(db: AsyncSession, user_id: UUID) -> OpportunityFilterValuesResponse:
    
    filter_data = await get_opportunity_filter_values(db, user_id)
    return OpportunityFilterValuesResponse(**filter_data)

async def get_opportunity_service(db: AsyncSession, opportunityID: UUID | str, user_id: UUID) -> OpportunityRead:

    try:
        opp_id = UUID(str(opportunityID))
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid Opportunity ID format")

    opportunity = await get_opportunity_by_id(db, opp_id, user_id)
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found or unauthorized")
        
    return OpportunityRead.model_validate(opportunity)

async def create_opportunity_service(db: AsyncSession, opp_data: OpportunityCreate, user_id: UUID,background_tasks : BackgroundTasks) -> CreateOpportunityResponse:

    try:
        opp_dict = opp_data.model_dump()
        request : AIManualJDRequest = AIManualJDRequest(
            company_name = opp_data.company,
            company_website = opp_data.company_website,
            job_title = opp_data.title,
            experience = opp_data.experience,
            job_description = opp_data.description,
            additional_notes = opp_data.additional_notes
        )

        response : CreateOpportunityResponse = await handleGetManualScrapedData(
            AIManualJDRequest = request,
            db = db,
            user_id = user_id,
            background_tasks = background_tasks
        )
        return response
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error creating opportunity: {str(exc)}")

async def update_opportunity_service(db: AsyncSession, opportunityID: UUID | str, opp_data: OpportunityCreate, user_id: UUID) -> OpportunityRead:

    try:
        opp_id = UUID(str(opportunityID))
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid Opportunity ID format")

    opportunity = await get_opportunity_by_id(db, opp_id, user_id)
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found or unauthorized")
        
    update_dict = opp_data.model_dump()
    update_dict['updatedBy'] = user_id
    updated_opp = await update_opportunity_db(db, opportunity, update_dict)
    return OpportunityRead.model_validate(updated_opp)

async def delete_opportunity_service(db: AsyncSession, opportunityID: UUID | str, user_id: UUID) -> BaseResponse:

    try:
        opp_id = UUID(str(opportunityID))
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid Opportunity ID format")

    opportunity = await get_opportunity_by_id(db, opp_id, user_id)
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found or unauthorized")
        
    await delete_opportunity_db(db, opportunity)
    return BaseResponse(success=True, message="Opportunity deleted successfully")


async def get_opportunity_statuses_service(db: AsyncSession) -> list[OpportunityStatusRead]:
    from app.services.db.opportunity import get_all_opportunity_statuses_db
    statuses = await get_all_opportunity_statuses_db(db)
    return [OpportunityStatusRead.model_validate(status) for status in statuses]

async def update_opportunity_status_service(db: AsyncSession, opportunityID: UUID | str, status_id: UUID, user_id: UUID) -> OpportunityRead:
    try:
        opp_id = UUID(str(opportunityID))
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid Opportunity ID format")

    opportunity = await get_opportunity_by_id(db, opp_id, user_id)
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found or unauthorized")
        
    # verify status exists
    from app.services.db.opportunity import get_all_opportunity_statuses_db
    statuses = await get_all_opportunity_statuses_db(db)
    valid_status_ids = [s.id for s in statuses]
    if status_id not in valid_status_ids:
        raise HTTPException(status_code=400, detail="Invalid status_id")

    update_dict = {"status_id": status_id, "updatedBy": user_id}
    updated_opp = await update_opportunity_db(db, opportunity, update_dict)
    return OpportunityRead.model_validate(updated_opp)
