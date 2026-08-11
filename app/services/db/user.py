from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from app.models.user import User

from app.models.user_personal_info import UserPersonalInfo
from app.models.user_invitation import UserInvitation
import logging
import uuid

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

async def update_user_password(db: AsyncSession, user_id: UUID, hashed_password: str) -> User | None:
    try:
        result = await db.execute(select(User).where(User.user_id == user_id))
        db_user = result.scalars().first()

        if not db_user:
            return None

        db_user.hashedPassword = hashed_password
        db_user.passwordResetAt = datetime.now(timezone.utc).replace(tzinfo=None)

        await db.commit()
        await db.refresh(db_user)
        return db_user
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception(f"Could not update password for user_id: {user_id}")
        raise e


async def getAllUsers(db: AsyncSession) -> list[User]:
    result = await db.execute(select(User))
    return result.scalars().all()

async def create_user(db : AsyncSession , user_details : User) -> str:
    try:
        db.add(user_details)
        await db.commit()
        await db.refresh(user_details)
        return str(user_details.user_id)

    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not create user")
        raise e

    except Exception as e:
        await db.rollback()
        logging.exception("Could not create user")
        raise e

async def register_user_from_invitation(
    db: AsyncSession,
    user: User,
    personal_info: UserPersonalInfo,
    invitation_id: uuid.UUID,
    invitation_update_data: dict,
) -> User:
    try:
        # Step 1: Create User
        db.add(user)
        await db.flush()          # Generates user_id without committing
        await db.refresh(user)

        # Step 2: Create Personal Info
        personal_info.user_id = user.user_id
        db.add(personal_info)

        # Step 3: Update Invitation
        result = await db.execute(
            select(UserInvitation).where(
                UserInvitation.id == invitation_id,
                UserInvitation.is_deleted == False,
            )
        )

        invitation = result.scalars().first()

        if not invitation:
            raise Exception("Invitation not found.")

        for key, value in invitation_update_data.items():
            if key != "id":
                setattr(invitation, key, value)

        invitation.user_id = user.user_id

        # Single Commit
        await db.commit()

        # Refresh objects
        await db.refresh(user)
        await db.refresh(personal_info)
        await db.refresh(invitation)

        return user

    except SQLAlchemyError:
        await db.rollback()
        logging.exception("Failed to register user from invitation")
        raise

    except Exception:
        await db.rollback()
        logging.exception("Unexpected error during invitation registration")
        raise