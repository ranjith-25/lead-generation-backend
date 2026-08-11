from sqlalchemy import func, select
from app.models.techstacks import TechStacks
from app.schemas.techstack import TechstackFilters
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

async def get_techstacks_by_ids_db(db: AsyncSession, techstack_ids: list[UUID]) -> list[TechStacks]:
    if not techstack_ids:
        return []
    result = await db.execute(
        select(TechStacks).where(TechStacks.techstack_id.in_(techstack_ids))
    )
    return list(result.scalars().all())

async def get_techstack_by_id_db(db: AsyncSession, techstack_id: UUID) -> TechStacks | None:
    result = await db.execute(select(TechStacks).where(TechStacks.techstack_id == techstack_id))
    return result.scalars().first()


async def get_all_techstacks_db(db: AsyncSession, filters: TechstackFilters) -> list[TechStacks]:
    offset = 0
    if filters.limit is not None:
        offset = (filters.page - 1) * filters.limit
    statement = select(TechStacks).order_by(TechStacks.techstack_id).offset(offset).limit(filters.limit)
    result = await db.execute(statement)
    return list(result.scalars().all())


async def count_techstacks_db(db: AsyncSession) -> int:
    result = await db.execute(select(func.count()).select_from(TechStacks))
    return result.scalar_one()


async def get_techstack_by_name_db(db: AsyncSession, techstack_name: str) -> TechStacks | None:
    result = await db.execute(select(TechStacks).where(TechStacks.techstack_name == techstack_name))
    return result.scalars().first()


async def add_techstack_db(db: AsyncSession, techstack: TechStacks) -> TechStacks:
    db.add(techstack)
    await db.commit()
    await db.refresh(techstack)
    return techstack


async def update_techstack_db(db: AsyncSession, techstack: TechStacks, update_data: dict) -> TechStacks:
    for key, value in update_data.items():
        setattr(techstack, key, value)
    db.add(techstack)
    await db.commit()
    await db.refresh(techstack)
    return techstack


async def delete_techstack_db(db: AsyncSession, techstack: TechStacks) -> None:
    await db.delete(techstack)
    await db.commit()
