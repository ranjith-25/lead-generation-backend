from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.job_roles import JobRoles
from sqlalchemy.exc import SQLAlchemyError
import logging


async def get_job_roles(db: AsyncSession):
    try:
        job_roles_list = await db.execute(select(JobRoles).where(JobRoles.is_active == True))
        job_roles_list = job_roles_list.scalars().all()
        return job_roles_list
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not find Job Roles")
        raise e


async def get_job_role_by_id(db: AsyncSession, job_role_id: int):
    try:
        job_role_details = await db.execute(
            select(JobRoles).where(JobRoles.id == job_role_id, JobRoles.is_active == True)
        )
        job_role_details = job_role_details.scalars().first()
        return job_role_details
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not find Job Roles")
        raise e


async def create_job_role(db: AsyncSession, job_role: JobRoles):
    try:
        db.add(job_role)
        await db.commit()
        await db.refresh(job_role)
        return job_role
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not create Job Role")
        raise e


async def update_job_role(
    db: AsyncSession,
    job_role: dict,
    job_role_id: int
):
    try:
        result = await db.execute(
            select(JobRoles).where(
                JobRoles.id == job_role_id
            )
        )
        db_job_role = result.scalars().first()

        if not db_job_role:
            return None

        for key, value in job_role.items():
            if key != "id":
                setattr(db_job_role, key, value)

        await db.commit()
        await db.refresh(db_job_role)
        return db_job_role

    except SQLAlchemyError:
        await db.rollback()
        logging.exception("Could not update Job Role")
        raise


async def delete_job_role(db: AsyncSession, job_role_id: int):
    try:
        job_role_details = await db.execute(
            select(JobRoles).where(JobRoles.id == job_role_id)
        )
        job_role_details = job_role_details.scalars().first()
        if job_role_details:
            await db.delete(job_role_details)
            await db.commit()
        return job_role_details
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not delete Job Role")
        raise e
