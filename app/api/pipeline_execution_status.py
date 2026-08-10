from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.api.deps import get_db
from app.core.security import require_permission
from app.models.user import User
from app.responses.pipeline_execution_status import (
    CreatePipelineExecutionStatusResponse,
    DeletePipelineExecutionStatusResponse,
    GetPipelineExecutionStatusResponse,
    UpdatePipelineExecutionStatusResponse,
)
from app.schemas.pipeline_execution_status import (
    PipelineExecutionStatusCreate,
    PipelineExecutionStatusUpdate,
)
from app.services.pipeline_execution_status import (
    handle_create_pipeline_execution_status,
    handle_delete_pipeline_execution_status,
    handle_get_all_pipeline_execution_statuses,
    handle_get_pipeline_execution_status_by_id,
    handle_update_pipeline_execution_status,
    handle_get_pipeline_execution_status_by_opportunity_id
)

pipeline_execution_status_router = APIRouter(prefix="/pipeline-execution-status", tags=["Pipeline Execution Status"])


@pipeline_execution_status_router.get("/")
async def get_all_pipeline_execution_statuses(
    page: int = 1,
    limit: int = 10,
    current_user: User = Depends(require_permission("pipeline_execution_status", "read")),
    db: AsyncSession = Depends(get_db),
):
    response: GetPipelineExecutionStatusResponse = await handle_get_all_pipeline_execution_statuses(db, current_user, page, limit)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )


@pipeline_execution_status_router.get("/{id}")
async def get_pipeline_execution_status_by_id(
    id: UUID,
    current_user: User = Depends(require_permission("pipeline_execution_status", "read")),
    db: AsyncSession = Depends(get_db),
):
    response: GetPipelineExecutionStatusResponse = await handle_get_pipeline_execution_status_by_id(db, current_user, id)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )


@pipeline_execution_status_router.get("/opportunity/{opportunity_id}")
async def get_pipeline_execution_status_by_opportunity_id(
    opportunity_id: UUID,
    current_user: User = Depends(require_permission("pipeline_execution_status", "read")),
    db: AsyncSession = Depends(get_db),
):
    response: GetPipelineExecutionStatusResponse = await handle_get_pipeline_execution_status_by_opportunity_id(db, current_user, opportunity_id)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )


@pipeline_execution_status_router.post("/")
async def create_pipeline_execution_status(
    pipeline_execution_status: PipelineExecutionStatusCreate,
    current_user: User = Depends(require_permission("pipeline_execution_status", "create")),
    db: AsyncSession = Depends(get_db),
):
    response: CreatePipelineExecutionStatusResponse = await handle_create_pipeline_execution_status(db, current_user, pipeline_execution_status)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )


@pipeline_execution_status_router.put("/{id}")
async def update_pipeline_execution_status(
    id: UUID,
    pipeline_execution_status: PipelineExecutionStatusUpdate,
    current_user: User = Depends(require_permission("pipeline_execution_status", "update")),
    db: AsyncSession = Depends(get_db),
):
    response: UpdatePipelineExecutionStatusResponse = await handle_update_pipeline_execution_status(db, current_user, pipeline_execution_status, id)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )


@pipeline_execution_status_router.delete("/{id}")
async def delete_pipeline_execution_status(
    id: UUID,
    current_user: User = Depends(require_permission("pipeline_execution_status", "delete")),
    db: AsyncSession = Depends(get_db),
):
    response: DeletePipelineExecutionStatusResponse = await handle_delete_pipeline_execution_status(db, current_user, id)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )
