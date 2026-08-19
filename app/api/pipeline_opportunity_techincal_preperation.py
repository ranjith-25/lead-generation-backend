from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.api.deps import get_db
from app.config import PageName
from app.core.security import require_permission
from app.models.user import User
from app.responses.base import BaseResponse
from app.responses.comment import CommentResponse
from app.responses.pipeline_opportunity_techincal_preperation import (
    CreatePipelineOpportunityTechnicalPreperationResponse,
    DeletePipelineOpportunityTechnicalPreperationResponse,
    GetPipelineOpportunityTechnicalPreperationResponse,
    UpdatePipelineOpportunityTechnicalPreperationResponse,
)
from app.schemas.comment import (
    CommentCreate,
    CommentPaginatedResponse,
    CommentUpdate,
)
from app.schemas.pipeline_opportunity_techincal_preperation import (
    PipelineOpportunityTechnicalPreperationCreate,
    PipelineOpportunityTechnicalPreperationUpdate,
)
from app.services.comment import (
    create_comment_service,
    delete_comment_service,
    get_comments_service,
    update_comment_service,
)
from app.services.pipeline_opportunity_techincal_preperation import (
    handle_create_pipeline_opportunity_technical_preperation,
    handle_delete_pipeline_opportunity_technical_preperation,
    handle_get_all_pipeline_opportunity_technical_preperations,
    handle_get_pipeline_opportunity_technical_preperation_by_id,
    handle_update_pipeline_opportunity_technical_preperation,
    handle_get_pipeline_opportunity_technical_preperation_by_opportunity_id,
    handle_update_pipeline_opportunity_technical_preperation_comments
)

pipeline_opportunity_technical_preperation_router = APIRouter(prefix="/pipeline-opportunity-technical-preperation", tags=["Pipeline Opportunity Technical Preparation"])


@pipeline_opportunity_technical_preperation_router.get("/")
async def get_all_pipeline_opportunity_technical_preperations(
    page: int = 1,
    limit: int = 10,
    current_user: User = Depends(require_permission("pipeline_opportunity_technical_preperation", "read")),
    db: AsyncSession = Depends(get_db),
):
    response: GetPipelineOpportunityTechnicalPreperationResponse = await handle_get_all_pipeline_opportunity_technical_preperations(db, current_user, page, limit)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )


@pipeline_opportunity_technical_preperation_router.get("/{id}")
async def get_pipeline_opportunity_technical_preperation_by_id(
    id: UUID,
    current_user: User = Depends(require_permission("pipeline_opportunity_technical_preperation", "read")),
    db: AsyncSession = Depends(get_db),
):
    response: GetPipelineOpportunityTechnicalPreperationResponse = await handle_get_pipeline_opportunity_technical_preperation_by_id(db, current_user, id)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )


@pipeline_opportunity_technical_preperation_router.get("/opportunity/{opportunity_id}")
async def get_pipeline_opportunity_technical_preperation_by_opportunity_id(
    opportunity_id: UUID,
    current_user: User = Depends(require_permission("pipeline_opportunity_technical_preperation", "read")),
    db: AsyncSession = Depends(get_db),
):
    response: GetPipelineOpportunityTechnicalPreperationResponse = await handle_get_pipeline_opportunity_technical_preperation_by_opportunity_id(db, current_user, opportunity_id)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )


@pipeline_opportunity_technical_preperation_router.post("/")
async def create_pipeline_opportunity_technical_preperation(
    pipeline_opportunity_technical_preperation: PipelineOpportunityTechnicalPreperationCreate,
    current_user: User = Depends(require_permission("pipeline_opportunity_technical_preperation", "create")),
    db: AsyncSession = Depends(get_db),
):
    response: CreatePipelineOpportunityTechnicalPreperationResponse = await handle_create_pipeline_opportunity_technical_preperation(db, current_user, pipeline_opportunity_technical_preperation)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )


