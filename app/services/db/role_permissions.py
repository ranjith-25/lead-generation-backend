from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role_permisions import RolePermission
from app.models.permissions import Permission
from app.models.feature import Feature
import logging
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



async def hasPermissions(db: AsyncSession, role_id: int, feature_key: str, permission_name: str) -> bool: 
    try : 
        stmt = (
            select(RolePermission)
            .join(Feature)
            .join(Permission)
            .where(
                RolePermission.role_id == role_id,
                Feature.feature_key == feature_key,
                Permission.permission_key == permission_name
            )
        )

        result = await db.execute(stmt)

        return result.scalar_one_or_none() is not None

    except Exception as e :
        logging.exception("Could not validate the roles.")
        raise