from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.api.deps import get_db
from app.core.security import require_permission
from app.models.user import User
from app.responses.user_status import (
    CreateUserStatusResponse,
    DeleteUserStatusResponse,
    GetUserStatusResponse,
    UpdateUserStatusResponse,
)
from app.schemas.user_status import UserStatusCreate, UserStatusUpdate
from app.services.user_status import (
    handle_create_user_status,
    handle_delete_user_status,
    handle_get_all_user_statuses,
    handle_get_user_status_by_id,
    handle_update_user_status,
)

router = APIRouter(prefix="/user-status", tags=["User Status"])


@router.get("/")
async def get_all_user_statuses(
    search: str | None = None,
    page: int = 1,
    limit: int = 10,
    current_user: User = Depends(require_permission("user_status", "read")),
    db: AsyncSession = Depends(get_db),
):
    response: GetUserStatusResponse = await handle_get_all_user_statuses(db, current_user, search, page, limit)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )


@router.get("/{id}")
async def get_user_status_by_id(
    id: UUID,
    current_user: User = Depends(require_permission("user_status", "read")),
    db: AsyncSession = Depends(get_db),
):
    response: GetUserStatusResponse = await handle_get_user_status_by_id(db, current_user, id)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )


@router.post("/")
async def create_user_status(
    user_status: UserStatusCreate,
    current_user: User = Depends(require_permission("user_status", "create")),
    db: AsyncSession = Depends(get_db),
):
    response: CreateUserStatusResponse = await handle_create_user_status(db, current_user, user_status)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )


@router.put("/{id}")
async def update_user_status(
    id: UUID,
    user_status: UserStatusUpdate,
    current_user: User = Depends(require_permission("user_status", "update")),
    db: AsyncSession = Depends(get_db),
):
    response: UpdateUserStatusResponse = await handle_update_user_status(db, current_user, user_status, id)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )


@router.delete("/{id}")
async def delete_user_status(
    id: UUID,
    current_user: User = Depends(require_permission("user_status", "delete")),
    db: AsyncSession = Depends(get_db),
):
    response: DeleteUserStatusResponse = await handle_delete_user_status(db, current_user, id)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )
