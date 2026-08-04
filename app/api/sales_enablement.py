from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.sales_enablement import SalesEnablementRead, SalesEnablementCreate
from app.responses.base import BaseResponse
from app.services.sales_enablement import (
    get_sales_enablement_service,
    get_sales_enablement_by_opp_service,
    create_sales_enablement_service,
    update_sales_enablement_service,
    delete_sales_enablement_service
)

router = APIRouter(prefix="/sales-enablement", tags=["Sales Enablement"])


@router.post("", response_model=SalesEnablementRead, status_code=status.HTTP_201_CREATED)
async def create_sales_enablement(
    se_data: SalesEnablementCreate,
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
) -> SalesEnablementRead:
    return await create_sales_enablement_service(db, se_data, current_user.user_id)


@router.get("/opportunity/{opportunityID}", response_model=SalesEnablementRead)
async def get_sales_enablement_by_opp(
    opportunityID: int,
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> SalesEnablementRead:
    return await get_sales_enablement_by_opp_service(db, opportunityID, current_user.user_id)


@router.get("/{id}", response_model=SalesEnablementRead)
async def get_sales_enablement(
    id: int,
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
) -> SalesEnablementRead:
    return await get_sales_enablement_service(db, id, current_user.user_id)


@router.put("/{id}", response_model=SalesEnablementRead)
async def update_sales_enablement(
    id: int,
    se_data: SalesEnablementCreate,
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
) -> SalesEnablementRead:
    return await update_sales_enablement_service(db, id, se_data, current_user.user_id)


@router.delete("/{id}", response_model=BaseResponse)
async def delete_sales_enablement(
    id: int,
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
) -> BaseResponse:
    return await delete_sales_enablement_service(db, id, current_user.user_id)
