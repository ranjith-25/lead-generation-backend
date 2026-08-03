from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse
from fastapi import status

from app.api.deps import get_current_user
from app.core.connections.postgres import get_db
from app.models.user import User
from app.schemas.opportunity import OpportunityRead, OpportunityCreate
from app.responses.base import BaseResponse
from app.services.opportunity import get_opportunity_service, create_opportunity_service, update_opportunity_service, delete_opportunity_service

router = APIRouter(prefix="/opportunities", tags=["Opportunities"])


@router.post("", response_model=OpportunityRead, status_code=status.HTTP_201_CREATED)
async def create_opportunity(
    opp_data: OpportunityCreate,
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
) -> OpportunityRead:
    return await create_opportunity_service(db, opp_data, current_user.user_id)


@router.get("", response_model=list[OpportunityRead])
async def get_opportunities(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> list[OpportunityRead]:
    from app.services.opportunity import get_all_opportunities_service
    return await get_all_opportunities_service(db, current_user.user_id)


@router.get("/{opportunityID}", response_model=OpportunityRead)
async def get_opportunity(
    opportunityID: str,
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
) -> OpportunityRead:
    return await get_opportunity_service(db, opportunityID, current_user.user_id)


@router.put("/{opportunityID}", response_model=OpportunityRead)
async def update_opportunity(
    opportunityID: str,
    opp_data: OpportunityCreate,
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
) -> OpportunityRead:
    return await update_opportunity_service(db, opportunityID, opp_data, current_user.user_id)


@router.delete("/{opportunityID}", response_model=BaseResponse)
async def delete_opportunity(
    opportunityID: str,
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
) -> BaseResponse:
    return await delete_opportunity_service(db, opportunityID, current_user.user_id)
