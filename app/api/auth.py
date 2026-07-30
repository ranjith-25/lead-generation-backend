from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, oauth2_scheme
from app.core.connections.postgres import get_db
from app.services.auth import authenticate_user, logout_user
from app.models.user import User
from app.schemas.user import UserRead
from app.responses.authentication import AuthenticationResponse
from app.responses.base import BaseResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=AuthenticationResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
) -> AuthenticationResponse:
    return await authenticate_user(db, form_data)


@router.post("/logout", response_model=BaseResponse)
async def logout(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> BaseResponse:
    return await logout_user(db, token)


@router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(current_user)
