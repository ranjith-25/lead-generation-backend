from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, oauth2_scheme
from app.core.security import create_access_token, verify_password
from app.core.connections.postgres import get_db
from app.services.db.user import get_user_by_email
from app.services.db.session import create_session, revoke_session
from app.services.db.menu import get_menu_names_by_role_id
from app.exceptions.auth import InvalidCredentialsException
from app.models.user import User
from app.schemas.auth import LoginRequest, Token
from app.schemas.user import UserRead
from app.responses.authentication import AuthenticationResponse
from app.responses.base import BaseResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=AuthenticationResponse)
async def login(
    login_data: LoginRequest, db: AsyncSession = Depends(get_db)
) -> Token:
    user = await get_user_by_email(db, login_data.email)

    if not user or not user.hashedPassword:
        raise InvalidCredentialsException()

    if not verify_password(login_data.password, user.hashedPassword):
        raise InvalidCredentialsException()

    access_token, expire = create_access_token(subject=str(user.user_id))
    
    # Store session in DB
    await create_session(db=db, user_id=user.user_id, token=access_token, expires_at=expire)

    user_role = user.role.roleName if user.role else "USER"
    user_permissions = []
    if user.role_id:
        user_permissions = await get_menu_names_by_role_id(db, user.role_id)

    return AuthenticationResponse(
        message="Authentication successful",
        access_token=access_token,
        user_id=str(user.user_id),
        fullName=user.fullName,
        role=user_role,
        permissions=user_permissions
    )


@router.post("/logout", response_model=BaseResponse)
async def logout(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> BaseResponse:
    success = await revoke_session(db, token)
    if not success:
        return BaseResponse(success=False, message="Session not found or already logged out")
    return BaseResponse(success=True, message="Successfully logged out")


@router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(current_user)
