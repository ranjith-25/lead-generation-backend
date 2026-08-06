from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.connections.postgres import get_db
from app.core.security import require_permission
from app.models.user import User
from app.responses.user_personal_info import (
    CreateUserPersonalInfoResponse,
    DeleteUserPersonalInfoResponse,
    GetUserPersonalInfoResponse,
    UpdateUserPersonalInfoResponse,
)
from app.schemas.user_personal_info import UserPersonalInfoCreate, UserPersonalInfoUpdate
from app.services.user_personal_info import (
    handle_create_user_personal_info,
    handle_delete_user_personal_info,
    handle_get_user_personal_info,
    handle_update_user_personal_info,
)

router = APIRouter(prefix="/user-personal-info", tags=["User Personal Info"])


@router.get("/{user_id}")
async def get_user_personal_info(
    user_id: UUID,
    current_user: User = Depends(require_permission("user_personal_info", "read")),
    db: AsyncSession = Depends(get_db),
) -> GetUserPersonalInfoResponse:
    return await handle_get_user_personal_info(db, current_user, user_id)


@router.post("/")
async def create_user_personal_info(
    personal_info: UserPersonalInfoCreate,
    current_user: User = Depends(require_permission("user_personal_info", "create")),
    db: AsyncSession = Depends(get_db),
) -> CreateUserPersonalInfoResponse:
    return await handle_create_user_personal_info(db, current_user, personal_info)


@router.patch("/{user_id}")
async def update_user_personal_info(
    user_id: UUID,
    personal_info: UserPersonalInfoUpdate,
    current_user: User = Depends(require_permission("user_personal_info", "update")),
    db: AsyncSession = Depends(get_db),
) -> UpdateUserPersonalInfoResponse:
    return await handle_update_user_personal_info(db, current_user, personal_info, user_id)


@router.delete("/{user_id}")
async def delete_user_personal_info(
    user_id: UUID,
    current_user: User = Depends(require_permission("user_personal_info", "delete")),
    db: AsyncSession = Depends(get_db),
) -> DeleteUserPersonalInfoResponse:
    return await handle_delete_user_personal_info(db, current_user, user_id)
