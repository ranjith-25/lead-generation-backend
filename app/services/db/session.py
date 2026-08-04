from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import Session


async def create_session(db: AsyncSession, user_id: int, token: str, expires_at: datetime) -> Session:
    session = Session(user_id=user_id, token=token, expiresAt=expires_at)
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def get_session_by_token(db: AsyncSession, token: str) -> Session | None:
    result = await db.execute(select(Session).where(Session.token == token))
    return result.scalars().first()


async def revoke_session(db: AsyncSession, token: str) -> bool:
    session = await get_session_by_token(db, token)
    if session:
        session.isRevoked = True
        await db.commit()
        return True
    return False
