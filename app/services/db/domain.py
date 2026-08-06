from sqlalchemy import func, select
from app.models.project_domains import ProjectDomain
from sqlalchemy.ext.asyncio import AsyncSession

async def get_domains_by_id_db(db: AsyncSession, domain_id: int):
    result = await db.execute(select(ProjectDomain).where(ProjectDomain.id == domain_id))
    return result.scalars().first()

async def get_all_domains_db(db: AsyncSession, limit: int, offset: int) -> list[ProjectDomain]:
    result = await db.execute(
        select(ProjectDomain).order_by(ProjectDomain.project_id).offset(offset).limit(limit)
    )
    return list(result.scalars().all())


async def count_domains_db(db: AsyncSession) -> int:
    result = await db.execute(select(func.count()).select_from(ProjectDomain))
    return result.scalar_one()


async def get_domain_by_name_db(db: AsyncSession, project_name: str) -> ProjectDomain | None:
    result = await db.execute(select(ProjectDomain).where(ProjectDomain.project_name == project_name))
    return result.scalars().first()


async def add_domain_db(db: AsyncSession, domain: ProjectDomain) -> ProjectDomain:
    db.add(domain)
    await db.commit()
    await db.refresh(domain)
    return domain


async def update_domain_db(db: AsyncSession, domain: ProjectDomain, update_data: dict) -> ProjectDomain:
    for key, value in update_data.items():
        setattr(domain, key, value)
    db.add(domain)
    await db.commit()
    await db.refresh(domain)
    return domain


async def delete_domain_db(db: AsyncSession, domain: ProjectDomain) -> None:
    await db.delete(domain)
    await db.commit()
