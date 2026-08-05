from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.project import (
    DomainNotFoundException,
    ProjectAlreadyExistsException,
    ProjectNotFoundException,
    TechStackNotFoundException,
)
from app.models.projects import Projects
from app.responses.base import BaseResponse
from app.responses.project import ProjectListResponse
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate
from app.services.db.project import (
    add_project_db,
    count_projects_db,
    delete_project_db,
    get_all_projects_db,
    get_domains_by_ids_db,
    get_project_by_id_db,
    get_project_by_name_db,
    get_techstacks_by_ids_db,
    update_project_db,
)


async def _resolve_domains(db: AsyncSession, domain_ids: list[int]):
    domains = await get_domains_by_ids_db(db, domain_ids)
    missing = set(domain_ids) - {domain.domain_id for domain in domains}
    if missing:
        raise DomainNotFoundException(sorted(missing))
    return domains


async def _resolve_techstacks(db: AsyncSession, techstack_ids: list[int]):
    techstacks = await get_techstacks_by_ids_db(db, techstack_ids)
    missing = set(techstack_ids) - {techstack.techstack_id for techstack in techstacks}
    if missing:
        raise TechStackNotFoundException(sorted(missing))
    return techstacks


async def get_all_projects_service(db: AsyncSession, limit: int, page: int) -> ProjectListResponse:

    offset = (page - 1) * limit
    projects = await get_all_projects_db(db, limit, offset)
    total = await count_projects_db(db)

    return ProjectListResponse(
        message="Projects fetched successfully",
        total=total,
        page=page,
        limit=limit,
        projects=[ProjectRead.model_validate(project) for project in projects],
    )


async def get_project_service(db: AsyncSession, project_id: int) -> ProjectRead:

    project = await get_project_by_id_db(db, project_id)
    if not project:
        raise ProjectNotFoundException()

    return ProjectRead.model_validate(project)


async def create_project_service(db: AsyncSession, project_data: ProjectCreate) -> ProjectRead:

    existing = await get_project_by_name_db(db, project_data.project_name)
    if existing:
        raise ProjectAlreadyExistsException()

    new_project = Projects(
        project_name=project_data.project_name,
        description=project_data.description,
        case_study=project_data.links.case_study,
        app_link=project_data.links.app_link,
        domains=await _resolve_domains(db, project_data.domain_ids),
        techstacks=await _resolve_techstacks(db, project_data.techstack_ids),
    )

    saved_project = await add_project_db(db, new_project)
    return ProjectRead.model_validate(saved_project)


async def update_project_service(
    db: AsyncSession, project_id: int, project_data: ProjectUpdate
) -> ProjectRead:

    project = await get_project_by_id_db(db, project_id)
    if not project:
        raise ProjectNotFoundException()

    payload = project_data.model_dump(exclude_unset=True)
    update_data = {}

    if "project_name" in payload:
        existing = await get_project_by_name_db(db, payload["project_name"])
        if existing and existing.project_id != project_id:
            raise ProjectAlreadyExistsException()
        update_data["project_name"] = payload["project_name"]

    if "description" in payload:
        update_data["description"] = payload["description"]

    if payload.get("links") is not None:
        update_data["case_study"] = payload["links"]["case_study"]
        update_data["app_link"] = payload["links"]["app_link"]

    if payload.get("domain_ids") is not None:
        update_data["domains"] = await _resolve_domains(db, payload["domain_ids"])

    if payload.get("techstack_ids") is not None:
        update_data["techstacks"] = await _resolve_techstacks(db, payload["techstack_ids"])

    updated_project = await update_project_db(db, project, update_data)
    return ProjectRead.model_validate(updated_project)


async def delete_project_service(db: AsyncSession, project_id: int) -> BaseResponse:

    project = await get_project_by_id_db(db, project_id)
    if not project:
        raise ProjectNotFoundException()

    await delete_project_db(db, project)
    return BaseResponse(message="Project deleted successfully")
