from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.projects import Projects


async def get_all_projects_db(db: AsyncSession, limit: int, offset: int) -> list[Projects]:
    result = await db.execute(
        select(Projects).order_by(Projects.project_id).offset(offset).limit(limit)
    )
    return list(result.scalars().all())


async def count_projects_db(db: AsyncSession) -> int:
    result = await db.execute(select(func.count()).select_from(Projects))
    return result.scalar_one()


async def get_project_by_id_db(db: AsyncSession, project_id: int) -> Projects | None:
    result = await db.execute(select(Projects).where(Projects.project_id == project_id))
    return result.scalars().first()


async def get_project_by_name_db(db: AsyncSession, project_name: str) -> Projects | None:
    result = await db.execute(select(Projects).where(Projects.project_name == project_name))
    return result.scalars().first()


async def add_project_db(db: AsyncSession, project: Projects) -> Projects:
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


async def update_project_db(db: AsyncSession, project: Projects, update_data: dict) -> Projects:
    for key, value in update_data.items():
        setattr(project, key, value)
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


async def delete_project_db(db: AsyncSession, project: Projects) -> None:
    await db.delete(project)
    await db.commit()
