from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import UserRegistrationFromInvitation
from app.schemas.user_invitation import UserInvitationDTO,UserInvitationUpdate,InvitationStatus
from app.schemas.user_personal_info import UserPersonalInfoCreate
from app.models.user_personal_info import UserPersonalInfo
from app.core.security import create_access_token, verify_password
from app.services.db.user import get_user_by_email
from app.services.db.session import create_session, revoke_session
from app.services.db.menu import get_menu_names_by_role_id
from app.services.db.role_permissions import get_feature_names_by_role_id
from app.exceptions.auth import InvalidCredentialsException
from app.responses.authentication import AuthenticationResponse
from app.responses.base import BaseResponse
from app.responses.authentication import UserRegistrationFromInvitationResponse
from app.services.db.user_invitation import update_user_invitation,get_user_invitation_by_id
from app.services.db.user_personal_info import create_user_personal_info
from app.services.db.user import create_user,register_user_from_invitation
import uuid
from app.exceptions.custom import NotFoundException
import logging
from sqlalchemy.exc import SQLAlchemyError
from app.exceptions.custom import InvitationCancelledException,InvitationRegisteredException

async def authenticate_user(db: AsyncSession, form_data: OAuth2PasswordRequestForm) -> AuthenticationResponse:

    user = await get_user_by_email(db, form_data.username)

    if not user or not user.hashedPassword:
        raise InvalidCredentialsException()

    if not verify_password(form_data.password, user.hashedPassword):
        raise InvalidCredentialsException()

    access_token, expire = create_access_token(subject=str(user.user_id))
    # print(user.role.role_permissions)
    # Store session in DB
    await create_session(db=db, user_id=user.user_id, token=access_token, expires_at=expire)

    user_role = user.role.roleName if user.role else "USER"
    user_permissions = []
    if user.role_id:
        user_permissions = await get_feature_names_by_role_id(db, user.role_id)

    return AuthenticationResponse(
        message="Authentication successful",
        access_token=access_token,
        user_id=str(user.user_id),
        fullName=user.fullName,
        role=user_role,
        permissions=user_permissions
    )


async def logout_user(db: AsyncSession, token: str) -> BaseResponse:
    success = await revoke_session(db, token)
    if not success:
        return BaseResponse(success=False, message="Session not found or already logged out")
    return BaseResponse(success=True, message="Successfully logged out")


async def handle_signup_invitation(db : AsyncSession , invitation_id : uuid.UUID,registration_data : UserRegistrationFromInvitation):
    try : 
        #Get Invitation Details
        invitationDetails : UserInvitationDTO = await get_user_invitation_by_id(db,invitation_id)
        if not invitationDetails:
            logging.exception("Invitation details not found",invitation_id)
            raise NotFoundException
        
        if invitationDetails.status == InvitationStatus.CANCELLED:
            logging.exception("Invitation is cancelled",invitation_id)
            raise InvitationCancelledException
        
        if invitationDetails.status == InvitationStatus.REGISTERED:
            logging.exception("Invitation is already registered",invitation_id)
            raise InvitationRegisteredException
        # User Table

        hashedPassword = get_password_hash(registration_data.user_details.password)
        user : User = User(
            email = invitationDetails.work_email,
            hashedPassword = hashedPassword,
            role_id = invitationDetails.roleID,
            reporting_to = invitationDetails.reporting_to
        )

        # User Personal Info
        new_personal_info = UserPersonalInfo(**registration_data.user_personal_details.model_dump(), user_id = "3fa85f64-5717-4562-b3fc-2c963f66afa6") # This is a dummmy userID it will be updated in the DB Layer with actual created uuid
        

        # User Invitation
        updateInvitationData = UserInvitationUpdate(
            status = InvitationStatus.REGISTERED
        )
        
        
        await register_user_from_invitation(db,user,new_personal_info,invitation_id,updateInvitationData.model_dump(exclude_none=True,exclude_unset=True))

        return UserRegistrationFromInvitationResponse(
            message = "User registration was successful."            
        )

    except InvitationCancelledException as e:
        await db.rollback()
        raise e

    except InvitationRegisteredException as e:
        await db.rollback()
        raise e
        
    except SQLAlchemyError as e:
        await db.rollback()
        raise 

    except NotFoundException as e:
        await db.rollback()
        logging.exception("Could not find Invitation")
        raise e
    except Exception as e:
        db.rollback()
        logging.exception("Some error occurred while getting Invitation")
        raise e