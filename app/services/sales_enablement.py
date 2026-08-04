from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.sales_enablement import SalesEnablementRead, SalesEnablementCreate
from app.responses.base import BaseResponse
from app.models.sales_enablement import SalesEnablement
from app.services.db.opportunity import get_opportunity_by_id
from app.services.db.sales_enablement import get_sales_enablement_by_id_db, get_sales_enablement_by_opp_db, add_sales_enablement_db, update_sales_enablement_db, delete_sales_enablement_db

async def check_opportunity_access(db: AsyncSession, opportunity_id: int, user_id: int) -> None:

    opportunity = await get_opportunity_by_id(db, opportunity_id, user_id)
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found or unauthorized")

async def get_sales_enablement_service(db: AsyncSession, se_id: int | str, user_id: int) -> SalesEnablementRead:
    
    try:
        parsed_id = int(se_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid Sales Enablement ID format")

    se = await get_sales_enablement_by_id_db(db, parsed_id)
    if not se:
        raise HTTPException(status_code=404, detail="Sales Enablement not found")
        
    await check_opportunity_access(db, se.opportunityID, user_id)
    
    return SalesEnablementRead.model_validate(se)

async def get_sales_enablement_by_opp_service(db: AsyncSession, opp_id: int | str, user_id: int) -> SalesEnablementRead:
    
    try:
        parsed_opp_id = int(opp_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid Opportunity ID format")

    await check_opportunity_access(db, parsed_opp_id, user_id)

    se = await get_sales_enablement_by_opp_db(db, parsed_opp_id)
    if not se:
        raise HTTPException(status_code=404, detail="Sales Enablement not found for this opportunity")
        
    return SalesEnablementRead.model_validate(se)

async def create_sales_enablement_service(db: AsyncSession, se_data: SalesEnablementCreate, user_id: int) -> SalesEnablementRead:

    await check_opportunity_access(db, se_data.opportunityID, user_id)

    existing = await get_sales_enablement_by_opp_db(db, se_data.opportunityID)
    if existing:
        raise HTTPException(status_code=400, detail="Sales Enablement already exists for this opportunity")
    
    se_dict = se_data.model_dump()
    se_dict['createdBy'] = user_id
    se_dict['updatedBy'] = user_id
    new_se = SalesEnablement(**se_dict)
    saved_se = await add_sales_enablement_db(db, new_se)
    return SalesEnablementRead.model_validate(saved_se)

async def update_sales_enablement_service(db: AsyncSession, se_id: int | str, se_data: SalesEnablementCreate, user_id: int) -> SalesEnablementRead:
    
    try:
        parsed_id = int(se_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid Sales Enablement ID format")

    se = await get_sales_enablement_by_id_db(db, parsed_id)
    if not se:
        raise HTTPException(status_code=404, detail="Sales Enablement not found")

    await check_opportunity_access(db, se.opportunityID, user_id)
    
    # Don't allow changing the opportunity ID
    update_dict = se_data.model_dump(exclude={'opportunityID'}, exclude_unset=True)
    update_dict['updatedBy'] = user_id
    
    updated_se = await update_sales_enablement_db(db, se, update_dict)
    return SalesEnablementRead.model_validate(updated_se)

async def delete_sales_enablement_service(db: AsyncSession, se_id: int | str, user_id: int) -> BaseResponse:
    
    try:
        parsed_id = int(se_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid Sales Enablement ID format")

    se = await get_sales_enablement_by_id_db(db, parsed_id)
    if not se:
        raise HTTPException(status_code=404, detail="Sales Enablement not found")

    await check_opportunity_access(db, se.opportunityID, user_id)
        
    await delete_sales_enablement_db(db, se)
    return BaseResponse(success=True, message="Sales Enablement deleted successfully")
