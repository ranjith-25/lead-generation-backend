from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from app.models.user import User

from app.models.role import Role
from app.models.user_personal_info import UserPersonalInfo
from app.models.user_invitation import UserInvitation
import logging
from uuid import UUID

async def get_all_user_by_role(db: AsyncSession, roles : list[UUID]) -> list[dict]:
    if roles is None or len(roles) == 0:
        roles = [UUID("67b38adf-f216-4208-ad2f-25db2e1f4248"), UUID("4395535d-d6f8-4069-aa42-54474ead361e")]
    try:
        query = select(
            User.user_id,
            User.email,
            User.role_id,
            User.reporting_to,
            User.createdAt,
            Role.roleName.label("role_name"),
            UserPersonalInfo.first_name,
            UserPersonalInfo.last_name,
        ).outerjoin(Role, User.role_id == Role.role_id) \
         .outerjoin(UserPersonalInfo, UserPersonalInfo.user_id == User.user_id)

        if roles:
            query = query.where(User.role_id.in_(roles))

        result = await db.execute(query)

        users = []
        for row in result:
            full_name = row.first_name or "Unknown User"
            if row.first_name and row.last_name:
                full_name = f"{row.first_name} {row.last_name}"

            users.append({
                "user_id": row.user_id,
                "full_name": full_name,
                "email": row.email,
                "role_id": row.role_id,
                "role_name": row.role_name,
                "reporting_to": row.reporting_to,
                "created_at": row.createdAt,
            })

        return users
    except SQLAlchemyError as e:
        logging.exception("Could not fetch users by role")
        raise e


async def get_user_ids_by_role_names(db: AsyncSession, role_names: list[str]) -> list[UUID]:
    """User ids for the given roles, matched by name rather than by role_id.

    Companion to `get_all_user_by_role`, which takes role_ids — those are generated per
    environment, so notification recipient lists are configured by the stable role name
    instead. An unknown name simply contributes no rows.
    """
    if not role_names:
        return []

    try:
        query = (
            select(User.user_id)
            .join(Role, User.role_id == Role.role_id)
            .where(Role.roleName.in_(role_names))
        )
        result = await db.execute(query)
        return list(result.scalars().all())
    except SQLAlchemyError as e:
        logging.exception("Could not fetch user ids by role names")
        raise e

async def get_users_by_role_id(db: AsyncSession, role_id: UUID) -> list[User]:
    """Users currently holding one role.

    Distinct from `get_all_user_by_role`, which takes a list and substitutes two hardcoded
    role_ids when handed an empty one — that fallback makes it unsafe for a caller that
    means "exactly this role".
    """
    try:
        result = await db.execute(select(User).where(User.role_id == role_id))
        return list(result.scalars().all())
    except SQLAlchemyError as e:
        logging.exception(f"Could not fetch users for role_id: {role_id}")
        raise e


async def bulk_update_users_role(db: AsyncSession, from_role_id: UUID, to_role_id: UUID) -> int:
    """Move every user on `from_role_id` to `to_role_id`. Returns the number of rows changed."""
    try:
        result = await db.execute(
            update(User)
            .where(User.role_id == from_role_id)
            .values(role_id=to_role_id)
            .execution_options(synchronize_session=False)
        )
        await db.commit()
        return result.rowcount or 0
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception(f"Could not move users from role {from_role_id} to {to_role_id}")
        raise e


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
    invitation_id: UUID,
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