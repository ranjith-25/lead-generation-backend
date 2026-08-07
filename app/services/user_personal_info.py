import logging
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.custom import NotFoundException
from app.models.user import User
from app.models.user_personal_info import UserPersonalInfo
from app.responses.user_personal_info import (
    CreateUserPersonalInfoResponse,
    DeleteUserPersonalInfoResponse,
    GetUserPersonalInfoResponse,
    UpdateUserPersonalInfoResponse,
)
from app.schemas.user_personal_info import (
    UserPersonalInfoCreate,
    UserPersonalInfoFilterRequest,
    UserPersonalInfoListRead,
    UserPersonalInfoPaginatedResponse,
    UserPersonalInfoResponse,
    UserPersonalInfoUpdate,
    UserProfileFiltersResponse,
)
from app.services.db.user_personal_info import (
    create_user_personal_info,
    delete_user_personal_info,
    get_all_user_personal_info,
    get_user_personal_info_by_user_id,
    update_user_personal_info,
    get_user_profile_filters,
)


async def handle_get_user_personal_info(
    db: AsyncSession, current_user: User, user_id: UUID
) -> GetUserPersonalInfoResponse:
    try:
        personal_info = await get_user_personal_info_by_user_id(db, user_id)
        if personal_info is None:
            raise NotFoundException()

        return GetUserPersonalInfoResponse(
            personalInfo=UserPersonalInfoResponse.model_validate(personal_info),
            message="User Personal Info fetched successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find User Personal Info")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while getting User Personal Info")
        raise e


async def handle_get_all_user_personal_info(
    db: AsyncSession, current_user: User, filters: UserPersonalInfoFilterRequest
) -> UserPersonalInfoPaginatedResponse:
    try:
        items, total = await get_all_user_personal_info(db, filters)
        
        return UserPersonalInfoPaginatedResponse(
            items=[UserPersonalInfoListRead(**item) for item in items],
            total=total,
            page=filters.page,
            limit=filters.limit,
            total_pages=(total + filters.limit - 1) // filters.limit if total > 0 else 1
        )
    except Exception as e:
        logging.exception("Some error occurred while getting all User Personal Info")
        raise e

async def handle_get_user_profile_filters(
    db: AsyncSession, current_user: User
) -> UserProfileFiltersResponse:
    try:
        filters = await get_user_profile_filters(db)
        return UserProfileFiltersResponse(**filters)
    except Exception as e:
        logging.exception("Some error occurred while getting user profile filters")
        raise e


async def handle_create_user_personal_info(
    db: AsyncSession, current_user: User, personal_info_create: UserPersonalInfoCreate
) -> CreateUserPersonalInfoResponse:
    try:
        new_personal_info = UserPersonalInfo(**personal_info_create.model_dump(),user_id = current_user.user_id)
        created_personal_info = await create_user_personal_info(db, new_personal_info)
        return CreateUserPersonalInfoResponse(
            personalInfo=UserPersonalInfoResponse.model_validate(created_personal_info),
            message="User Personal Info created successfully",
            status_code=200,
        )
    except Exception as e:
        logging.exception("Some error occurred while creating User Personal Info")
        raise e


async def handle_update_user_personal_info(
    db: AsyncSession, current_user: User, personal_info_update: UserPersonalInfoUpdate, user_id: UUID
) -> UpdateUserPersonalInfoResponse:
    try:
        update_data = personal_info_update.model_dump(exclude_unset=True, exclude_none=True)
        updated_personal_info = await update_user_personal_info(db, update_data, user_id)
        if updated_personal_info is None:
            raise NotFoundException()

        return UpdateUserPersonalInfoResponse(
            personalInfo=UserPersonalInfoResponse.model_validate(updated_personal_info),
            message="User Personal Info updated successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find User Personal Info")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while updating User Personal Info")
        raise e


async def handle_delete_user_personal_info(
    db: AsyncSession, current_user: User, user_id: UUID
) -> DeleteUserPersonalInfoResponse:
    try:
        deleted_personal_info = await delete_user_personal_info(db, user_id)
        if deleted_personal_info is None:
            raise NotFoundException()

        return DeleteUserPersonalInfoResponse(
            message="User Personal Info deleted successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find User Personal Info")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while deleting User Personal Info")
        raise e
