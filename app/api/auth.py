from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.security import create_access_token, verify_password
from app.core.connections.postgres import get_db
from app.services.db.user import get_user_by_email
from app.exceptions.auth import InvalidCredentialsException
from app.models.user import User
from app.schemas.auth import LoginRequest, Token
from app.schemas.user import UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest, db: AsyncSession = Depends(get_db)
) -> Token:
    user = await get_user_by_email(db, login_data.email)

    if not user or not user.hashedPassword:
        raise InvalidCredentialsException()

    if not verify_password(login_data.password, user.hashedPassword):
        raise InvalidCredentialsException()

    access_token = create_access_token(subject=str(user.user_id))
    return Token(access_token=access_token)


@router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(current_user)
