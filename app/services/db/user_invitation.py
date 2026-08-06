import logging
import uuid
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_invitation import UserInvitation


async def get_all_user_invitations(db: AsyncSession):
    try:
        result = await db.execute(select(UserInvitation).where(UserInvitation.is_deleted == False))
        return result.scalars().all()
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not find User Invitations")
        raise e


async def get_user_invitation_by_id(db: AsyncSession, user_invitation_id: uuid.UUID):
    try:
        result = await db.execute(
            select(UserInvitation).where(
                UserInvitation.id == user_invitation_id,
                UserInvitation.is_deleted == False,
            )
        )
        return result.scalars().first()
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not find User Invitation")
        raise e


async def create_user_invitation(db: AsyncSession, user_invitation: UserInvitation):
    try:
        db.add(user_invitation)
        await db.commit()
        await db.refresh(user_invitation)
        return user_invitation
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not create User Invitation")
        raise e


async def update_user_invitation(db: AsyncSession, update_data: dict, user_invitation_id: uuid.UUID):
    try:
        result = await db.execute(
            select(UserInvitation).where(
                UserInvitation.id == user_invitation_id,
                UserInvitation.is_deleted == False,
            )
        )
        db_user_invitation = result.scalars().first()

        if not db_user_invitation:
            return None

        for key, value in update_data.items():
            if key != "id":
                setattr(db_user_invitation, key, value)

        await db.commit()
        await db.refresh(db_user_invitation)
        return db_user_invitation
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not update User Invitation")
        raise e


async def delete_user_invitation(db: AsyncSession, user_invitation_id: uuid.UUID):
    try:
        result = await db.execute(select(UserInvitation).where(UserInvitation.id == user_invitation_id))
        db_user_invitation = result.scalars().first()
        if not db_user_invitation:
            return None
        db_user_invitation.is_deleted = True
        await db.commit()
        return db_user_invitation
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not delete User Invitation")
        raise e
