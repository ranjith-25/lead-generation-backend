import uuid

from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.custom import AppException
from app.exceptions.error_codes import ErrorCode
from app.exceptions.project import ProjectDomainNotFoundException
from app.models.project_domains import ProjectDomain
from app.responses.base import BaseResponse
from app.responses.domain import DomainsListResponse
from app.schemas.project_domains import (
    ProjectDomainCreate,
    ProjectDomainRead,
    ProjectDomainUpdate,
)

from app.services.db.domain import (
    get_all_domains_db,
    count_domains_db,
    get_domains_by_id_db,
    get_domain_by_name_db,
    add_domain_db,
    update_domain_db,
    delete_domain_db,
)


def _domain_already_exists() -> AppException:
    return AppException(
        message="A domain with this name already exists",
        status_code=status.HTTP_409_CONFLICT,
        error_code=ErrorCode.DUPLICATE_RECORD,
    )


async def get_all_domains(db: AsyncSession, limit: int, page: int) -> DomainsListResponse:
    offset = (page - 1) * limit
    projects = await get_all_domains_db(db, limit, offset)
    total = await count_domains_db(db)

    return DomainsListResponse(
            message="Projects fetched successfully",
            total=total,
            page=page,
            limit=limit,
            projects=[ProjectDomainRead.model_validate(project) for project in projects],
        )


async def get_domain(db: AsyncSession, domain_id: int) -> ProjectDomainRead:
    domain = await get_domains_by_id_db(db, domain_id)
    if not domain:
        raise ProjectDomainNotFoundException(domain_id)

    return ProjectDomainRead.model_validate(domain)


async def create_domain(
    db: AsyncSession, domain_data: ProjectDomainCreate, user_id: uuid.UUID
) -> ProjectDomainRead:
    existing = await get_domain_by_name_db(db, domain_data.domain)
    if existing:
        raise _domain_already_exists()

    new_domain = ProjectDomain(
        domain=domain_data.domain,
        description=domain_data.description,
        is_active=domain_data.is_active,
        createdBy=user_id,
        updatedBy=user_id,
    )

    saved_domain = await add_domain_db(db, new_domain)
    return ProjectDomainRead.model_validate(saved_domain)


async def update_domain(
    db: AsyncSession, domain_id: int, domain_data: ProjectDomainUpdate, user_id: uuid.UUID
) -> ProjectDomainRead:
    domain = await get_domains_by_id_db(db, domain_id)
    if not domain:
        raise ProjectDomainNotFoundException(domain_id)

    payload = domain_data.model_dump(exclude_unset=True, exclude_none=True)
    update_data = {}

    if "domain" in payload:
        existing = await get_domain_by_name_db(db, payload["domain"])
        if existing and existing.id != domain_id:
            raise _domain_already_exists()
        update_data["domain"] = payload["domain"]

    if "description" in payload:
        update_data["description"] = payload["description"]

    if "is_active" in payload:
        update_data["is_active"] = payload["is_active"]

    update_data["updatedBy"] = user_id

    updated_domain = await update_domain_db(db, domain, update_data)
    return ProjectDomainRead.model_validate(updated_domain)


async def delete_domain(db: AsyncSession, domain_id: int) -> BaseResponse:
    domain = await get_domains_by_id_db(db, domain_id)
    if not domain:
        raise ProjectDomainNotFoundException(domain_id)

    await delete_domain_db(db, domain)
    return BaseResponse(message="Domain deleted successfully")
