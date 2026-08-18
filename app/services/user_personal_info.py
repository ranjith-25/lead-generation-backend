import logging
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import LogAction
from app.exceptions.custom import (
    AppException,
    NotFoundException,
    IncorrectPasswordException,
    ConfirmPasswordMismatchException,
    UserAlreadyDeletedException,
)
from app.responses.base import BaseResponse
from app.models.user import User
from app.models.user_personal_info import UserPersonalInfo
from app.responses.user_personal_info import (
    CreateUserPersonalInfoResponse,
    DeleteUserPersonalInfoResponse,
    GetUserPersonalInfoResponse,
    UpdateUserPersonalInfoResponse,
)
from app.schemas.common import get_time_filter_options
from app.schemas.user_personal_info import (
    UserPersonalInfoCreate,
    UserPersonalInfoFilterRequest,
    UserPersonalInfoListRead,
    UserPersonalInfoPaginatedResponse,
    UserPersonalInfoResponse,
    UserPersonalInfoUpdate,
    UserPersonalInfoStatusUpdate,
    UserProfileFiltersResponse,
    UserPasswordUpdate
)
from app.services.db.user import get_user_by_id, soft_delete_user, update_user_password
from app.services.db.user_personal_info import (
    create_user_personal_info,
    get_all_user_personal_info,
    get_user_personal_info_by_user_id,
    update_user_personal_info,
    get_user_profile_filters,
)
from app.core.security import (
    verify_password,
    get_password_hash
)

from app.services.hierarchy import handleGetHierarchyByUser
from app.services.system_log import log_activity


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
        
        hierarchy_res = await handleGetHierarchyByUser(db, current_user.user_id)
        team_list = []
        if hierarchy_res.hierarchy:
            def extract_team(node):
                if node.fullName not in team_list:
                    team_list.append(node.fullName)
                for child in node.children:
                    extract_team(child)
            extract_team(hierarchy_res.hierarchy)
            
        filters["team"] = team_list
        filters["time_filter"] = get_time_filter_options()

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


async def handle_update_user_personal_info_status(
    db: AsyncSession, current_user: User, status_update: UserPersonalInfoStatusUpdate, user_id: UUID
) -> UpdateUserPersonalInfoResponse:
    try:
        update_data = {"working_status_id": status_update.working_status_id}
        updated_personal_info = await update_user_personal_info(db, update_data, user_id)
        if updated_personal_info is None:
            raise NotFoundException()

        return UpdateUserPersonalInfoResponse(
            personalInfo=UserPersonalInfoResponse.model_validate(updated_personal_info),
            message="User status updated successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find User Personal Info")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while updating user status")
        raise e


async def handle_delete_user_personal_info(
    db: AsyncSession, current_user: User, user_id: UUID
) -> DeleteUserPersonalInfoResponse:
    """Soft-deletes the *user account*, despite the route sitting under /user-personal-info.

    The `user_personal_info` row is deliberately left in place: it is what `User.fullName`
    reads, so dropping it would degrade every historical `createdByName` and every system-log
    actor name to "Unknown User". See app/.docs/plans/user-soft-delete.md.
    """
    try:
        user = await get_user_by_id(db, user_id)
        if user is None:
            raise NotFoundException()
        if user.is_deleted:
            raise UserAlreadyDeletedException()

        # Staged before the write so that soft_delete_user's commit flushes the log row too,
        # and while `fullName` / `email` still read off a row nobody has touched yet.
        await log_activity(
            db,
            LogAction.USER_DELETED,
            current_user,
            entity_type="user",
            entity_id=user.user_id,
            entity_name=user.fullName,
            details={"email": user.email},
        )

        counts = await soft_delete_user(db, user)
        # Counts land here rather than in the log row's `details`: staging happens before the
        # write, so the row is composed before these numbers exist.
        logging.info(
            "Soft deleted user %s - reparented %s subordinate(s), orphaned %s, "
            "cleared %s opportunity assignment(s), revoked %s session(s)",
            user_id,
            counts["subordinates_reparented"],
            counts["subordinates_orphaned"],
            counts["opportunities_unassigned"],
            counts["sessions_revoked"],
        )

        return DeleteUserPersonalInfoResponse(
            message="User deleted successfully",
            status_code=200,
        )
    except AppException:
        raise
    except Exception:
        logging.exception("Some error occurred while deleting the user")
        raise

async def handle_update_password(
    db: AsyncSession, payload: UserPasswordUpdate, current_user: User
) -> BaseResponse:
    try:
        if not current_user.hashedPassword or not verify_password(
            payload.existing_password, current_user.hashedPassword
        ):
            raise IncorrectPasswordException()

        if payload.new_password != payload.confirm_password:
            raise ConfirmPasswordMismatchException()
        updated_user = await update_user_password(
            db, current_user.user_id, get_password_hash(payload.new_password)
        )
        if updated_user is None:
            raise NotFoundException()

        return BaseResponse(message="Password updated successfully")
    except AppException:
        raise
    except Exception:
        logging.exception("Some error occurred while updating the password")
        raise