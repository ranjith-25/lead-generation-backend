import logging
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.models.branch import Branch
from app.models.user_personal_info import UserPersonalInfo


async def get_all_branches(db: AsyncSession):
    try:
        result = await db.execute(select(Branch).where(Branch.is_active == True))
        return result.scalars().all()
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not find Branches")
        raise e


async def get_branch_by_id(db: AsyncSession, branch_id: UUID):
    try:
        result = await db.execute(select(Branch).where(Branch.id == branch_id, Branch.is_active == True))
        return result.scalars().first()
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not find Branch")
        raise e


async def create_branch(db: AsyncSession, branch: Branch):
    try:
        db.add(branch)
        await db.commit()
        await db.refresh(branch)
        return branch
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not create Branch")
        raise e


async def update_branch(db: AsyncSession, update_data: dict, branch_id: UUID):
    try:
        result = await db.execute(select(Branch).where(Branch.id == branch_id, Branch.is_active == True))
        db_branch = result.scalars().first()

        if not db_branch:
            return None

        for key, value in update_data.items():
            if key != "id":
                setattr(db_branch, key, value)

        await db.commit()
        await db.refresh(db_branch)
        return db_branch
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not update Branch")
        raise e


async def delete_branch(db: AsyncSession, branch_id: UUID):
    try:
        result = await db.execute(select(Branch).where(Branch.id == branch_id))
        db_branch = result.scalars().first()
        if not db_branch:
            return None
        await db.delete(db_branch)
        await db.commit()
        return db_branch
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not delete Branch")
        raise e
