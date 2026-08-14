import logging
import re
import httpx
from pathlib import Path
from fastapi import UploadFile
from fastapi.exceptions import RequestValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.core.storage import has_upload, save_profile_variant
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
from app.schemas.profile_variant import (
    ProfileVariantCreate,
    ProfileVariantDTO,
    ProfileVariantProjectCreate,
    ProfileVariantUpdate,
)
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
from app.services.db.user_status import get_user_status_by_id


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
    resource_status = "On Bench"
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

        working_status_id = personal_info.working_status_id
        if working_status_id:
            # Fetch working status explicitly using DB layer
            user_status = await get_user_status_by_id(db, working_status_id)
            if user_status and user_status.displayName:
                resource_status = user_status.displayName

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
        "resource_status": resource_status,
        "email": email,
        "education": education,
        "passout_year": passout_year,
        "dob": dob,
        "branch": branch_name,
        "variants": [
            {
                "variant_id": str(profile_variant.profile_variant_id),
                "variant_title": profile_variant.name or "",
                "role": profile_variant_role_name or "",
                "experience_years": parse_experience_years(profile_variant.experience),
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
    db: AsyncSession, current_user: User, profile_variant_create: ProfileVariantCreate, upload_profile: UploadFile
) -> CreateProfileVariantResponse:
    if not has_upload(upload_profile):
        raise RequestValidationError(
            [
                {
                    "type": "missing",
                    "loc": ("body", "upload_profile"),
                    "msg": "Field required",
                    "input": None,
                }
            ]
        )

    # Validate PDF extension before inserting anything to database
    filename = upload_profile.filename or ""
    extension = Path(filename).suffix.lower()
    if extension != ".pdf":
        raise RequestValidationError(
            [
                {
                    "type": "value_error",
                    "loc": ("body", "upload_profile"),
                    "msg": "Only PDF files are allowed",
                    "input": filename,
                }
            ]
        )

    created_profile_variant = None
    stored_path = None
    try:
        # Set dummy upload_profile string to satisfy NOT NULL db constraint
        profile_variant_create.upload_profile = "placeholder"

        create_data = profile_variant_create.model_dump(exclude={"projects"})
        new_profile_variant = ProfileVariant(
            **create_data,
            created_by=current_user.user_id,
            updated_by=current_user.user_id,
        )

        # 1. Insert record into database first to let db generate profile_variant_id
        created_profile_variant = await create_profile_variant(
            db, new_profile_variant, profile_variant_create.projects or []
        )

        # 2. Save file to disk using the db-generated profile_variant_id
        stored_path = await save_profile_variant(
            upload_profile, 
            created_profile_variant.user_id, 
            created_profile_variant.profile_variant_id
        )

        # 3. Update database record with the actual stored path
        created_profile_variant.upload_profile = stored_path
        await db.commit()
        await db.refresh(created_profile_variant)

        # 4. Ingest profile variant to AI
        await ingest_profile_variant_to_ai(db, created_profile_variant)

        return CreateProfileVariantResponse(
            newProfileVariant=ProfileVariantDTO.model_validate(created_profile_variant),
            message="Profile Variant created successfully",
        )
    except Exception as e:
        if stored_path:
            project_root = Path(__file__).resolve().parents[2]
            (project_root / stored_path).unlink(missing_ok=True)
        if created_profile_variant:
            try:
                await delete_profile_variant(db, created_profile_variant.profile_variant_id)
            except Exception:
                pass
        logging.exception("Some error occurred while creating Profile Variant")
        raise e


_PDF_BACKUP_SUFFIX = ".bak"


def _restore_profile_variant_pdf(project_root: Path, stored_path: str | None, backup_path: Path | None) -> None:
    """Undo a PDF replacement: drop the newly written file and put the previous one back."""

    if stored_path:
        (project_root / stored_path).unlink(missing_ok=True)
    if backup_path and backup_path.is_file():
        backup_path.replace(backup_path.with_name(backup_path.name[: -len(_PDF_BACKUP_SUFFIX)]))


async def handle_update_profile_variant(
    db: AsyncSession,
    current_user: User,
    profile_variant_update: ProfileVariantUpdate,
    profile_variant_id: UUID,
    upload_profile: UploadFile | None = None,
) -> UpdateProfileVariantResponse:
    # Validate PDF extension before touching the database or disk
    if has_upload(upload_profile):
        filename = upload_profile.filename or ""
        extension = Path(filename).suffix.lower()
        if extension != ".pdf":
            raise RequestValidationError(
                [
                    {
                        "type": "value_error",
                        "loc": ("body", "upload_profile"),
                        "msg": "Only PDF files are allowed",
                        "input": filename,
                    }
                ]
            )

    project_root = Path(__file__).resolve().parents[2]
    previous_data = None
    previous_projects = None
    backup_path = None
    stored_path = None
    try:
        existing_profile_variant = await get_profile_variant_by_id(db, profile_variant_id)
        if existing_profile_variant is None:
            raise NotFoundException()

        # Snapshot the current row now — update_profile_variant commits, so a failed
        # ingestion can only be undone by writing the old values back
        previous_upload_profile = existing_profile_variant.upload_profile
        previous_data = {
            "name": existing_profile_variant.name,
            "role": existing_profile_variant.role,
            "experience": existing_profile_variant.experience,
            "highlighted_skills": existing_profile_variant.highlighted_skills,
            "upload_profile": previous_upload_profile,
            "certificate": existing_profile_variant.certificate,
            "is_draft": existing_profile_variant.is_draft,
            "user_id": existing_profile_variant.user_id,
            "updated_by": existing_profile_variant.updated_by,
        }
        previous_projects = [
            ProfileVariantProjectCreate(
                project_id=proj.project_id,
                project_name=proj.project_name,
                projectDomainID=proj.projectDomainID,
                techstacks=proj.techstacks,
                description=proj.description,
                links=proj.links,
            )
            for proj in existing_profile_variant.projects
        ]

        # Full replacement: every settable column comes from the request, so optional
        # fields the client left out are cleared instead of carried over
        update_data = profile_variant_update.model_dump(exclude={"projects", "upload_profile"})
        update_data["updated_by"] = current_user.user_id

        # 1. Replace the PDF on disk, keeping the old one aside until ingestion succeeds
        if has_upload(upload_profile):
            old_file = project_root / previous_upload_profile if previous_upload_profile else None
            if old_file and old_file.is_file():
                backup_path = old_file.with_name(old_file.name + _PDF_BACKUP_SUFFIX)
                old_file.replace(backup_path)

            stored_path = await save_profile_variant(
                upload_profile,
                profile_variant_update.user_id,
                profile_variant_id,
            )
            update_data["upload_profile"] = stored_path

        # 2. Update database record
        updated_profile_variant = await update_profile_variant(
            db, update_data, profile_variant_update.projects, profile_variant_id
        )
        if updated_profile_variant is None:
            raise NotFoundException()

        # 3. Ingest profile variant to AI
        await ingest_profile_variant_to_ai(db, updated_profile_variant)

        # 4. Ingestion succeeded — the replaced PDF is no longer needed
        if backup_path:
            backup_path.unlink(missing_ok=True)

        return UpdateProfileVariantResponse(
            updatedProfileVariant=ProfileVariantDTO.model_validate(updated_profile_variant),
            message="Profile Variant updated successfully",
        )
    except NotFoundException as e:
        _restore_profile_variant_pdf(project_root, stored_path, backup_path)
        logging.exception("Could not find Profile Variant")
        raise e
    except Exception as e:
        _restore_profile_variant_pdf(project_root, stored_path, backup_path)
        if previous_data is not None:
            try:
                await update_profile_variant(db, previous_data, previous_projects, profile_variant_id)
            except Exception:
                pass
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


async def handle_download_profile_variant(
    db: AsyncSession, user_id: UUID, profile_variant_id: UUID
) -> Path:
    try:
        profile_variant = await get_profile_variant_by_id(db, profile_variant_id)
        if not profile_variant:
            raise NotFoundException()
        if profile_variant.user_id != user_id:
            raise NotFoundException()

        project_root = Path(__file__).resolve().parents[2]
        file_path = project_root / profile_variant.upload_profile
        if not file_path.exists() or not file_path.is_file():
            raise NotFoundException()

        return file_path
    except NotFoundException as e:
        raise e
    except Exception as e:
        logging.exception("Some error occurred while downloading Profile Variant PDF")
        raise e