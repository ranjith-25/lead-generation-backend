import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import UserRegistrationFromInvitation
from app.schemas.user_invitation import UserInvitationDTO,UserInvitationUpdate,InvitationStatus
from app.models.user_personal_info import UserPersonalInfo
from app.core.security import create_access_token, verify_password
from app.services.db.user import get_user_by_email, get_user_by_id
from app.services.db.session import create_session, revoke_session
from app.services.db.role_permissions import get_feature_names_by_role_id
from app.exceptions.auth import InvalidCredentialsException, InvalidResetTokenException, InvalidOtpException
from app.exceptions.custom import AppException, ConfirmPasswordMismatchException
from app.core.settings import settings
from app.schemas.auth import ForgotPasswordRequest, ResetPasswordRequest, VerifyOtpRequest
from app.services.db.password_reset import (
    create_password_reset_token as create_password_reset_token_record,
    get_password_reset_token_by_user_and_hash,
    reset_password_by_user_id,
    spend_password_reset_token,
)
from app.services.email import send_otp_email
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
from app.responses.authentication import (
    ForgotPasswordMailResponse
)
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


def _hash_otp(user_id: str, otp: str) -> str:
    return hashlib.sha256(f"{user_id}:{otp}".encode()).hexdigest()


_OTP_MAX_ATTEMPTS = 5
_otp_attempts: dict[str, int] = {}


def _generate_otp() -> str:
    return f"{secrets.randbelow(10**6):06d}"


async def handle_forgot_password(db: AsyncSession, payload: ForgotPasswordRequest) -> BaseResponse:
    try:
        user = await get_user_by_email(db, payload.email)

        if user is not None:
            otp = _generate_otp()
            expires_at = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(
                minutes=settings.OTP_EXPIRE_MINUTES
            )

            await create_password_reset_token_record(
                db, user.user_id, _hash_otp(str(user.user_id), otp), expires_at
            )

            await send_otp_email(user.email, otp)
            
            return ForgotPasswordMailResponse(
                message= "A password reset OTP has been sent to it",
                user_id= user.user_id
            )
        else:
            logging.info("Password reset requested for an unregistered address")

        return ForgotPasswordMailResponse(
            message="A password reset code has been sent to it",
        )
    except AppException:
        raise
    except Exception:
        logging.exception("Some error occurred while starting the password reset")
        raise


async def handle_verify_otp(db: AsyncSession, payload: VerifyOtpRequest) -> ForgotPasswordMailResponse:
    try:
        user = await get_user_by_id(db, payload.user_id)

        if user is None:
            raise InvalidOtpException()

        token_hash = _hash_otp(str(user.user_id), payload.otp)

        attempts = _otp_attempts.get(token_hash, 0) + 1
        if attempts > _OTP_MAX_ATTEMPTS:
            raise InvalidOtpException()

        reset_token = await get_password_reset_token_by_user_and_hash(
            db, user.user_id, token_hash
        )

        if reset_token is None or reset_token.used_at is not None:
            raise InvalidOtpException()

        if reset_token.expires_at <= datetime.now(timezone.utc).replace(tzinfo=None):
            raise InvalidOtpException()

        _otp_attempts.pop(token_hash, None)

        return ForgotPasswordMailResponse(
            message="Code verified successfully",
            user_id=user.user_id,
        )
    except AppException:
        raise
    except Exception:
        logging.exception("Some error occurred while verifying the password reset code")
        raise


async def handle_reset_password(db: AsyncSession, payload: ResetPasswordRequest) -> BaseResponse:
    try:
        if payload.new_password != payload.confirm_password:
            raise ConfirmPasswordMismatchException()

        user_id = payload.user_id
        updated_user = await reset_password_by_user_id(
            db, user_id, get_password_hash(payload.new_password)
        )
        if updated_user is None:
            raise InvalidResetTokenException()

        return BaseResponse(
            message="Password reset successfully. Please log in with your new password"
        )
    except AppException:
        raise
    except Exception:
        logging.exception("Some error occurred while resetting the password")
        raise


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
    except Exception as e:
        db.rollback()
        logging.exception("Some error occurred while getting Invitation")
        raise e