from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from passlib.context import CryptContext

from app.core.settings import settings
from app.core.connections.postgres import get_db
from app.api.deps import get_current_user
from app.services.db.role_permissions import hasPermissions
from fastapi import Depends
from app.exceptions.auth import PermissionRequired, InvalidResetTokenException

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(subject: str | Any, expires_delta: timedelta | None = None) -> tuple[str, datetime]:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    # Strip tzinfo to make it offset-naive for SQLAlchemy DateTime column
    expire_naive = expire.replace(tzinfo=None)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt, expire_naive


def create_password_reset_token(
    user_id: str | Any, expires_delta: timedelta | None = None
) -> tuple[str, datetime]:
    """Short-lived JWT proving the user verified an OTP.

    Scoped `password_reset` so it can never double as an access token, and kept separate from
    the session-backed `create_access_token` — it is never stored anywhere.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.PASSWORD_RESET_JWT_EXPIRE_MINUTES
        )
    expire_naive = expire.replace(tzinfo=None)

    to_encode = {"exp": expire, "sub": str(user_id), "scope": "password_reset"}
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt, expire_naive


def decode_password_reset_token(token: str) -> str:
    """Return the subject (`user_id` as str) of a valid reset JWT, else raise InvalidResetTokenException."""
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
    except jwt.PyJWTError:
        raise InvalidResetTokenException()

    if payload.get("scope") != "password_reset" or not payload.get("sub"):
        raise InvalidResetTokenException()

    return str(payload["sub"])


def require_permission(
    feature_key: str,
    permission_name: str
):
    async def dependency(
        db=Depends(get_db),
        current_user=Depends(get_current_user)
    ):

        # if current_user.role.roleName == "Super Admin":
        #     return current_user

        allowed = await hasPermissions(
            db=db,
            role_id=current_user.role_id,
            feature_key=feature_key,
            permission_name=permission_name
        )

        if not allowed:
            raise PermissionRequired()

        return current_user

    return dependency