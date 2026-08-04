from uuid import UUID

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import settings
from app.core.connections.postgres import get_db
from app.exceptions.auth import SessionExpiredException, TokenExpiredException
from app.models.user import User
from app.services.db.user import get_user_by_id
from app.services.db.session import get_session_by_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise SessionExpiredException()
    except jwt.ExpiredSignatureError:
        raise TokenExpiredException()
    except (jwt.InvalidTokenError, ValidationError):
        raise SessionExpiredException()

    try:
        uid = UUID(user_id)
    except ValueError:
        raise SessionExpiredException()

    user = await get_user_by_id(db, uid)

    if user is None:
        raise SessionExpiredException()

    session = await get_session_by_token(db, token)
    if not session or session.isRevoked:
        raise SessionExpiredException()

    return user
