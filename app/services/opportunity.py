from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.opportunity import OpportunityRead, OpportunityListRead, OpportunityCreate, OpportunityPatch, OpportunityFilterRequest, OpportunityFilterValuesResponse, OpportunityPaginatedResponse, OpportunityStatusRead
from app.services.db.opportunity import Opportunity, get_opportunity_by_id, get_all_opportunities, addOpportunity, update_opportunity_db, delete_opportunity_db, get_opportunity_filter_values, get_all_opportunity_statuses_db
from app.services.db.user import get_user_by_id
from app.services.opportunity_edit_history import record_opportunity_edit
from app.config import LogAction
from app.services.system_log import log_activity
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
        from app.services.db.opportunity import get_status_by_name
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
    # Staged before the update lands so the diff still sees the old values; the commit
    # inside update_opportunity_db covers both rows.
    await record_opportunity_edit(db, opportunity, update_dict, user_id)
    await log_activity(
        db,
        LogAction.OPPORTUNITY_STATUS_CHANGED
        if update_dict.get("status_id") not in (None, opportunity.status_id)
        else LogAction.OPPORTUNITY_UPDATED,
        user_id,
        entity_type="opportunity",
        entity_id=opportunity.opportunityID,
        entity_name=opportunity.title,
        details={"fields": sorted(k for k in update_dict if k != "updatedBy")},
    )
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
        
    # Captured before the delete so the log keeps the identifiers the row is about to lose.
    await log_activity(
        db,
        LogAction.OPPORTUNITY_DELETED,
        user_id,
        entity_type="opportunity",
        entity_id=opportunity.opportunityID,
        entity_name=opportunity.title,
        details={"company": opportunity.company, "role": opportunity.role},
    )
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
    await record_opportunity_edit(db, opportunity, update_dict, user_id)
    await log_activity(
        db,
        LogAction.OPPORTUNITY_STATUS_CHANGED,
        user_id,
        entity_type="opportunity",
        entity_id=opportunity.opportunityID,
        entity_name=opportunity.title,
        details={"from_status_id": opportunity.status_id, "to_status_id": status_id},
    )
    updated_opp = await update_opportunity_db(db, opportunity, update_dict)
    return OpportunityRead.model_validate(updated_opp)

PATCH_NON_NULLABLE_FIELDS = ("title", "status_id")

async def patch_opportunity_service(db: AsyncSession, opportunityID: UUID | str, opp_data: OpportunityPatch, user_id: UUID) -> OpportunityRead:

    try:
        opp_id = UUID(str(opportunityID))
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid Opportunity ID format")

    opportunity = await get_opportunity_by_id(db, opp_id, user_id)
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found or unauthorized")

    update_dict = opp_data.model_dump(exclude_unset=True)
    if not update_dict:
        return OpportunityRead.model_validate(opportunity)

    for field in PATCH_NON_NULLABLE_FIELDS:
        if field in update_dict and update_dict[field] is None:
            raise HTTPException(status_code=400, detail=f"'{field}' cannot be set to null")

    if update_dict.get("status_id") is not None:
        statuses = await get_all_opportunity_statuses_db(db)
        if update_dict["status_id"] not in [s.id for s in statuses]:
            raise HTTPException(status_code=400, detail="Invalid status_id")

    if update_dict.get("assigned_to") is not None:
        if not await get_user_by_id(db, update_dict["assigned_to"]):
            raise HTTPException(status_code=400, detail="Invalid assigned_to user")

    update_dict['updatedBy'] = user_id
    await record_opportunity_edit(db, opportunity, update_dict, user_id)
    await log_activity(
        db,
        LogAction.OPPORTUNITY_STATUS_CHANGED
        if update_dict.get("status_id") not in (None, opportunity.status_id)
        else LogAction.OPPORTUNITY_UPDATED,
        user_id,
        entity_type="opportunity",
        entity_id=opportunity.opportunityID,
        entity_name=opportunity.title,
        details={"fields": sorted(k for k in update_dict if k != "updatedBy")},
    )
    updated_opp = await update_opportunity_db(db, opportunity, update_dict)
    return OpportunityRead.model_validate(updated_opp)
