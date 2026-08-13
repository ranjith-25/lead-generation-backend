import logging
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.models.user_project import UserProject


async def get_all_user_projects(db: AsyncSession, user_id: UUID | None = None):
    try:
        query = select(UserProject)
        if user_id is not None:
            query = query.where(UserProject.user_id == user_id)

        result = await db.execute(query)
        return result.scalars().all()
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not find User Projects")
        raise e


async def get_user_project_by_id(db: AsyncSession, user_project_id: UUID):
    try:
        result = await db.execute(
            select(UserProject).where(UserProject.user_project_id == user_project_id)
        )
        return result.scalars().first()
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not find User Project")
        raise e


async def create_user_project(db: AsyncSession, user_project: UserProject):
    try:
        db.add(user_project)
        await db.commit()
        await db.refresh(user_project)
        return user_project
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not create User Project")
        raise e


async def update_user_project(db: AsyncSession, update_data: dict, user_project_id: UUID):
    try:
        result = await db.execute(
            select(UserProject).where(UserProject.user_project_id == user_project_id)
        )
        db_user_project = result.scalars().first()

        if not db_user_project:
            return None

        for key, value in update_data.items():
            if key != "user_project_id":
                setattr(db_user_project, key, value)

        await db.commit()
        await db.refresh(db_user_project)
        return db_user_project
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not update User Project")
        raise e


async def delete_user_project(db: AsyncSession, user_project_id: UUID):
    try:
        result = await db.execute(
            select(UserProject).where(UserProject.user_project_id == user_project_id)
        )
        db_user_project = result.scalars().first()
        if not db_user_project:
            return None
        await db.delete(db_user_project)
        await db.commit()
        return db_user_project
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not delete User Project")
        raise e