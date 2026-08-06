from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.storage import (
    delete_case_study,
    has_upload,
    resolve_case_study,
    save_case_study,
)
from app.exceptions.project import (
    CaseStudyNotFoundException,
    ProjectAlreadyExistsException,
    ProjectDomainNotFoundException,
    ProjectNotFoundException,
    TechStackNotFoundException,
    CantFetchFilterException
)
from app.models.projects import Projects
from app.responses.base import BaseResponse
from app.responses.project import ProjectListResponse
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate, ProjectFilters
from app.services.db.project import (
    add_project_db,
    delete_project_db,
    get_all_projects_db,
    get_project_by_id_db,
    get_project_by_name_db,
    update_project_db,
)

from app.services.db.project_domains import (
    get_project_domain_by_id,
    get_all_project_domain_db
)

from app.services.db.techstack import (
    get_techstacks_by_ids_db,
    get_all_techstacks_db
)


async def _resolve_domain(db: AsyncSession, project_domain_id: int):
    domain = await get_project_domain_by_id(db, project_domain_id)
    if not domain:
        raise ProjectDomainNotFoundException(project_domain_id)
    return domain


async def _resolve_techstacks(db: AsyncSession, techstack_ids: list[int]):
    techstacks = await get_techstacks_by_ids_db(db, techstack_ids)
    missing = set(techstack_ids) - {techstack.techstack_id for techstack in techstacks}
    if missing:
        raise TechStackNotFoundException(sorted(missing))
    return techstacks


async def get_all_projects_service(
    db: AsyncSession,
    filters: ProjectFilters,
) -> ProjectListResponse:

    projects, total = await get_all_projects_db(db, filters)

    return ProjectListResponse(
        message="Projects fetched successfully",
        total=total,
        page=filters.page,
        limit=filters.limit,
        projects=[ProjectRead.model_validate(project) for project in projects],
    )


async def get_project_service(db: AsyncSession, project_id: int) -> ProjectRead:

    project = await get_project_by_id_db(db, project_id)
    if not project:
        raise ProjectNotFoundException()

    return ProjectRead.model_validate(project)


async def create_project_service(
    db: AsyncSession, project_data: ProjectCreate, case_study: UploadFile | None = None
) -> ProjectRead:

    existing = await get_project_by_name_db(db, project_data.project_name)
    if existing:
        raise ProjectAlreadyExistsException()

    domain = await _resolve_domain(db, project_data.projectDomainID)
    techstacks = await _resolve_techstacks(db, project_data.techstack_ids)

    stored_path = await save_case_study(case_study) if has_upload(case_study) else None

    new_project = Projects(
        project_name=project_data.project_name,
        description=project_data.description,
        links=project_data.links,
        case_study=stored_path,
        projectDomainID=domain.id,
        techstacks=techstacks,
        is_draft=project_data.is_draft
    )

    try:
        saved_project = await add_project_db(db, new_project)
    except Exception:
        # a failed insert must not leave the uploaded document orphaned on disk
        delete_case_study(stored_path)
        raise

    return ProjectRead.model_validate(saved_project)


async def update_project_service(
    db: AsyncSession,
    project_id: int,
    project_data: ProjectUpdate,
    case_study: UploadFile | None = None,
    remove_case_study: bool = False,
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

    if payload.get("is_draft") is not None:
        update_data["is_draft"] = payload["is_draft"]

    if payload.get("links") is not None:
        # the whole map is replaced, not merged — send every link you want to keep
        update_data["links"] = payload["links"]

    if payload.get("projectDomainID") is not None:
        domain = await _resolve_domain(db, payload["projectDomainID"])
        update_data["projectDomainID"] = domain.id

    if payload.get("techstack_ids") is not None:
        update_data["techstacks"] = await _resolve_techstacks(db, payload["techstack_ids"])

    previous_path = project.case_study
    new_path = None

    if has_upload(case_study):
        new_path = await save_case_study(case_study)
        update_data["case_study"] = new_path
    elif remove_case_study:
        update_data["case_study"] = None

    try:
        updated_project = await update_project_db(db, project, update_data)
    except Exception:
        delete_case_study(new_path)
        raise

    # the old document is only removed once the row has stopped pointing at it
    if "case_study" in update_data and previous_path != update_data["case_study"]:
        delete_case_study(previous_path)

    return ProjectRead.model_validate(updated_project)


async def delete_project_service(db: AsyncSession, project_id: int) -> BaseResponse:

    project = await get_project_by_id_db(db, project_id)
    if not project:
        raise ProjectNotFoundException()

    stored_path = project.case_study

    await delete_project_db(db, project)
    delete_case_study(stored_path)

    return BaseResponse(message="Project deleted successfully")


async def get_project_case_study_service(db: AsyncSession, project_id: int) -> Path:

    project = await get_project_by_id_db(db, project_id)
    if not project:
        raise ProjectNotFoundException()

    document = resolve_case_study(project.case_study)
    if document is None:
        raise CaseStudyNotFoundException()

    return document

async def get_project_filters(db: AsyncSession):
    try:
        all_domains = await get_all_project_domain_db(db)
        all_techstack = await get_all_techstacks_db(db)
        
        response = {
            "Domains": [],
            "Techstack": [],
            "message": "Project filters fetched successfully"
        }
        for domain in all_domains:
            response["Domains"].append(domain.domain)
        for techstack in all_techstack:
            response["Techstack"].append(techstack.techstack_name)
        return response
    except:
        raise CantFetchFilterException()