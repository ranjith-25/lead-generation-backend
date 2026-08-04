from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role_permisions import RolePermission
from app.models.permissions import Permission
from app.models.feature import Feature

async def get_feature_names_by_role_id(
    db: AsyncSession,
    role_id: int,
) -> list[str]:
    query = (
        select(Feature.display_name)
        .distinct()
        .join(RolePermission, Feature.feature_id == RolePermission.feature_id)
        .where(RolePermission.role_id == role_id)
    )

    result = await db.execute(query)
    return result.scalars().all()
