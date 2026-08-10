from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.connections.postgres import get_db
from app.core.security import require_permission
from app.models.user import User
from app.responses.role import (
    CreateRoleResponse,
    DeleteRoleResponse,
    GetRoleResponse,
    UpdateRoleResponse,
)
from app.schemas.role import RoleCreate, RoleRead, RoleUpdate
from app.services.role import (
    handle_create_role,
    handle_delete_role,
    handle_get_all_roles,
    handle_get_role,
    handle_update_role,
)

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.get("", response_model=list[RoleRead])
async def get_all_roles(
    current_user: User = Depends(require_permission("roles", "read")),
    db: AsyncSession = Depends(get_db),
) -> list[RoleRead]:
    return await handle_get_all_roles(db, current_user)


@router.get("/{role_id}")
async def get_role(
    role_id: UUID,
    current_user: User = Depends(require_permission("roles", "read")),
    db: AsyncSession = Depends(get_db),
) -> GetRoleResponse:
    return await handle_get_role(db, current_user, role_id)


@router.post("")
async def create_role(
    role: RoleCreate,
    current_user: User = Depends(require_permission("roles", "create")),
    db: AsyncSession = Depends(get_db),
) -> CreateRoleResponse:
    return await handle_create_role(db, current_user, role)


@router.patch("/{role_id}")
async def update_role(
    role_id: UUID,
    role: RoleUpdate,
    current_user: User = Depends(require_permission("roles", "update")),
    db: AsyncSession = Depends(get_db),
) -> UpdateRoleResponse:
    return await handle_update_role(db, current_user, role, role_id)


@router.delete("/{role_id}")
async def delete_role(
    role_id: UUID,
    current_user: User = Depends(require_permission("roles", "delete")),
    db: AsyncSession = Depends(get_db),
) -> DeleteRoleResponse:
    return await handle_delete_role(db, current_user, role_id)
