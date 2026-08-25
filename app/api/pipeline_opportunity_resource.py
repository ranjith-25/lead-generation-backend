from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.api.deps import get_db
from app.core.security import require_permission
from app.models.user import User
from app.responses.pipeline_opportunity_resource import (
    AssignPipelineOpportunityResourcesResponse,
    CreatePipelineOpportunityResourceResponse,
    DeletePipelineOpportunityResourceResponse,
    GetPipelineOpportunityResourceResponse,
    UpdatePipelineOpportunityResourceResponse,
    SelectPipelineOpportunityResourcesResponse
)
from app.schemas.pipeline_opportunity_resource import (
    PipelineOpportunityResourceCreate,
    PipelineOpportunityResourceUpdate,
    PipelineOpportunityResourceSelectRequest,
    PipelineOpportunityResourceAssignToTLRequest,
    PipelineOpportunityResourceApproveRequest,
    PipelineOpportunityResourceAutoApproveRequest,
    PipelineOpportunityResourceRejectRequest,
)
from app.services.pipeline_opportunity_resource import (
    handle_create_pipeline_opportunity_resource,
    handle_delete_pipeline_opportunity_resource,
    handle_get_all_pipeline_opportunity_resources,
    handle_get_pipeline_opportunity_resource_by_id,
    handle_update_pipeline_opportunity_resource,
    handle_get_pipeline_opportunity_resource_by_opportunity_id,
    handle_select_pipeline_opportunity_resource,
    handle_assign_pipeline_opportunity_resource_to_tl,
    handle_approve_pipeline_opportunity_resource,
    handle_auto_approve_pipeline_opportunity_resource,
    handle_reject_pipeline_opportunity_resource,
)
from fastapi import BackgroundTasks


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


@pipeline_opportunity_resource_router.patch("/select")
async def select_pipeline_opportunity_resource(
    request: PipelineOpportunityResourceSelectRequest,
    current_user: User = Depends(require_permission("pipeline_opportunity_resource", "select_resource")),
    db: AsyncSession = Depends(get_db),
):
    response: SelectPipelineOpportunityResourcesResponse = await handle_select_pipeline_opportunity_resource(
        db, current_user, request
    )
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )


@pipeline_opportunity_resource_router.patch("/assign")
async def assign_pipeline_opportunity_resource_to_tl(
    request: PipelineOpportunityResourceAssignToTLRequest,
    current_user: User = Depends(require_permission("pipeline_opportunity_resource", "resource_assign_to_tl")),
    db: AsyncSession = Depends(get_db),
):
    response: AssignPipelineOpportunityResourcesResponse = await handle_assign_pipeline_opportunity_resource_to_tl(
        db, current_user, request
    )
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )


@pipeline_opportunity_resource_router.patch("/approve")
async def approve_pipeline_opportunity_resource(
    request: PipelineOpportunityResourceApproveRequest,
    background_tasks : BackgroundTasks,
    current_user: User = Depends(require_permission("pipeline_opportunity_resource", "approve")),
    db: AsyncSession = Depends(get_db),
):
    response: UpdatePipelineOpportunityResourceResponse = await handle_approve_pipeline_opportunity_resource(
        db, current_user, request,background_tasks=background_tasks
    )
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )


@pipeline_opportunity_resource_router.patch("/auto-approve")
async def auto_approve_pipeline_opportunity_resource(
    request: PipelineOpportunityResourceAutoApproveRequest,
    background_tasks : BackgroundTasks,
    current_user: User = Depends(require_permission("pipeline_opportunity_resource", "auto_approve")),
    db: AsyncSession = Depends(get_db),
):
    response: UpdatePipelineOpportunityResourceResponse = await handle_auto_approve_pipeline_opportunity_resource(
        db, current_user, request, background_tasks=background_tasks
    )
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )


@pipeline_opportunity_resource_router.patch("/reject")
async def reject_pipeline_opportunity_resource(
    request: PipelineOpportunityResourceRejectRequest,
    current_user: User = Depends(require_permission("pipeline_opportunity_resource", "reject")),
    db: AsyncSession = Depends(get_db),
):
    response: UpdatePipelineOpportunityResourceResponse = await handle_reject_pipeline_opportunity_resource(
        db, current_user, request
    )
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )


# --- Comments (shared comment service, PageName.RESOURCE_MATCH) ---
from fastapi import Query

from app.config import PageName
from app.responses.base import BaseResponse
from app.responses.comment import CommentResponse
from app.schemas.comment import (
    CommentCreate,
    CommentPaginatedResponse,
    CommentUpdate,
)
from app.services.comment import (
    create_comment_service,
    delete_comment_service,
    get_comments_service,
    update_comment_service,
)


@pipeline_opportunity_resource_router.get("/{id}/comments", response_model=CommentPaginatedResponse)
async def get_pipeline_opportunity_resource_comments(
    id: UUID,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(require_permission("pipeline_opportunity_resource", "read")),
    db: AsyncSession = Depends(get_db),
) -> CommentPaginatedResponse:
    return await get_comments_service(db, PageName.RESOURCE_MATCH, id, current_user, page, size)


@pipeline_opportunity_resource_router.post("/{id}/comments", response_model=CommentResponse)
async def create_pipeline_opportunity_resource_comment(
    id: UUID,
    comment: CommentCreate,
    current_user: User = Depends(require_permission("pipeline_opportunity_resource", "create")),
    db: AsyncSession = Depends(get_db),
) -> CommentResponse:
    return await create_comment_service(db, PageName.RESOURCE_MATCH, id, comment, current_user)


@pipeline_opportunity_resource_router.patch("/{id}/comments/{comment_id}", response_model=CommentResponse)
async def update_pipeline_opportunity_resource_comment(
    id: UUID,
    comment_id: UUID,
    comment: CommentUpdate,
    current_user: User = Depends(require_permission("pipeline_opportunity_resource", "update")),
    db: AsyncSession = Depends(get_db),
) -> CommentResponse:
    return await update_comment_service(db, PageName.RESOURCE_MATCH, id, comment_id, comment, current_user)


@pipeline_opportunity_resource_router.delete("/{id}/comments/{comment_id}", response_model=BaseResponse)
async def delete_pipeline_opportunity_resource_comment(
    id: UUID,
    comment_id: UUID,
    current_user: User = Depends(require_permission("pipeline_opportunity_resource", "delete")),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    return await delete_comment_service(db, PageName.RESOURCE_MATCH, id, comment_id, current_user)
