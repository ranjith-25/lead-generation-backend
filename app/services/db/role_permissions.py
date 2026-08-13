from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from app.models.role_permissions import RolePermission
from app.models.role import Role
from app.models.feature import Feature
from app.models.permissions import Permission
from app.config import SUPER_ADMIN_ROLE_NAME
import logging
async def get_feature_names_by_role_id(
    db: AsyncSession,
    role_id: UUID,
) -> list[str]:
    query = (
        select(Feature.display_name)
        .distinct()
        .join(RolePermission, Feature.feature_id == RolePermission.feature_id)
        .where(RolePermission.role_id == role_id)
    )

    result = await db.execute(query)
    return result.scalars().all()



async def hasPermissions(db: AsyncSession, role_id: UUID, feature_key: str, permission_name: str) -> bool: 
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

async def add_role_permission_db(db: AsyncSession, role_permission: RolePermission) -> RolePermission:
    db.add(role_permission)
    await db.commit()
    await db.refresh(role_permission)
    return role_permission

async def get_role_permission_by_id_db(db: AsyncSession, rp_id: UUID) -> RolePermission | None:
    result = await db.execute(
        select(RolePermission).where(
            RolePermission.role_permission_id == rp_id,
            RolePermission.isDeleted == False
        )
    )
    return result.scalars().first()

async def get_all_role_permissions_db(db: AsyncSession) -> list[RolePermission]:
    result = await db.execute(
        select(RolePermission)
        .join(Role, RolePermission.role_id == Role.role_id)
        .where(
            RolePermission.isDeleted == False,
            Role.roleName != SUPER_ADMIN_ROLE_NAME
        )
    )
    return list(result.scalars().all())

async def get_role_permission_by_details_db(
    db: AsyncSession, role_id: UUID, feature_id: UUID, permission_id: UUID
) -> RolePermission | None:
    result = await db.execute(
        select(RolePermission).where(
            RolePermission.role_id == role_id,
            RolePermission.feature_id == feature_id,
            RolePermission.permission_id == permission_id
        )
    )
    return result.scalars().first()

async def update_role_permission_db(
    db: AsyncSession, role_permission: RolePermission, update_data: dict
) -> RolePermission:
    for key, value in update_data.items():
        setattr(role_permission, key, value)
    db.add(role_permission)
    await db.commit()
    await db.refresh(role_permission)
    return role_permission

async def delete_role_permission_db(db: AsyncSession, role_permission: RolePermission) -> None:
    role_permission.isDeleted = True
    db.add(role_permission)
    await db.commit()

