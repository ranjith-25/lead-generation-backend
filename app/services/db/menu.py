from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.menu import Menu, MenuRole


async def get_menu_names_by_role_id(db: AsyncSession, role_id: UUID) -> list[str]:
    query = select(Menu.name).join(MenuRole, Menu.menu_id == MenuRole.menu_id).where(MenuRole.role_id == role_id)
    result = await db.execute(query)
    return list(result.scalars().all())
