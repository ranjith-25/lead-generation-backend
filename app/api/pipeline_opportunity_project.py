from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.api.deps import get_db
from app.core.security import require_permission
from app.models.user import User
from app.responses.pipeline_opportunity_project import (
    CreatePipelineOpportunityProjectResponse,
    DeletePipelineOpportunityProjectResponse,
    GetPipelineOpportunityProjectResponse,
    UpdatePipelineOpportunityProjectResponse,
)
from app.schemas.pipeline_opportunity_project import (
    PipelineOpportunityProjectCreate,
    PipelineOpportunityProjectUpdate,
)
from app.services.pipeline_opportunity_project import (
    handle_create_pipeline_opportunity_project,
    handle_delete_pipeline_opportunity_project,
    handle_get_all_pipeline_opportunity_projects,
    handle_get_pipeline_opportunity_project_by_id,
    handle_update_pipeline_opportunity_project,
    handle_get_pipeline_opportunity_project_by_opportunity_id
)

pipeline_opportunity_project_router = APIRouter(prefix="/pipeline-opportunity-project", tags=["Pipeline Opportunity Project"])


@pipeline_opportunity_project_router.get("/")
async def get_all_pipeline_opportunity_projects(
    page: int = 1,
    limit: int = 10,
    current_user: User = Depends(require_permission("pipeline_opportunity_project", "read")),
    db: AsyncSession = Depends(get_db),
):
    response: GetPipelineOpportunityProjectResponse = await handle_get_all_pipeline_opportunity_projects(db, current_user, page, limit)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )


@pipeline_opportunity_project_router.get("/{id}")
async def get_pipeline_opportunity_project_by_id(
    id: UUID,
    current_user: User = Depends(require_permission("pipeline_opportunity_project", "read")),
    db: AsyncSession = Depends(get_db),
):
    response: GetPipelineOpportunityProjectResponse = await handle_get_pipeline_opportunity_project_by_id(db, current_user, id)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )


@pipeline_opportunity_project_router.get("/opportunity/{opportunity_id}")
async def get_pipeline_opportunity_project_by_opportunity_id(
    opportunity_id: UUID,
    current_user: User = Depends(require_permission("pipeline_opportunity_project", "read")),
    db: AsyncSession = Depends(get_db),
):
    response: GetPipelineOpportunityProjectResponse = await handle_get_pipeline_opportunity_project_by_opportunity_id(db, current_user, opportunity_id)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )



@pipeline_opportunity_project_router.post("/")
async def create_pipeline_opportunity_project(
    pipeline_opportunity_project: PipelineOpportunityProjectCreate,
    current_user: User = Depends(require_permission("pipeline_opportunity_project", "create")),
    db: AsyncSession = Depends(get_db),
):
    response: CreatePipelineOpportunityProjectResponse = await handle_create_pipeline_opportunity_project(db, current_user, pipeline_opportunity_project)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )


@pipeline_opportunity_project_router.put("/{id}")
async def update_pipeline_opportunity_project(
    id: UUID,
    pipeline_opportunity_project: PipelineOpportunityProjectUpdate,
    current_user: User = Depends(require_permission("pipeline_opportunity_project", "update")),
    db: AsyncSession = Depends(get_db),
):
    response: UpdatePipelineOpportunityProjectResponse = await handle_update_pipeline_opportunity_project(db, current_user, pipeline_opportunity_project, id)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )


@pipeline_opportunity_project_router.delete("/{id}")
async def delete_pipeline_opportunity_project(
    id: UUID,
    current_user: User = Depends(require_permission("pipeline_opportunity_project", "delete")),
    db: AsyncSession = Depends(get_db),
):
    response: DeletePipelineOpportunityProjectResponse = await handle_delete_pipeline_opportunity_project(db, current_user, id)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )
