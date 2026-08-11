from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.api.deps import get_db
from app.core.security import require_permission
from app.models.user import User
from app.responses.pipeline_opportunity_resource import (
    CreatePipelineOpportunityResourceResponse,
    DeletePipelineOpportunityResourceResponse,
    GetPipelineOpportunityResourceResponse,
    UpdatePipelineOpportunityResourceResponse,
)
from app.schemas.pipeline_opportunity_resource import (
    PipelineOpportunityResourceCreate,
    PipelineOpportunityResourceUpdate,
    PipelineOpportunityResourceSelectRequest
)
from app.services.pipeline_opportunity_resource import (
    handle_create_pipeline_opportunity_resource,
    handle_delete_pipeline_opportunity_resource,
    handle_get_all_pipeline_opportunity_resources,
    handle_get_pipeline_opportunity_resource_by_id,
    handle_update_pipeline_opportunity_resource,
    handle_get_pipeline_opportunity_resource_by_opportunity_id
)

pipeline_opportunity_resource_router = APIRouter(prefix="/pipeline-opportunity-resource", tags=["Pipeline Opportunity Resource"])


@pipeline_opportunity_resource_router.get("/")
async def get_all_pipeline_opportunity_resources(
    page: int = 1,
    limit: int = 10,
    current_user: User = Depends(require_permission("pipeline_opportunity_resource", "read")),
    db: AsyncSession = Depends(get_db),
):
    response: GetPipelineOpportunityResourceResponse = await handle_get_all_pipeline_opportunity_resources(db, current_user, page, limit)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )


@pipeline_opportunity_resource_router.get("/{id}")
async def get_pipeline_opportunity_resource_by_id(
    id: UUID,
    current_user: User = Depends(require_permission("pipeline_opportunity_resource", "read")),
    db: AsyncSession = Depends(get_db),
):
    response: GetPipelineOpportunityResourceResponse = await handle_get_pipeline_opportunity_resource_by_id(db, current_user, id)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )


@pipeline_opportunity_resource_router.get("/opportunity/{opportunity_id}")
async def get_pipeline_opportunity_resource_by_opportunity_id(
    opportunity_id: UUID,
    current_user: User = Depends(require_permission("pipeline_opportunity_resource", "read")),
    db: AsyncSession = Depends(get_db),
):
    response: GetPipelineOpportunityResourceResponse = await handle_get_pipeline_opportunity_resource_by_opportunity_id(db, current_user, opportunity_id)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )


@pipeline_opportunity_resource_router.post("/")
async def create_pipeline_opportunity_resource(
    pipeline_opportunity_resource: PipelineOpportunityResourceCreate,
    current_user: User = Depends(require_permission("pipeline_opportunity_resource", "create")),
    db: AsyncSession = Depends(get_db),
):
    response: CreatePipelineOpportunityResourceResponse = await handle_create_pipeline_opportunity_resource(db, current_user, pipeline_opportunity_resource)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )


@pipeline_opportunity_resource_router.put("/{id}")
async def update_pipeline_opportunity_resource(
    id: UUID,
    pipeline_opportunity_resource: PipelineOpportunityResourceUpdate,
    current_user: User = Depends(require_permission("pipeline_opportunity_resource", "update")),
    db: AsyncSession = Depends(get_db),
):
    response: UpdatePipelineOpportunityResourceResponse = await handle_update_pipeline_opportunity_resource(db, current_user, pipeline_opportunity_resource, id)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )


@pipeline_opportunity_resource_router.delete("/{id}")
async def delete_pipeline_opportunity_resource(
    id: UUID,
    current_user: User = Depends(require_permission("pipeline_opportunity_resource", "delete")),
    db: AsyncSession = Depends(get_db),
):
    response: DeletePipelineOpportunityResourceResponse = await handle_delete_pipeline_opportunity_resource(db, current_user, id)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )

