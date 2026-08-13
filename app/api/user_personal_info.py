from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.connections.postgres import get_db
from app.core.security import require_permission
from app.models.user import User
from app.responses.base import BaseResponse
from app.responses.user_personal_info import (
    CreateUserPersonalInfoResponse,
    DeleteUserPersonalInfoResponse,
    GetUserPersonalInfoResponse,
    UpdateUserPersonalInfoResponse,
)
from app.schemas.user_personal_info import (
    UserPersonalInfoCreate,
    UserPersonalInfoFilterRequest,
    UserPersonalInfoPaginatedResponse,
    UserPersonalInfoUpdate,
    UserPersonalInfoStatusUpdate,
    UserProfileFiltersResponse,
    UserPasswordUpdate
)
from app.services.user_personal_info import (
    handle_create_user_personal_info,
    handle_delete_user_personal_info,
    handle_get_all_user_personal_info,
    handle_get_user_personal_info,
    handle_update_user_personal_info,
    handle_update_user_personal_info_status,
    handle_get_user_profile_filters,
    handle_update_password
)

router = APIRouter(prefix="/user-personal-info", tags=["User Profile"])


@router.post("/all", response_model=UserPersonalInfoPaginatedResponse)
async def get_all_user_personal_info_filtered(
    filters: UserPersonalInfoFilterRequest,
    current_user: User = Depends(require_permission("user_personal_info", "read")),
    db: AsyncSession = Depends(get_db),
) -> UserPersonalInfoPaginatedResponse:
    return await handle_get_all_user_personal_info(db, current_user, filters)


@router.get("/filters", response_model=UserProfileFiltersResponse)
async def get_user_profile_filters(
    current_user: User = Depends(require_permission("user_personal_info", "read")),
    db: AsyncSession = Depends(get_db),
) -> UserProfileFiltersResponse:
    return await handle_get_user_profile_filters(db, current_user)

@router.patch("/update-password", response_model=BaseResponse)
async def update_user_password(
    payloads: UserPasswordUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await handle_update_password(db, payloads, current_user)

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


@router.patch("/{user_id}/status")
async def update_user_personal_info_status(
    user_id: UUID,
    status_update: UserPersonalInfoStatusUpdate,
    current_user: User = Depends(require_permission("user_personal_info", "update")),
    db: AsyncSession = Depends(get_db),
) -> UpdateUserPersonalInfoResponse:
    return await handle_update_user_personal_info_status(db, current_user, status_update, user_id)


@router.delete("/{user_id}")
async def delete_user_personal_info(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DeleteUserPersonalInfoResponse:
    return await handle_delete_user_personal_info(db, current_user, user_id)
