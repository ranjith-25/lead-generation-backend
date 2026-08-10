import logging
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.exceptions.custom import NotFoundException
from app.models.profile_variant import ProfileVariant
from app.models.user import User
from app.responses.profile_variant import (
    CreateProfileVariantResponse,
    DeleteProfileVariantResponse,
    GetProfileVariantResponse,
    UpdateProfileVariantResponse, JobRoleSkillsResponse, RoleItem, JobRoleSkillsData,
    ProjectsDomainsResponse, ProjectDomainRelationItem, ProjectItem, ProjectDomainItem,
)
from app.schemas.job_role import JobRoleFilters
from app.schemas.profile_variant import ProfileVariantCreate, ProfileVariantDTO, ProfileVariantUpdate
from app.schemas.project import ProjectFilters
from app.schemas.techstack import TechstackFilters
from app.services.db.job_role import get_all_job_roles
from app.services.db.profile_variant import (
    create_profile_variant,
    delete_profile_variant,
    get_all_profile_variants,
    get_profile_variant_by_id,
    update_profile_variant,
)
from app.services.db.techstack import get_all_techstacks_db
from app.services.db.project import get_all_projects_db


async def handle_get_all_profile_variants(db: AsyncSession, current_user: User) -> GetProfileVariantResponse:
    try:
        profile_variants = await get_all_profile_variants(db)
        if profile_variants is None:
            raise NotFoundException()

        return GetProfileVariantResponse(
            profileVariantList=[ProfileVariantDTO.model_validate(pv) for pv in profile_variants],
            message="Profile Variants fetched successfully",
        )
    except NotFoundException as e:
        logging.exception("Could not find Profile Variants")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while getting Profile Variants list")
        raise e


async def handle_get_profile_variant_by_id(db: AsyncSession, current_user: User, profile_variant_id: UUID) -> GetProfileVariantResponse:
    try:
        profile_variant = await get_profile_variant_by_id(db, profile_variant_id)
        if profile_variant is None:
            raise NotFoundException()

        return GetProfileVariantResponse(
            profileVariant=ProfileVariantDTO.model_validate(profile_variant),
            message="Profile Variant fetched successfully",
        )
    except NotFoundException as e:
        logging.exception("Could not find Profile Variant")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while getting Profile Variant details")
        raise e


async def handle_create_profile_variant(
    db: AsyncSession, current_user: User, profile_variant_create: ProfileVariantCreate
) -> CreateProfileVariantResponse:
    try:
        create_data = profile_variant_create.model_dump(exclude={"projects"})
        new_profile_variant = ProfileVariant(
            **create_data,
            created_by=current_user.user_id,
            updated_by=current_user.user_id,
        )
        created_profile_variant = await create_profile_variant(
            db, new_profile_variant, profile_variant_create.projects or []
        )
        return CreateProfileVariantResponse(
            newProfileVariant=ProfileVariantDTO.model_validate(created_profile_variant),
            message="Profile Variant created successfully",
        )
    except Exception as e:
        logging.exception("Some error occurred while creating Profile Variant")
        raise e


async def handle_update_profile_variant(
    db: AsyncSession, current_user: User, profile_variant_update: ProfileVariantUpdate, profile_variant_id: UUID
) -> UpdateProfileVariantResponse:
    try:
        update_data = profile_variant_update.model_dump(exclude={"projects"}, exclude_unset=True, exclude_none=True)
        update_data["updated_by"] = current_user.user_id
        
        updated_profile_variant = await update_profile_variant(
            db, update_data, profile_variant_update.projects, profile_variant_id
        )
        if updated_profile_variant is None:
            raise NotFoundException()

        return UpdateProfileVariantResponse(
            updatedProfileVariant=ProfileVariantDTO.model_validate(updated_profile_variant),
            message="Profile Variant updated successfully",
        )
    except NotFoundException as e:
        logging.exception("Could not find Profile Variant")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while updating Profile Variant")
        raise e


async def handle_delete_profile_variant(
    db: AsyncSession, current_user: User, profile_variant_id: UUID
) -> DeleteProfileVariantResponse:
    try:
        deleted_profile_variant = await delete_profile_variant(db, profile_variant_id)
        if deleted_profile_variant is None:
            raise NotFoundException()

        return DeleteProfileVariantResponse(
            message="Profile Variant deleted successfully",
        )
    except NotFoundException as e:
        logging.exception("Could not find Profile Variant")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while deleting Profile Variant")
        raise e


async def handle_get_job_role_skills(
        db: AsyncSession,
        current_user: User
) -> JobRoleSkillsResponse:
    try:
        # Fetch job roles (reusing the existing DB query)
        job_roles = await get_all_job_roles(db, JobRoleFilters(page=1, limit=None))
        roles_list = []
        if job_roles:
            roles_list = [
                RoleItem(job_role_name=role.roleName, job_role_id=str(role.id))
                for role in job_roles
            ]

        # Fetch tech stacks (reusing the existing DB query)
        tech_stacks = await get_all_techstacks_db(db, TechstackFilters(page=1, limit=None))
        unique_skills = []
        if tech_stacks:
            techstack_names = [ts.techstack_name for ts in tech_stacks if ts.techstack_name is not None]
            # Deduplicate in code using a set to preserve order
            seen = set()
            for name in techstack_names:
                if name not in seen:
                    seen.add(name)
                    unique_skills.append(name)

        return JobRoleSkillsResponse(
            status=True,
            message="Job Roles and Skills fetched successfully",
            data=JobRoleSkillsData(
                role=roles_list,
                highlighted_skills=unique_skills
            )
        )
    except Exception as e:
        logging.exception("Some error occurred while fetching job roles and skills")
        raise e


async def handle_get_projects_and_domains(
    db: AsyncSession,
    current_user: User
) -> ProjectsDomainsResponse:
    try:
        # Fetch all projects (reusing existing query from db layers)
        projects, _ = await get_all_projects_db(db, ProjectFilters(page=1, limit=None))
        
        data_list = []
        for project in projects:
            # Map project to ProjectItem
            proj_item = ProjectItem(
                project_name=project.project_name,
                project_id=str(project.project_id)
            )

            # Map project domain to ProjectDomainItem (ORM relation loaded via selectin)
            domain_item = None
            if project.projectDomain:
                domain_item = ProjectDomainItem(
                    project_domain_name=project.projectDomain.domain,
                    project_domain_id=str(project.projectDomain.id)
                )

            data_list.append(
                ProjectDomainRelationItem(
                    project=proj_item,
                    project_domain=domain_item
                )
            )
            
        return ProjectsDomainsResponse(
            status=True,
            message="Projects and Domains fetched successfully",
            data=data_list
        )
    except Exception as e:
        logging.exception("Some error occurred while fetching projects and domains")
        raise e