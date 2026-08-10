from fastapi import APIRouter, Depends
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
from app.schemas.profile_variant import ProfileVariantCreate, ProfileVariantUpdate
from app.services.profile_variant import (
    handle_create_profile_variant,
    handle_delete_profile_variant,
    handle_get_all_profile_variants,
    handle_get_profile_variant_by_id,
    handle_update_profile_variant, handle_get_job_role_skills,
    handle_get_projects_and_domains,
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
    profile_variant: ProfileVariantCreate,
    current_user: User = Depends(require_permission("profile_variants", "create")),
    db: AsyncSession = Depends(get_db),
) -> CreateProfileVariantResponse:
    return await handle_create_profile_variant(db, current_user, profile_variant)


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