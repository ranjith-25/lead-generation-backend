from pathlib import Path
from uuid import UUID
import json 
import logging

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.types import (
    ProjectHelpers
)
from app.exceptions.ai_exception import handle_ai_exception
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
from app.core.connections.ai_connection import get_ai_client
from app.services.db.project_domains import (
    get_project_domain_by_id,
    get_all_project_domain_db
)

from app.services.db.techstack import (
    get_techstacks_by_ids_db,
    get_all_techstacks_db
)


async def _resolve_domain(db: AsyncSession, project_domain_id: UUID):
    domain = await get_project_domain_by_id(db, project_domain_id)
    if not domain:
        raise ProjectDomainNotFoundException(project_domain_id)
    return domain


async def _resolve_techstacks(db: AsyncSession, techstack_ids: list[UUID]):
    techstacks = await get_techstacks_by_ids_db(db, techstack_ids)
    missing = set(techstack_ids) - {techstack.techstack_id for techstack in techstacks}
    if missing:
        raise TechStackNotFoundException(sorted(missing))
    return techstacks

async def ingest_project_to_ai(project) -> dict | None:
    AI_PROJECT_INGEST_URL = "/api/v1/projects/ingest"
    
    document: Path | None = resolve_case_study(project.case_study)
    if document is None:
        return None
    projectData = ProjectRead.model_validate(project).model_dump()
    payload = {
        "project_id": str(projectData["project_id"]),
        "project_name": projectData["project_name"],
        "description": projectData["description"],
        "domain": projectData["projectDomain"]["domain"],
        "techstacks": [techstack["techstack_name"] for techstack in projectData["techstacks"]],
        "links": json.dumps(projectData["links"])
    }
    try:
        client = get_ai_client()
        with document.open("rb") as handle:
            response = await client.post(
                AI_PROJECT_INGEST_URL,
                data={"payload": json.dumps(payload)},
                files={
                    "case_study": (
                        document.name,
                        handle,
                        ProjectHelpers.content_type_for(document),
                    )
                },
            )
        response.raise_for_status()
        return response.json()
    except Exception as exc:
        logging.exception("Could not ingest project %s into the AI service", project.project_id)
        raise handle_ai_exception(exc) from exc

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


async def get_project_service(db: AsyncSession, project_id: UUID) -> ProjectRead:

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
        delete_case_study(stored_path)
        raise

    await ingest_project_to_ai(saved_project)
    return ProjectRead.model_validate(saved_project)


async def update_project_service(
    db: AsyncSession,
    project_id: UUID,
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


async def delete_project_service(db: AsyncSession, project_id: UUID) -> BaseResponse:

    project = await get_project_by_id_db(db, project_id)
    if not project:
        raise ProjectNotFoundException()

    stored_path = project.case_study

    await delete_project_db(db, project)
    delete_case_study(stored_path)

    return BaseResponse(message="Project deleted successfully")


async def get_project_case_study_service(db: AsyncSession, project_id: UUID) -> Path:

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