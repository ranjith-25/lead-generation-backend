from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse
from fastapi import status
from uuid import UUID

from app.api.deps import get_current_user
from app.config import PageName, SortOrder, TimeRange
from app.core.connections.postgres import get_db
from app.core.security import require_permission
from app.models.user import User
from app.schemas.opportunity import (
    OpportunityRead, 
    OpportunityListRead, 
    OpportunityCreate,
    OpportunityPatch,
    OpportunityFilterRequest,
    OpportunityFilterValuesResponse, 
    OpportunityPaginatedResponse,
    OpportunityStatusRead,
    OpportunityStatusUpdate
)
from app.schemas.opportunity_edit_history import OpportunityEditHistoryPaginatedResponse
from app.responses.base import BaseResponse
from app.services.opportunity_edit_history import get_opportunity_edit_history_service
from app.services.opportunity import (
    get_opportunity_service, 
    create_opportunity_service, 
    update_opportunity_service,
    patch_opportunity_service,
    delete_opportunity_service,
    get_all_opportunities_service, 
    get_opportunity_filter_values_service,
    get_opportunity_statuses_service,
    update_opportunity_status_service
)
from fastapi import BackgroundTasks
from app.responses.opportunity import CreateOpportunityResponse

router = APIRouter(prefix="/opportunities", tags=["Opportunities"])


@router.post("", response_model=CreateOpportunityResponse, status_code=status.HTTP_201_CREATED)
async def create_opportunity(
    opp_data: OpportunityCreate,
    background_tasks : BackgroundTasks,
    current_user: User = Depends(require_permission("overview_and_analysis","create")), 
    db: AsyncSession = Depends(get_db)
) -> CreateOpportunityResponse:
    return await create_opportunity_service(db, opp_data, current_user.user_id,background_tasks)


@router.get("", response_model=OpportunityPaginatedResponse)
async def get_opportunities(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    time_filter: TimeRange | None = Query(None),
    sort_by: str | None = Query(None, description="Field to sort on; unsupported names are ignored"),
    order_by: SortOrder | None = Query(None),
    current_user: User = Depends(require_permission("overview_and_analysis","read")), db: AsyncSession = Depends(get_db)
) -> OpportunityPaginatedResponse:
    return await get_all_opportunities_service(
        db,
        current_user.user_id,
        OpportunityFilterRequest(
            page=page,
            size=size,
            time_filter=time_filter,
            sort_by=sort_by,
            order_by=order_by,
        ),
    )


@router.get("/filter-values", response_model=OpportunityFilterValuesResponse)
async def get_filter_values(
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
) -> OpportunityFilterValuesResponse:
    return await get_opportunity_filter_values_service(db, current_user.user_id)


@router.get("/status/all", response_model=list[OpportunityStatusRead])
async def get_opportunity_statuses(
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
) -> list[OpportunityStatusRead]:
    return await get_opportunity_statuses_service(db)


@router.patch("/{opportunityID}/status", response_model=OpportunityRead)
async def update_opportunity_status(
    opportunityID: UUID,
    status_data: OpportunityStatusUpdate,
    current_user: User = Depends(require_permission("overview_and_analysis","update")), 
    db: AsyncSession = Depends(get_db)
) -> OpportunityRead:
    return await update_opportunity_status_service(db, opportunityID, status_data.status_id, current_user.user_id)


@router.get("/{opportunityID}/edit-history", response_model=OpportunityEditHistoryPaginatedResponse)
async def get_opportunity_edit_history(
    opportunityID: UUID,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    page_name: PageName | None = Query(None, description="Filter to one screen; defaults to all"),
    current_user: User = Depends(require_permission("overview_and_analysis","read")),
    db: AsyncSession = Depends(get_db)
) -> OpportunityEditHistoryPaginatedResponse:
    return await get_opportunity_edit_history_service(db, opportunityID, current_user.user_id, page_name, page, size)


@router.get("/{opportunityID}", response_model=OpportunityRead)
async def get_opportunity(
    opportunityID: UUID,
    current_user: User = Depends(require_permission("overview_and_analysis","read")), 
    db: AsyncSession = Depends(get_db)
) -> OpportunityRead:
    return await get_opportunity_service(db, opportunityID, current_user.user_id)


@router.put("/{opportunityID}", response_model=OpportunityRead)
async def update_opportunity(
    opportunityID: UUID,
    opp_data: OpportunityCreate,
    current_user: User = Depends(require_permission("overview_and_analysis","update")), 
    db: AsyncSession = Depends(get_db)
) -> OpportunityRead:
    return await update_opportunity_service(db, opportunityID, opp_data, current_user.user_id)


@router.patch("/{opportunityID}", response_model=OpportunityRead)
async def patch_opportunity(
    opportunityID: UUID,
    opp_data: OpportunityPatch,
    current_user: User = Depends(require_permission("overview_and_analysis","update")),
    db: AsyncSession = Depends(get_db)
) -> OpportunityRead:
    return await patch_opportunity_service(db, opportunityID, opp_data, current_user.user_id)


@router.delete("/{opportunityID}", response_model=BaseResponse)
async def delete_opportunity(
    opportunityID: UUID,
    current_user: User = Depends(require_permission("overview_and_analysis","delete")), 
    db: AsyncSession = Depends(get_db)
) -> BaseResponse:
    return await delete_opportunity_service(db, opportunityID, current_user.user_id)


@router.post("/all", response_model=OpportunityPaginatedResponse)
async def get_all_opportunities_filtered(
    filters: OpportunityFilterRequest,
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
) -> OpportunityPaginatedResponse:
    return await get_all_opportunities_service(db, current_user.user_id, filters)
