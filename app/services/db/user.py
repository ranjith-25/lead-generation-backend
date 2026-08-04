from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
import logging

async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    try : 
        result = await db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    except Exception as e:
        logging.exception("Could not fetch database record")
        raise


async def get_user_by_id(db: AsyncSession, user_id: UUID) -> User | None:
    result = await db.execute(select(User).where(User.user_id == user_id))
    return result.scalars().first()

async def getAllUsers(db: AsyncSession) -> list[User]:
    result = await db.execute(select(User))
    return result.scalars().all()
