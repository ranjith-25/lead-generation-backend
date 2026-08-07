from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.connections.postgres import get_db
from app.core.security import require_permission
from app.models.user import User
from app.schemas.user_personal_info import UserPersonalInfoFilterRequest, UserManagementFilterRequest
from app.schemas.user_management import UserManagementPaginatedResponse
from app.services.user_management import handle_get_all_user_management

router = APIRouter(prefix="/settings/user-management", tags=["User Management"])

@router.post("/all", response_model=UserManagementPaginatedResponse)
async def get_all_user_management(
    filters: UserManagementFilterRequest,
    current_user: User = Depends(require_permission("user_management", "read")),
    db: AsyncSession = Depends(get_db),
) -> UserManagementPaginatedResponse:
    return await handle_get_all_user_management(db, current_user, filters)