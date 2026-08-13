from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

import jwt
from passlib.context import CryptContext

from app.core.settings import settings
from app.core.connections.postgres import get_db
from app.api.deps import get_current_user
from app.services.db.role_permissions import hasPermissions
from fastapi import Depends
from app.exceptions.auth import (
    PermissionRequired,
    InvalidResetTokenException,
    SessionExpiredException,
)

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# Marks a token as usable only for opening a notification stream.
STREAM_TOKEN_TYPE = "notification_stream"


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


def create_stream_token(user_id: UUID, session_id: UUID) -> str:
    """Short-lived, single-purpose credential for `GET /notifications/stream`.

    Carries the session id rather than the access token so that opening a stream never
    puts a reusable bearer credential in a URL, while logout can still close it.
    """
    expire = datetime.now(timezone.utc) + timedelta(
        seconds=settings.STREAM_TOKEN_EXPIRE_SECONDS
    )
    return jwt.encode(
        {
            "sub": str(user_id),
            "sid": str(session_id),
            "typ": STREAM_TOKEN_TYPE,
            "exp": expire,
        },
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_stream_token(token: str) -> tuple[UUID, UUID]:
    """Returns (user_id, session_id); raises if the token is expired, forged or misused."""
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
    except jwt.InvalidTokenError:
        raise SessionExpiredException()

    # An ordinary access token must not be accepted here — it outlives this one by hours,
    # and the whole point of the short window is that the URL copy goes stale fast.
    if payload.get("typ") != STREAM_TOKEN_TYPE:
        raise SessionExpiredException()

    try:
        return UUID(payload["sub"]), UUID(payload["sid"])
    except (KeyError, TypeError, ValueError):
        raise SessionExpiredException()


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