@pipeline_opportunity_technical_preperation_router.put("/{id}")
async def update_pipeline_opportunity_technical_preperation(
    id: UUID,
    pipeline_opportunity_technical_preperation: PipelineOpportunityTechnicalPreperationUpdate,
    current_user: User = Depends(require_permission("pipeline_opportunity_technical_preperation", "update")),
    db: AsyncSession = Depends(get_db),
):
    response: UpdatePipelineOpportunityTechnicalPreperationResponse = await handle_update_pipeline_opportunity_technical_preperation(db, current_user, pipeline_opportunity_technical_preperation, id)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )


@pipeline_opportunity_technical_preperation_router.delete("/{id}")
async def delete_pipeline_opportunity_technical_preperation(
    id: UUID,
    current_user: User = Depends(require_permission("pipeline_opportunity_technical_preperation", "delete")),
    db: AsyncSession = Depends(get_db),
):
    response: DeletePipelineOpportunityTechnicalPreperationResponse = await handle_delete_pipeline_opportunity_technical_preperation(db, current_user, id)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )

@pipeline_opportunity_technical_preperation_router.patch("/{id}/comments", deprecated=True)
async def update_technical_preperation_comments(
    id: UUID,
    pipeline_opportunity_technical_preperation_comments: list[str],
    current_user: User = Depends(require_permission("pipeline_opportunity_technical_preperation", "update")),
    db: AsyncSession = Depends(get_db),
):
    """Deprecated. Use POST/GET `/{id}/comments` and PATCH/DELETE `/{id}/comments/{comment_id}`.

    This route overwrites the whole `comments` column with a plain `list[str]`: no author, no
    timestamp and no per-item identity, so nothing written through it can be edited, deleted or
    replied to. The `comments` table carries all of that. The column is kept for one release
    while the backfill is verified against real data (C-D6).
    """
    response: UpdatePipelineOpportunityTechnicalPreperationResponse = await handle_update_pipeline_opportunity_technical_preperation_comments(db, current_user, pipeline_opportunity_technical_preperation_comments, id)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )


@pipeline_opportunity_technical_preperation_router.get("/{id}/comments", response_model=CommentPaginatedResponse)
async def get_technical_preperation_comments(
    id: UUID,
    page: int = 1,
    size: int = 10,
    current_user: User = Depends(require_permission("pipeline_opportunity_technical_preperation", "read")),
    db: AsyncSession = Depends(get_db),
):
    return await get_comments_service(db, PageName.TECHNICAL_PREPARATION, id, current_user, page, size)


@pipeline_opportunity_technical_preperation_router.post("/{id}/comments", response_model=CommentResponse)
async def create_technical_preperation_comment(
    id: UUID,
    comment: CommentCreate,
    current_user: User = Depends(require_permission("pipeline_opportunity_technical_preperation", "create")),
    db: AsyncSession = Depends(get_db),
):
    """Create a comment, or a reply when `parent_comment_id` is set in the body."""
    return await create_comment_service(db, PageName.TECHNICAL_PREPARATION, id, comment, current_user)


@pipeline_opportunity_technical_preperation_router.patch("/{id}/comments/{comment_id}", response_model=CommentResponse)
async def update_technical_preperation_comment(
    id: UUID,
    comment_id: UUID,
    comment: CommentUpdate,
    current_user: User = Depends(require_permission("pipeline_opportunity_technical_preperation", "update")),
    db: AsyncSession = Depends(get_db),
):
    return await update_comment_service(db, PageName.TECHNICAL_PREPARATION, id, comment_id, comment, current_user)


@pipeline_opportunity_technical_preperation_router.delete("/{id}/comments/{comment_id}", response_model=BaseResponse)
async def delete_technical_preperation_comment(
    id: UUID,
    comment_id: UUID,
    current_user: User = Depends(require_permission("pipeline_opportunity_technical_preperation", "delete")),
    db: AsyncSession = Depends(get_db),
):
    return await delete_comment_service(db, PageName.TECHNICAL_PREPARATION, id, comment_id, current_user)
