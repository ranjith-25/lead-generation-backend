import logging
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.models.profile_variant import ProfileVariant, ProfileVariantProject


async def get_all_profile_variants(db: AsyncSession):
    try:
        result = await db.execute(select(ProfileVariant))
        return result.scalars().all()
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not find Profile Variants")
        raise e


async def get_profile_variant_by_id(db: AsyncSession, profile_variant_id: UUID):
    try:
        result = await db.execute(
            select(ProfileVariant).where(ProfileVariant.profile_variant_id == profile_variant_id)
        )
        return result.scalars().first()
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not find Profile Variant")
        raise e


async def create_profile_variant(db: AsyncSession, profile_variant: ProfileVariant, projects_data: list):
    try:
        if projects_data:
            for proj in projects_data:
                pv_project = ProfileVariantProject(
                    project_id=proj.project_id,
                    project_name=proj.project_name,
                    projectDomainID=proj.projectDomainID,
                    techstacks=proj.techstacks,
                    description=proj.description,
                    links=proj.links
                )
                profile_variant.projects.append(pv_project)
        
        db.add(profile_variant)
        await db.commit()
        await db.refresh(profile_variant)
        return profile_variant
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not create Profile Variant")
        raise e


async def update_profile_variant(db: AsyncSession, update_data: dict, projects_data: list | None, profile_variant_id: UUID):
    try:
        result = await db.execute(
            select(ProfileVariant).where(ProfileVariant.profile_variant_id == profile_variant_id)
        )
        db_profile_variant = result.scalars().first()

        if not db_profile_variant:
            return None

        # Update standard columns
        for key, value in update_data.items():
            if key not in ("profile_variant_id", "projects"):
                setattr(db_profile_variant, key, value) # db_profile_variant.key = value

        # Update M2M Projects relation if provided
        if projects_data is not None:
            # Clear old mappings (orphan removal deletes them from DB)
            db_profile_variant.projects = []
            
            if projects_data:
                for proj in projects_data:
                    pv_project = ProfileVariantProject(
                        project_id=proj.project_id,
                        project_name=proj.project_name,
                        projectDomainID=proj.projectDomainID,
                        techstacks=proj.techstacks,
                        description=proj.description,
                        links=proj.links
                    )
                    db_profile_variant.projects.append(pv_project)

        await db.commit()
        await db.refresh(db_profile_variant)
        return db_profile_variant
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not update Profile Variant")
        raise e


async def delete_profile_variant(db: AsyncSession, profile_variant_id: UUID):
    try:
        result = await db.execute(
            select(ProfileVariant).where(ProfileVariant.profile_variant_id == profile_variant_id)
        )
        db_profile_variant = result.scalars().first()
        if not db_profile_variant:
            return None
        await db.delete(db_profile_variant)
        await db.commit()
        return db_profile_variant
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not delete Profile Variant")
        raise e