from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.security import require_permission
from app.models.user import User
from app.responses.settings import (
    GetRolePermissionMatrixResponse,
    UpdateRolePermissionMatrixResponse,
)
from app.schemas.settings import RolePermissionMatrixUpdate
from app.services.settings import (
    get_role_permission_matrix_service,
    update_role_permission_matrix_service,
)

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get(
    "/roles/{role_id}/permissions", response_model=GetRolePermissionMatrixResponse
)
async def get_role_permission_matrix(
    role_id: UUID,
    current_user: User = Depends(require_permission("role_permissions", "read")),
    db: AsyncSession = Depends(get_db),
) -> GetRolePermissionMatrixResponse:
    return await get_role_permission_matrix_service(db, role_id)


@router.put(
    "/roles/{role_id}/permissions", response_model=UpdateRolePermissionMatrixResponse
)
async def update_role_permission_matrix(
    payload: RolePermissionMatrixUpdate,
    role_id: UUID,
    current_user: User = Depends(require_permission("role_permissions", "update")),
    db: AsyncSession = Depends(get_db),
) -> UpdateRolePermissionMatrixResponse:
    return await update_role_permission_matrix_service(
        db, role_id, payload, current_user.user_id
    )
