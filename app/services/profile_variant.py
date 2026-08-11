import logging
import re
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.exceptions.custom import NotFoundException
from app.exceptions.ai_exception import handle_ai_exception
from app.core.connections.ai_connection import get_ai_client
from app.models import JobRole
from app.models.profile_variant import ProfileVariant, ProfileVariantProject
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
from app.services.db.user import get_user_by_id
from app.services.db.user_personal_info import get_user_personal_info_by_user_id
from app.services.db.branch import get_branch_by_id
from app.services.db.project_domains import get_project_domain_by_id


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


def parse_experience_years(exp: str) -> int:
    if not exp:
        return 0
    try:
        match = re.search(r"[-+]?\d*\.\d+|\d+", exp)
        if match:
            return int(float(match.group(0)))
        return 0
    except Exception:
        return 0


async def ingest_profile_variant_to_ai(db: AsyncSession, profile_variant: ProfileVariant) -> dict | None:
    # 1. Fetch user (for email) explicitly using DB layer to avoid ORM lazy load (MissingGreenlet)
    user = await get_user_by_id(db, profile_variant.user_id)
    email = user.email if (user and user.email) else ""

    # 2. Fetch user personal info explicitly using DB layer
    personal_info = await get_user_personal_info_by_user_id(db, profile_variant.user_id)

    candidate_name = ""
    education = ""
    passout_year = 0
    dob = ""
    branch_name = ""

    if personal_info:
        if personal_info.last_name:
            candidate_name = f"{personal_info.first_name} {personal_info.last_name}".strip()
        else:
            candidate_name = personal_info.first_name or ""
        
        education = personal_info.highest_qualification or ""
        passout_year = personal_info.year_of_passout or 0
        dob = personal_info.date_of_birth or ""

        # Fetch branch explicitly using DB layer
        if personal_info.branch_id:
            branch = await get_branch_by_id(db, personal_info.branch_id)
            if branch and branch.name:
                branch_name = branch.name

    # 3. Construct projects array (querying explicitly to avoid lazy loading projects relation)
    projects = []
    projects_result = await db.execute(
        select(ProfileVariantProject).where(ProfileVariantProject.profile_variant_id == profile_variant.profile_variant_id)
    )
    pv_projects = projects_result.scalars().all()
    
    for proj in pv_projects:
        # Look up domain explicitly using DB layer
        domain_name = ""
        if proj.projectDomainID:
            domain_obj = await get_project_domain_by_id(db, proj.projectDomainID)
            if domain_obj and domain_obj.domain:
                domain_name = domain_obj.domain

        projects.append({
            "project_id": str(proj.project_id),
            "project_name": proj.project_name or "",
            "domain": domain_name,
            "tech_stack": proj.techstacks or [],
            "links": proj.links or {},
            "description": proj.description or ""
        })

    result = await db.execute(
        select(JobRole).where(JobRole.id == profile_variant.role)
    )
    profile_variant_role = result.scalars().first()
    profile_variant_role_name = profile_variant_role.roleName if profile_variant_role else ""

    # 4. Construct payload
    payload = {
        "candidate_id": str(profile_variant.user_id),
        "candidate_name": candidate_name,
        "email": email,
        "education": education,
        "passout_year": passout_year,
        "dob": dob,
        "branch": branch_name,
        "variants": [
            {
                "variant_id": str(profile_variant.profile_variant_id),
                "variant_title": profile_variant.name or "",
                "experience_years": parse_experience_years(profile_variant.experience),
                "role": profile_variant_role_name or "",
                "no_of_projects": len(projects),
                "tech_stacks": profile_variant.highlighted_skills or [],
                "certifications": profile_variant.certificate or [],
                "projects": projects
            }
        ]
    }

    try:
        client = get_ai_client()
        response = await client.post("/api/v1/profiles/ingest", json=payload)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as exc:
        logging.error("AI service HTTP status error: %s - Response body: %s", exc, exc.response.text)
        raise handle_ai_exception(exc) from exc
    except Exception as exc:
        logging.exception("Could not ingest profile variant %s into the AI service", profile_variant.profile_variant_id)
        raise handle_ai_exception(exc) from exc


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
        await ingest_profile_variant_to_ai(db, created_profile_variant)
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