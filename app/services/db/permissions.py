from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.permissions import Permission
from sqlalchemy.exc import SQLAlchemyError
import logging


async def get_permissions(db: AsyncSession):
    try:
        permissions_list = await db.execute(select(Permission))
        permissions_list = permissions_list.scalars().all()
        return permissions_list
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not find Permissions")
        raise e


async def get_permission_by_id(db: AsyncSession, permission_id: int):
    try:
        permission_details = await db.execute(
            select(Permission).where(Permission.permission_id == permission_id)
        )
        permission_details = permission_details.scalars().first()
        return permission_details
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not find Permission")
        raise e


async def create_permission(db: AsyncSession, permission: Permission):
    try:
        db.add(permission)
        await db.commit()
        await db.refresh(permission)
        return permission
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not create Permission")
        raise e


async def update_permission(
    db: AsyncSession,
    permission_data: dict,
    permission_id: int
):
    try:
        result = await db.execute(
            select(Permission).where(
                Permission.permission_id == permission_id
            )
        )
        db_permission = result.scalars().first()

        if not db_permission:
            return None

        for key, value in permission_data.items():
            if key != "permission_id" and key != "id":
                setattr(db_permission, key, value)

        await db.commit()
        await db.refresh(db_permission)
        return db_permission
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not update Permission")
        raise e


async def delete_permission(db: AsyncSession, permission_id: int):
    try:
        permission_details = await db.execute(
            select(Permission).where(Permission.permission_id == permission_id)
        )
        permission_details = permission_details.scalars().first()
        if permission_details:
            await db.delete(permission_details)
            await db.commit()
        return permission_details
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not delete Permission")
        raise e
