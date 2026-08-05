from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.role_permisions import RolePermission
from app.models.user import Role
from app.models.feature import Feature
from app.models.permissions import Permission

async def add_role_permission_db(db: AsyncSession, role_permission: RolePermission) -> RolePermission:
    db.add(role_permission)
    await db.commit()
    await db.refresh(role_permission)
    return role_permission

async def get_role_permission_by_id_db(db: AsyncSession, rp_id: int) -> RolePermission | None:
    result = await db.execute(
        select(RolePermission).where(
            RolePermission.role_permission_id == rp_id,
            RolePermission.isDeleted == False
        )
    )
    return result.scalars().first()

async def get_all_role_permissions_db(db: AsyncSession) -> list[RolePermission]:
    result = await db.execute(
        select(RolePermission).where(RolePermission.isDeleted == False)
    )
    return list(result.scalars().all())

async def get_role_permission_by_details_db(
    db: AsyncSession, role_id: int, feature_id: int, permission_id: int
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

async def check_role_exists_db(db: AsyncSession, role_id: int) -> bool:
    result = await db.execute(select(Role).where(Role.role_id == role_id))
    return result.scalars().first() is not None

async def check_feature_exists_db(db: AsyncSession, feature_id: int) -> bool:
    result = await db.execute(select(Feature).where(Feature.feature_id == feature_id))
    return result.scalars().first() is not None

async def check_permission_exists_db(db: AsyncSession, permission_id: int) -> bool:
    result = await db.execute(select(Permission).where(Permission.permission_id == permission_id))
    return result.scalars().first() is not None
