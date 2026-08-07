import logging
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role import Role


async def create_role(db: AsyncSession, role: Role) -> Role:
    try:
        db.add(role)
        await db.commit()
        await db.refresh(role)
        return role
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not create Role")
        raise e


async def get_role_by_id(db: AsyncSession, role_id: int) -> Role | None:
    try:
        result = await db.execute(select(Role).where(Role.role_id == role_id))
        return result.scalars().first()
    except SQLAlchemyError as e:
        logging.exception(f"Could not fetch Role for role_id: {role_id}")
        raise e


async def get_all_roles(db: AsyncSession) -> list[Role]:
    try:
        result = await db.execute(select(Role))
        return list(result.scalars().all())
    except SQLAlchemyError as e:
        logging.exception("Could not fetch Roles")
        raise e


async def update_role(db: AsyncSession, update_data: dict, role_id: int) -> Role | None:
    try:
        result = await db.execute(select(Role).where(Role.role_id == role_id))
        db_role = result.scalars().first()

        if not db_role:
            return None

        for key, value in update_data.items():
            if hasattr(db_role, key):
                setattr(db_role, key, value)

        await db.commit()
        await db.refresh(db_role)
        return db_role
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception(f"Could not update Role for role_id: {role_id}")
        raise e


async def delete_role(db: AsyncSession, role_id: int) -> Role | None:
    try:
        result = await db.execute(select(Role).where(Role.role_id == role_id))
        db_role = result.scalars().first()
        
        if not db_role:
            return None
            
        await db.delete(db_role)
        await db.commit()
        return db_role
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception(f"Could not delete Role for role_id: {role_id}")
        raise e
