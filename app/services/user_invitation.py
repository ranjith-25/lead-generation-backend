import logging
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.custom import NotFoundException
from app.models.user_invitation import UserInvitation
from app.models.user import User
from app.responses.user_invitation import (
    CreateUserInvitationResponse,
    DeleteUserInvitationResponse,
    GetUserInvitationResponse,
    UpdateUserInvitationResponse,
)
from app.schemas.user_invitation import InvitationStatus, UserInvitationCreate, UserInvitationDTO, UserInvitationUpdate
from app.services.db.user_invitation import (
    create_user_invitation,
    delete_user_invitation,
    get_all_user_invitations,
    get_user_invitation_by_id,
    update_user_invitation,
    
)
from app.core.settings import settings


async def handle_get_all_user_invitations(db: AsyncSession, current_user: User) -> GetUserInvitationResponse:
    try:
        user_invitations = await get_all_user_invitations(db)
        if user_invitations is None:
            raise NotFoundException()

        return GetUserInvitationResponse(
            userInvitationList=[UserInvitationDTO.model_validate(invitation) for invitation in user_invitations],
            message="User Invitations fetched successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find User Invitations")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while getting User Invitations list")
        raise e


async def handle_get_user_invitation_by_id(db: AsyncSession, current_user: User, user_invitation_id: uuid.UUID) -> GetUserInvitationResponse:
    try:
        user_invitation = await get_user_invitation_by_id(db, user_invitation_id)
        if user_invitation is None:
            raise NotFoundException()

        return GetUserInvitationResponse(
            userInvitation=UserInvitationDTO.model_validate(user_invitation),
            message="User Invitation fetched successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find User Invitation")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while getting User Invitation details")
        raise e


async def handle_create_user_invitation(
    db: AsyncSession, current_user: User, user_invitation_create: UserInvitationCreate
) -> CreateUserInvitationResponse:
    try:
        create_data = user_invitation_create.model_dump()
        create_data.pop("is_active", None)
        new_user_invitation = UserInvitation(
            **create_data,
            invitedBy=current_user.user_id,
            updatedBy=current_user.user_id,
        )
        created_user_invitation = await create_user_invitation(db, new_user_invitation)
        return CreateUserInvitationResponse(
            newUserInvitation=UserInvitationDTO.model_validate(created_user_invitation),
            message="User Invitation created successfully",
            invitationURL = f"{settings.FRONTEND_BASE_URL}/register?invitation_id={created_user_invitation.id}&work_email={created_user_invitation.work_email}",
            status_code=200,
        )
    except Exception as e:
        logging.exception("Some error occurred while creating User Invitation")
        raise e


async def handle_update_user_invitation(
    db: AsyncSession, current_user: User, user_invitation_update: UserInvitationUpdate, user_invitation_id: uuid.UUID
) -> UpdateUserInvitationResponse:
    try:
        update_data = user_invitation_update.model_dump(exclude_unset=True, exclude_none=True)
        update_data.pop("is_active", None)
        update_data["updatedBy"] = current_user.user_id
        updated_user_invitation = await update_user_invitation(db, update_data, user_invitation_id)
        if updated_user_invitation is None:
            raise NotFoundException()

        return UpdateUserInvitationResponse(
            updatedUserInvitation=UserInvitationDTO.model_validate(updated_user_invitation),
            message="User Invitation updated successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find User Invitation")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while updating User Invitation")
        raise e


async def handle_cancel_user_invitation(
    db: AsyncSession, current_user: User, user_invitation_id: uuid.UUID
) -> DeleteUserInvitationResponse:
    try:
        updateData = UserInvitationUpdate(
            status = InvitationStatus.CANCELLED,
            updatedBy = current_user.user_id
        )
        updated_user_invitation = await update_user_invitation(db, updateData.model_dump(exclude_unset=True, exclude_none=True), user_invitation_id)
        if updated_user_invitation is None:
            raise NotFoundException()

        return DeleteUserInvitationResponse(
            message="User Invitation cancelled successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find User Invitation")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while cancelling User Invitation")
        raise e

async def handle_delete_user_invitation(
    db: AsyncSession, current_user: User, user_invitation_id: uuid.UUID
) -> DeleteUserInvitationResponse:
    try:
        deleted_user_invitation = await delete_user_invitation(db, user_invitation_id)
        if deleted_user_invitation is None:
            raise NotFoundException()

        return DeleteUserInvitationResponse(
            message="User Invitation deleted successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find User Invitation")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while deleting User Invitation")
        raise e
