from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.api.deps import get_db
from app.core.security import require_permission
from app.models.user import User
from app.responses.opportunity_status import (
    CreateOpportunityStatusResponse,
    DeleteOpportunityStatusResponse,
    GetOpportunityStatusResponse,
    UpdateOpportunityStatusResponse,
)
from app.schemas.opportunity_status import OpportunityStatusCreate, OpportunityStatusUpdate
from app.services.opportunity_status import (
    handle_create_opportunity_status,
    handle_delete_opportunity_status,
    handle_get_all_opportunity_statuses,
    handle_get_opportunity_status_by_id,
    handle_update_opportunity_status,
)

opportunity_status_router = APIRouter(prefix="/opportunity-status", tags=["Pipeline Status"])


@opportunity_status_router.get("/")
async def get_all_opportunity_statuses(
    search: str | None = None,
    page: int = 1,
    limit: int = 10,
    current_user: User = Depends(require_permission("pipeline_status", "read")),
    db: AsyncSession = Depends(get_db),
):
    response: GetOpportunityStatusResponse = await handle_get_all_opportunity_statuses(db, current_user, search, page, limit)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )


@opportunity_status_router.get("/{id}")
async def get_opportunity_status_by_id(
    id: UUID,
    current_user: User = Depends(require_permission("pipeline_status", "read")),
    db: AsyncSession = Depends(get_db),
):
    response: GetOpportunityStatusResponse = await handle_get_opportunity_status_by_id(db, current_user, id)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )


@opportunity_status_router.post("/")
async def create_opportunity_status(
    opportunity_status: OpportunityStatusCreate,
    current_user: User = Depends(require_permission("pipeline_status", "create")),
    db: AsyncSession = Depends(get_db),
):
    response: CreateOpportunityStatusResponse = await handle_create_opportunity_status(db, current_user, opportunity_status)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )


@opportunity_status_router.put("/{id}")
async def update_opportunity_status(
    id: UUID,
    opportunity_status: OpportunityStatusUpdate,
    current_user: User = Depends(require_permission("pipeline_status", "update")),
    db: AsyncSession = Depends(get_db),
):
    response: UpdateOpportunityStatusResponse = await handle_update_opportunity_status(db, current_user, opportunity_status, id)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )


@opportunity_status_router.delete("/{id}")
async def delete_opportunity_status(
    id: UUID,
    current_user: User = Depends(require_permission("pipeline_status", "delete")),
    db: AsyncSession = Depends(get_db),
):
    response: DeleteOpportunityStatusResponse = await handle_delete_opportunity_status(db, current_user, id)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )
