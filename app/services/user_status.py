import logging
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.exceptions.custom import NotFoundException
from app.models.user_status import UserStatus
from app.models.user import User
from app.responses.user_status import (
    CreateUserStatusResponse,
    DeleteUserStatusResponse,
    GetUserStatusResponse,
    UpdateUserStatusResponse,
)
from app.schemas.user_status import UserStatusCreate, UserStatusDTO, UserStatusUpdate, UserStatusListRead
from app.services.db.user_status import (
    create_user_status,
    delete_user_status,
    get_all_user_statuses,
    get_user_status_by_id,
    update_user_status,
)


async def handle_get_all_user_statuses(db: AsyncSession, search: str | None = None, page: int = 1, limit: int = 10) -> GetUserStatusResponse:
    try:
        user_statuses, total = await get_all_user_statuses(db, search, page, limit)

        return GetUserStatusResponse(
            userStatusList=[UserStatusListRead.model_validate(status) for status in user_statuses],
            total=total,
            page=page,
            limit=limit,
            total_pages=(total + limit - 1) // limit if total > 0 else 1,
            message="User Statuses fetched successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find User Statuses")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while getting User Statuses list")
        raise e


async def handle_get_user_status_by_id(db: AsyncSession, current_user: User, user_status_id: UUID) -> GetUserStatusResponse:
    try:
        user_status = await get_user_status_by_id(db, user_status_id)
        if user_status is None:
            raise NotFoundException()

        return GetUserStatusResponse(
            userStatus=UserStatusDTO.model_validate(user_status),
            message="User Status fetched successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find User Status")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while getting User Status details")
        raise e


async def handle_create_user_status(
    db: AsyncSession, current_user: User, user_status_create: UserStatusCreate
) -> CreateUserStatusResponse:
    try:
        new_user_status = UserStatus(
            **user_status_create.model_dump(),
            createdBy=current_user.user_id,
            updatedBy=current_user.user_id,
        )
        created_user_status = await create_user_status(db, new_user_status)
        return CreateUserStatusResponse(
            newUserStatus=UserStatusDTO.model_validate(created_user_status),
            message="User Status created successfully",
            status_code=200,
        )
    except Exception as e:
        logging.exception("Some error occurred while creating User Status")
        raise e


async def handle_update_user_status(
    db: AsyncSession, current_user: User, user_status_update: UserStatusUpdate, user_status_id: UUID
) -> UpdateUserStatusResponse:
    try:
        update_data = user_status_update.model_dump(exclude_unset=True, exclude_none=True)
        update_data["updatedBy"] = current_user.user_id
        updated_user_status = await update_user_status(db, update_data, user_status_id)
        if updated_user_status is None:
            raise NotFoundException()

        return UpdateUserStatusResponse(
            updatedUserStatus=UserStatusDTO.model_validate(updated_user_status),
            message="User Status updated successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find User Status")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while updating User Status")
        raise e


async def handle_delete_user_status(
    db: AsyncSession, current_user: User, user_status_id: UUID
) -> DeleteUserStatusResponse:
    try:
        deleted_user_status = await delete_user_status(db, user_status_id)
        if deleted_user_status is None:
            raise NotFoundException()

        return DeleteUserStatusResponse(
            message="User Status deleted successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find User Status")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while deleting User Status")
        raise e
