import logging
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.models.job_role import JobRole
from app.schemas.job_role import JobRoleFilters, JobRoleRead

async def get_all_job_roles(db: AsyncSession, filters : JobRoleFilters) -> list[JobRoleRead]:
    try:
        offset = 0
        if filters.limit:
            offset = (filters.page - 1) * filters.limit
        result = await db.execute(select(JobRole).where(JobRole.is_active == True).offset(offset).limit(filters.limit).order_by(JobRole.roleName))
        return result.scalars().all()
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not find Job Roles")
        raise e


async def get_job_role_by_id(db: AsyncSession, job_role_id: UUID):
    try:
        result = await db.execute(
            select(JobRole).where(
                JobRole.id == job_role_id,
                JobRole.is_active == True,
            )
        )
        return result.scalars().first()
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not find Job Role")
        raise e


async def create_job_role(db: AsyncSession, job_role: JobRole):
    try:
        db.add(job_role)
        await db.commit()
        await db.refresh(job_role)
        return job_role
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not create Job Role")
        raise e


async def update_job_role(db: AsyncSession, update_data: dict, job_role_id: UUID):
    try:
        result = await db.execute(
            select(JobRole).where(
                JobRole.id == job_role_id,
                JobRole.is_active == True,
            )
        )
        db_job_role = result.scalars().first()

        if not db_job_role:
            return None

        for key, value in update_data.items():
            if key != "id":
                setattr(db_job_role, key, value)

        await db.commit()
        await db.refresh(db_job_role)
        return db_job_role
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not update Job Role")
        raise e


async def delete_job_role(db: AsyncSession, job_role_id: UUID):
    try:
        result = await db.execute(select(JobRole).where(JobRole.id == job_role_id))
        db_job_role = result.scalars().first()
        if not db_job_role:
            return None
        await db.delete(db_job_role)
        await db.commit()
        return db_job_role
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not delete Job Role")
        raise e
