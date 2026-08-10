from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.security import require_permission
from app.models.user import User
from app.api.deps import get_db
from app.schemas.permissions import PermissionCreate, PermissionUpdate
from app.responses.permissions import (
    GetPermissionResponse,
    CreatePermissionResponse,
    UpdatePermissionResponse,
    DeletePermissionResponse,
)
from app.services.permissions import (
    handle_get_permissions,
    handle_get_permission_by_id,
    handle_create_permission,
    handle_update_permission,
    handle_delete_permission,
)

permission_router = APIRouter(prefix="/permissions", tags=["Permissions"])


@permission_router.get("/")
async def get_all_permissions(
    current_user: User = Depends(require_permission("permissions", "read")),
    db: AsyncSession = Depends(get_db)
):
    response: GetPermissionResponse = await handle_get_permissions(db, current_user)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200
    )


@permission_router.get("/{permission_id}")
async def get_permission_by_id(
    permission_id: UUID,
    current_user: User = Depends(require_permission("permissions", "read")),
    db: AsyncSession = Depends(get_db)
):
    response: GetPermissionResponse = await handle_get_permission_by_id(db, current_user, permission_id)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200
    )


@permission_router.post("/")
async def create_permission(
    permission: PermissionCreate,
    current_user: User = Depends(require_permission("permissions", "create")),
    db: AsyncSession = Depends(get_db)
):
    response: CreatePermissionResponse = await handle_create_permission(db, current_user, permission)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=201
    )


@permission_router.put("/{permission_id}")
async def update_permission(
    permission_id: UUID,
    permission: PermissionUpdate,
    current_user: User = Depends(require_permission("permissions", "update")),
    db: AsyncSession = Depends(get_db)
):
    response: UpdatePermissionResponse = await handle_update_permission(db, current_user, permission, permission_id)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200
    )


@permission_router.delete("/{permission_id}")
async def delete_permission(
    permission_id: UUID,
    current_user: User = Depends(require_permission("permissions", "delete")),
    db: AsyncSession = Depends(get_db)
):
    response: DeletePermissionResponse = await handle_delete_permission(db, current_user, permission_id)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200
    )
