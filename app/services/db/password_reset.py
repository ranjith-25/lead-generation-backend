import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.password_reset_token import PasswordResetToken
from app.models.user import Session, User


async def create_password_reset_token(
    db: AsyncSession, user_id: UUID, token_hash: str, expires_at: datetime
) -> PasswordResetToken:
    try:
        await db.execute(
            update(PasswordResetToken)
            .where(
                PasswordResetToken.user_id == user_id,
                PasswordResetToken.used_at.is_(None),
            )
            .values(used_at=datetime.now(timezone.utc).replace(tzinfo=None))
        )

        reset_token = PasswordResetToken(
            user_id=user_id, token_hash=token_hash, expires_at=expires_at
        )
        db.add(reset_token)

        await db.commit()
        await db.refresh(reset_token)
        return reset_token
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not create a password reset token for user_id: %s", user_id)
        raise e


async def get_password_reset_token_by_user_and_hash(
    db: AsyncSession, user_id: UUID, token_hash: str
) -> PasswordResetToken | None:
    """Fetch by user + digest regardless of expiry/use — the caller decides, so it can log the reason."""

    try:
        result = await db.execute(
            select(PasswordResetToken).where(
                PasswordResetToken.user_id == user_id,
                PasswordResetToken.token_hash == token_hash,
            )
        )
        return result.scalars().first()
    except SQLAlchemyError as e:
        logging.exception("Could not fetch the password reset token")
        raise e


async def spend_password_reset_token(
    db: AsyncSession, reset_token: PasswordResetToken
) -> None:
    """Stamp the OTP as used so it cannot be replayed."""
    try:
        reset_token.used_at = datetime.now(timezone.utc).replace(tzinfo=None)
        await db.commit()
        await db.refresh(reset_token)
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not spend the password reset token")
        raise e


async def reset_password_by_user_id(
    db: AsyncSession, user_id: UUID, hashed_password: str
) -> User | None:
    """Set the new password and revoke every session — one transaction.

    These two have to commit together. Split apart, a failure between them leaves the password
    changed while the account is still reachable by whoever prompted the reset.
    """

    try:
        result = await db.execute(select(User).where(User.user_id == user_id))
        db_user = result.scalars().first()

        if not db_user:
            return None

        now = datetime.now(timezone.utc).replace(tzinfo=None)

        db_user.hashedPassword = hashed_password
        db_user.passwordResetAt = now

        await db.execute(
            update(Session)
            .where(Session.user_id == db_user.user_id, Session.isRevoked.is_(False))
            .values(isRevoked=True)
        )

        await db.commit()
        await db.refresh(db_user)
        return db_user
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception(
            "Could not complete the password reset for user_id: %s", user_id
        )
        raise e
