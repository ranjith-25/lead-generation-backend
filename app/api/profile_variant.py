from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.core.connections.postgres import get_db
from app.core.security import require_permission
from app.models.user import User
from app.responses.profile_variant import (
    CreateProfileVariantResponse,
    DeleteProfileVariantResponse,
    GetProfileVariantResponse,
    UpdateProfileVariantResponse, JobRoleSkillsResponse, ProjectsDomainsResponse,
)
from app.schemas.profile_variant import ProfileVariantCreate, ProfileVariantUpdate, DownloadProfileRequest
from app.services.profile_variant import (
    handle_create_profile_variant,
    handle_delete_profile_variant,
    handle_get_all_profile_variants,
    handle_get_profile_variant_by_id,
    handle_update_profile_variant, handle_get_job_role_skills,
    handle_get_projects_and_domains,
    handle_download_profile_variant,
)


router = APIRouter(prefix="/profile-variants", tags=["Profile Variant"])


@router.get("/")
async def get_all_profile_variants(
    current_user: User = Depends(require_permission("profile_variants", "read")),
    db: AsyncSession = Depends(get_db),
) -> GetProfileVariantResponse:
    return await handle_get_all_profile_variants(db, current_user)


@router.get("/{id}")
async def get_profile_variant_by_id(
    id: UUID,
    current_user: User = Depends(require_permission("profile_variants", "read")),
    db: AsyncSession = Depends(get_db),
) -> GetProfileVariantResponse:
    return await handle_get_profile_variant_by_id(db, current_user, id)


@router.post("/")
async def create_profile_variant(
    profile_variant: ProfileVariantCreate = Depends(ProfileVariantCreate.as_form),
    upload_profile: UploadFile = File(...),
    current_user: User = Depends(require_permission("profile_variants", "create")),
    db: AsyncSession = Depends(get_db),
) -> CreateProfileVariantResponse:
    return await handle_create_profile_variant(db, current_user, profile_variant, upload_profile)


@router.put("/{id}")
async def update_profile_variant(
    id: UUID,
    profile_variant: ProfileVariantUpdate,
    current_user: User = Depends(require_permission("profile_variants", "update")),
    db: AsyncSession = Depends(get_db),
) -> UpdateProfileVariantResponse:
    return await handle_update_profile_variant(db, current_user, profile_variant, id)


@router.delete("/{id}")
async def delete_profile_variant(
    id: UUID,
    current_user: User = Depends(require_permission("profile_variants", "delete")),
    db: AsyncSession = Depends(get_db),
) -> DeleteProfileVariantResponse:
    return await handle_delete_profile_variant(db, current_user, id)


@router.get("/configurations/roles-skills/")
async def get_job_role_skills(
    current_user: User = Depends(require_permission("profile_variants", "read")),
    db: AsyncSession = Depends(get_db)
) -> JobRoleSkillsResponse:
    return await handle_get_job_role_skills(db, current_user)


@router.get("/configurations/projects-domains/")
async def get_projects_and_domains(
    current_user: User = Depends(require_permission("profile_variants", "read")),
    db: AsyncSession = Depends(get_db)
) -> ProjectsDomainsResponse:
    return await handle_get_projects_and_domains(db, current_user)


@router.post("/download-profile")
async def download_profile_variant_pdf(
    request_data: DownloadProfileRequest,
    current_user: User = Depends(require_permission("profile_variants", "read")),
    db: AsyncSession = Depends(get_db),
) -> FileResponse:
    file_path = await handle_download_profile_variant(
        db, request_data.user_id, request_data.profile_variant_id
    )
    # Extract original filename by stripping the `<uuid>_` prefix
    parts = file_path.name.split("_", 1)
    original_filename = parts[1] if len(parts) > 1 else file_path.name
    return FileResponse(file_path, media_type="application/pdf", filename=original_filename)