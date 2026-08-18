from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.connections.postgres import get_db
from app.core.security import require_permission
from app.models.user import User
from app.schemas.user_personal_info import UserPersonalInfoFilterRequest, UserManagementFilterRequest
from app.schemas.user_management import (
    UserManagementPaginatedResponse,
    UpdateUserRoleRequest
)
from app.services.user_management import (
    handle_get_all_user_management,
    handle_update_user_role
)
from app.responses.base import BaseResponse

router = APIRouter(prefix="/settings/user-management", tags=["User Management"])

@router.post("/all", response_model=UserManagementPaginatedResponse)
async def get_all_user_management(
    filters: UserManagementFilterRequest,
    current_user: User = Depends(require_permission("user_management", "read")),
    db: AsyncSession = Depends(get_db),
) -> UserManagementPaginatedResponse:
    return await handle_get_all_user_management(db, current_user, filters)

@router.patch("/{user_id}/role", response_model=BaseResponse)
async def update_user_role(
    user_id: str,
    update_data: UpdateUserRoleRequest,
    current_user: User = Depends(require_permission("user_management", "update")),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    return await handle_update_user_role(db, user_id, update_data, current_user.user_id)