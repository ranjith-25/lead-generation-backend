from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.connections.postgres import get_db
from app.core.security import require_permission
from app.models.user import User
from app.responses.branch import (
    CreateBranchResponse,
    DeleteBranchResponse,
    GetBranchResponse,
    UpdateBranchResponse,
)
from app.schemas.branch import BranchCreate, BranchUpdate
from app.services.branch import (
    handle_create_branch,
    handle_delete_branch,
    handle_get_all_branches,
    handle_get_branch_by_id,
    handle_update_branch,
)

branch_router = APIRouter(prefix="/branch", tags=["Branch"])


@branch_router.get("/")
async def get_all_branches(
    db: AsyncSession = Depends(get_db),
):
    response: GetBranchResponse = await handle_get_all_branches(db)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )


@branch_router.get("/{id}")
async def get_branch_by_id(
    id: UUID,
    current_user: User = Depends(require_permission("branch", "read")),
    db: AsyncSession = Depends(get_db),
):
    response: GetBranchResponse = await handle_get_branch_by_id(db, current_user, id)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )


@branch_router.post("/")
async def create_branch(
    branch: BranchCreate,
    current_user: User = Depends(require_permission("branch", "create")),
    db: AsyncSession = Depends(get_db),
):
    response: CreateBranchResponse = await handle_create_branch(db, current_user, branch)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )


@branch_router.patch("/{id}")
async def update_branch(
    id: UUID,
    branch: BranchUpdate,
    current_user: User = Depends(require_permission("branch", "update")),
    db: AsyncSession = Depends(get_db),
):
    response: UpdateBranchResponse = await handle_update_branch(db, current_user, branch, id)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )


@branch_router.delete("/{id}")
async def delete_branch(
    id: UUID,
    current_user: User = Depends(require_permission("branch", "delete")),
    db: AsyncSession = Depends(get_db),
):
    response: DeleteBranchResponse = await handle_delete_branch(db, current_user, id)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )
