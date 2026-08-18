from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import Session


async def create_session(db: AsyncSession, user_id: UUID, token: str, expires_at: datetime) -> Session:
    session = Session(user_id=user_id, token=token, expiresAt=expires_at)
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def get_session_by_token(db: AsyncSession, token: str) -> Session | None:
    result = await db.execute(select(Session).where(Session.token == token))
    return result.scalars().first()


async def get_active_session_by_id(
    db: AsyncSession, session_id: UUID, user_id: UUID
) -> Session | None:
    """Look a session up without its token — the notification stream only carries the id."""
    result = await db.execute(
        select(Session).where(
            Session.session_id == session_id,
            Session.user_id == user_id,
            Session.isRevoked.is_(False),
            Session.expiresAt > datetime.now(timezone.utc).replace(tzinfo=None),
        )
    )
    return result.scalars().first()


async def revoke_all_sessions_for_user(db: AsyncSession, user_id: UUID) -> int:
    """Revoke every live session a user holds. Returns the number revoked.

    Unlike its neighbours this does **not** commit - it is called inside the soft-delete
    transaction so the `is_deleted` flag and the revocations land together or not at all.
    """
    result = await db.execute(
        update(Session)
        .where(Session.user_id == user_id, Session.isRevoked.is_(False))
        .values(isRevoked=True)
        .execution_options(synchronize_session=False)
    )
    return result.rowcount or 0


async def revoke_session(db: AsyncSession, token: str) -> bool:
    session = await get_session_by_token(db, token)
    if session:
        session.isRevoked = True
        await db.commit()
        return True
    return False
