import logging
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.models.job_role import JobRole
from app.models.projects import Projects
from app.models.techstacks import TechStacks
from app.models.user_project import UserProject


def _user_project_detail_query():
    """Allocation rows joined to the names of their project, job role and techstack.

    Inner joins are safe: all three FKs are NOT NULL, so every allocation has a match.
    Returns (UserProject, project_name, role_name, techstack_name) tuples.
    """

    return (
        select(
            UserProject,
            Projects.project_name,
            JobRole.roleName,
            TechStacks.techstack_name,
        )
        .join(Projects, UserProject.project_id == Projects.project_id)
        .join(JobRole, UserProject.role_id == JobRole.id)
        .join(TechStacks, UserProject.techstack_id == TechStacks.techstack_id)
    )


async def get_user_project_configurations(db: AsyncSession):
    """Names available when building an allocation, one query per lookup table."""

    try:
        projects = await db.execute(
            select(Projects.project_name).order_by(Projects.project_name)
        )
        roles = await db.execute(
            select(JobRole.roleName)
            .where(JobRole.is_active == True)
            .order_by(JobRole.roleName)
        )
        techstacks = await db.execute(
            select(TechStacks.techstack_name)
            .where(TechStacks.is_active == True)
            .order_by(TechStacks.techstack_name)
        )

        return (
            projects.scalars().all(),
            roles.scalars().all(),
            techstacks.scalars().all(),
        )
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not find User Project configurations")
        raise e


async def get_all_user_projects(db: AsyncSession, user_id: UUID | None = None):
    try:
        query = _user_project_detail_query()
        if user_id is not None:
            query = query.where(UserProject.user_id == user_id)

        result = await db.execute(query)
        return result.all()
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not find User Projects")
        raise e


async def get_user_project_by_id(db: AsyncSession, user_project_id: UUID):
    try:
        result = await db.execute(
            _user_project_detail_query().where(
                UserProject.user_project_id == user_project_id
            )
        )
        return result.first()
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not find User Project")
        raise e


async def get_allocation_user_id(db: AsyncSession, user_project_id: UUID) -> UUID | None:
    """Just the `user_id` an allocation currently holds, or None when there is no such row.

    Read *before* an update or delete: after either, the previous holder is unrecoverable and
    the auto-bench sync would have nobody to check.
    """
    try:
        result = await db.execute(
            select(UserProject.user_id).where(
                UserProject.user_project_id == user_project_id
            )
        )
        return result.scalars().first()
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not find the User Project allocation holder")
        raise e


async def get_user_ids_by_project(db: AsyncSession, project_id: UUID) -> list[UUID]:
    """Distinct users allocated to a project.

    `user_projects.project_id` is `ondelete="CASCADE"`, so these rows vanish with the project —
    collect them before the delete or they cannot be recovered afterwards.
    """
    try:
        result = await db.execute(
            select(UserProject.user_id)
            .where(UserProject.project_id == project_id)
            .distinct()
        )
        return list(result.scalars().all())
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not find the users allocated to the project")
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