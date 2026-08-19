import io
from uuid import UUID
import json 
import logging

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.responses.base import BaseResponse
from app.models.projects import Projects
from app.core import settings

import uuid
from pathlib import Path

from app.services.types import (
    ProjectHelpers
)
from app.exceptions.ai_exception import AIException, handle_ai_exception
from app.core.storage import (
    has_upload,
    ALLOWED_CASE_STUDY_EXTENSIONS,
    SizeLimitingReader,
)
from app.services.s3_crud import (
    upload_fileobj,
    download_bytes,
    delete_file,
    file_exists,
    stream_file,
)
from app.exceptions.project import (
    CaseStudyNotFoundException,
    ProjectAlreadyExistsException,
    ProjectDomainNotFoundException,
    ProjectNotFoundException,
    TechStackNotFoundException,
    CantFetchFilterException,
    CaseStudyTooLargeException,
    CaseStudyEmptyException,
    CaseStudyUnsupportedTypeException,
)

from app.exceptions.s3_exceptions import S3UploadException, S3DeleteException
from app.responses.project import CreateProjectResponse, ProjectListResponse, FileDownloadResponse
from app.responses.base import BaseResponse
from app.schemas.common import get_time_filter_options
from app.schemas.project import (
    ProjectCreate,
    ProjectRead,
    ProjectUpdate,
    ProjectFilters
)
from app.services.db.project import (
    add_project_db,
    delete_project_db,
    get_all_projects_db,
    get_project_by_id_db,
    get_project_by_name_db,
    update_project_db,
)
from app.services.db.user_project import get_user_ids_by_project
# Module-level import is safe: app/services/user_project.py imports nothing from this module,
# so there is no cycle to break with a function-local import.
from app.services.user_project import sync_bench_status
from app.core.connections.ai_connection import get_ai_client
from app.services.db.project_domains import (
    get_project_domain_by_id,
    get_all_project_domain_db
)

from app.services.db.techstack import (
    get_techstacks_by_ids_db,
    get_all_techstacks_db
)
from app.schemas.techstack import TechstackFilters
from app.schemas.project_domains import ProjectDomainFilters 
from app.exceptions.custom import AppException
from app.config import LogAction
from app.services.system_log import log_activity

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
    
    if not project.case_study:
        return None

    # Download the file bytes from S3 directly to memory to avoid local disk usage
    try:
        file_bytes = await download_bytes(project.case_study)
    except Exception as exc:
        logging.warning("Could not download case study from S3 for AI ingestion: %s", project.case_study)
        return None

    projectData = ProjectRead.model_validate(project).model_dump()
    payload = {
        "project_id": str(projectData["project_id"]),
        "project_name": projectData["project_name"],
        "description": projectData["description"],
        "domain": projectData["projectDomain"]["domain"],
        "techstacks": [techstack["techstack_name"] for techstack in projectData["techstacks"]],
        "links": projectData["links"]
    }
    
    # Get the basename after the folder prefix from the S3 key
    filename = project.case_study.split("/")[-1]
    
    try:
        client = get_ai_client()
        # Uploading the S3 bytes as a file-like BytesIO stream to the AI service
        response = await client.post(
            AI_PROJECT_INGEST_URL,
            data={"payload": json.dumps(payload)},
            files={
                "case_study": (
                    filename,
                    io.BytesIO(file_bytes),
                    ProjectHelpers.content_type_for(filename),
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
    db: AsyncSession,
    project_data: ProjectCreate,
    user_id: UUID,
    case_study: UploadFile | None = None,
) -> CreateProjectResponse:

    existing = await get_project_by_name_db(db, project_data.project_name)
    if existing:
        raise ProjectAlreadyExistsException()

    domain = await _resolve_domain(db, project_data.projectDomainID)
    techstacks = await _resolve_techstacks(db, project_data.techstack_ids)

    project_id = uuid.uuid4()
    stored_path = None

    if has_upload(case_study):
        filename = case_study.filename or ""
        extension = Path(filename).suffix.lower()
        if extension not in ALLOWED_CASE_STUDY_EXTENSIONS:
            raise CaseStudyUnsupportedTypeException(sorted(ALLOWED_CASE_STUDY_EXTENSIONS))

        stored_path = f"case_studies/{project_id}{extension}"
        max_bytes = settings.MAX_CASE_STUDY_SIZE_MB * 1024 * 1024
        
        await case_study.seek(0)
        reader = SizeLimitingReader(case_study.file, max_bytes, settings.MAX_CASE_STUDY_SIZE_MB)
        try:
            # Upload the file directly to S3 using the existing file object.
            # This avoids creating a temporary local copy and prevents unnecessary
            # disk usage on the application server.
            await upload_fileobj(
                reader,
                stored_path,
                content_type=case_study.content_type or ProjectHelpers.content_type_for(filename),
            )
            if reader.bytes_read == 0:
                raise CaseStudyEmptyException()

        except S3UploadException as exc:
            raise exc
        
        except Exception as exc:
            # Delete S3 object if upload fails/is empty/too large to avoid orphaned files
            try:
                await delete_file(stored_path)

            except S3DeleteException as exc:
                raise exc

            except Exception as exc:
                raise exc
            raise exc

    new_project = Projects(
        project_id=project_id,
        project_name=project_data.project_name,
        description=project_data.description,
        links=project_data.links,
        case_study=stored_path,
        projectDomainID=domain.id,
        techstacks=techstacks,
        is_draft=project_data.is_draft
    )

    await log_activity(
        db,
        LogAction.PROJECT_CREATED,
        user_id,
        entity_type="project",
        entity_id=project_id,
        entity_name=project_data.project_name,
        details={
            "projectDomainID": domain.id,
            "techstack_ids": project_data.techstack_ids,
            "case_study": stored_path,
            "is_draft": project_data.is_draft,
        },
    )

    try:
        saved_project = await add_project_db(db, new_project)
    except Exception as exc:
        # If database creation fails after the S3 upload succeeds, remove the
        # S3 object to prevent orphaned files.
        if stored_path:
            try:
                await  delete_file(stored_path)

            except S3DeleteException as exc:
                raise exc

            except Exception as exc:
                raise exc
        raise exc

    try:
        await ingest_project_to_ai(saved_project)
    except AIException as exc:
        logging.exception(
            "Project %s was created but could not be ingested into the AI service",
            saved_project.project_id,
        )
        return CreateProjectResponse(
            message="Project created, but AI ingestion failed",
            project=ProjectRead.model_validate(saved_project),
            ai_ingest_failed=True,
            ai_error=exc.message,
        )

    return CreateProjectResponse(
        message="Project created successfully",
        project=ProjectRead.model_validate(saved_project),
    )


async def update_project_service(
    db: AsyncSession,
    project_id: UUID,
    project_data: ProjectUpdate,
    case_study: UploadFile | None = None,
    remove_case_study: bool = False,
    user_id: UUID | None = None,
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
        filename = case_study.filename or ""
        extension = Path(filename).suffix.lower()
        if extension not in ALLOWED_CASE_STUDY_EXTENSIONS:
            raise CaseStudyUnsupportedTypeException(sorted(ALLOWED_CASE_STUDY_EXTENSIONS))

        new_path = f"case_studies/{project_id}{extension}"
        max_bytes = settings.MAX_CASE_STUDY_SIZE_MB * 1024 * 1024
        
        await case_study.seek(0)
        reader = SizeLimitingReader(case_study.file, max_bytes, settings.MAX_CASE_STUDY_SIZE_MB)
        try:
            # Upload the file directly to S3 using the existing file object.
            # This avoids creating a temporary local copy and prevents unnecessary
            # disk usage on the application server.
            await upload_fileobj(
                reader,
                new_path,
                content_type=case_study.content_type or ProjectHelpers.content_type_for(filename),
            )
            if reader.bytes_read == 0:
                raise CaseStudyEmptyException()
        except Exception as exc:
            # Delete S3 object if upload fails/is empty/too large to avoid orphaned files
            try:
                await delete_file(new_path)
            except Exception:
                pass
            raise exc
        update_data["case_study"] = new_path
    elif remove_case_study:
        update_data["case_study"] = None

    await log_activity(
        db,
        LogAction.PROJECT_UPDATED,
        user_id,
        entity_type="project",
        entity_id=project_id,
        entity_name=project.project_name,
        details={"updated_fields": sorted(update_data.keys())},
    )

    try:
        updated_project = await update_project_db(db, project, update_data)
    except Exception as exc:
        if new_path:
            try:
                await delete_file(new_path)
            except Exception:
                pass
        raise exc

    # the old document is only removed once the row has stopped pointing at it
    if "case_study" in update_data and previous_path != update_data["case_study"] and previous_path:
        try:
            await delete_file(previous_path)
        except Exception:
            logging.warning("Could not delete old S3 case study: %s", previous_path)

    return ProjectRead.model_validate(updated_project)


async def delete_project_service(
    db: AsyncSession, project_id: UUID, user_id: UUID | None = None
) -> BaseResponse:

    project = await get_project_by_id_db(db, project_id)
    if not project:
        raise ProjectNotFoundException()

    # entity details are read off the row before it is deleted
    stored_path = project.case_study
    project_name = project.project_name

    # user_projects.project_id is ondelete="CASCADE", so these allocations disappear with the
    # project — collect their users now or they cannot be found afterwards.
    allocated_user_ids = await get_user_ids_by_project(db, project_id)

    await delete_project_db(db, project)

    # Benching is reported, never blocking: the project is already gone, and an org that never
    # seeded an "On Bench" status should not see the delete fail because of it.
    benched_count = 0
    try:
        benched_count = await sync_bench_status(db, allocated_user_ids, user_id)
    except Exception:
        logging.exception(
            "Could not sync bench status for the %s user(s) freed by deleting project %s",
            len(allocated_user_ids),
            project_id,
        )

    # Logged after the delete because the benched count only exists once the allocations are
    # gone; the entity name and case-study path were captured off the row beforehand.
    await log_activity(
        db,
        LogAction.PROJECT_DELETED,
        user_id,
        entity_type="project",
        entity_id=project_id,
        entity_name=project_name,
        details={
            "case_study": stored_path,
            "allocated_users_released": len(allocated_user_ids),
            "users_moved_to_bench": benched_count,
        },
        commit=True,
    )

    if stored_path:
        # Delete the case study object from S3 after deleting the project record
        try:
            await delete_file(stored_path)
        except Exception:
            logging.warning("Could not delete S3 case study on project deletion: %s", stored_path)

    message = "Project deleted successfully"
    if benched_count:
        message = (
            f"{message}. {benched_count} user(s) moved to bench with no remaining allocations"
        )

    return BaseResponse(message=message)


async def get_project_case_study_service(db: AsyncSession, project_id: UUID) -> str:
    """
    Get the S3 object key for a project's case study.
    Raises ProjectNotFoundException if the project doesn't exist,
    and CaseStudyNotFoundException if the project has no case study or if it doesn't exist on S3.
    """
    project = await get_project_by_id_db(db, project_id)
    if not project:
        raise ProjectNotFoundException()

    object_key = project.case_study
    if not object_key or not await file_exists(object_key):
        raise CaseStudyNotFoundException()

    return object_key

async def get_project_filters(db: AsyncSession):
    try:
        all_domains = await get_all_project_domain_db(db, ProjectDomainFilters(page=1, limit=None))
        all_techstack = await get_all_techstacks_db(db, TechstackFilters(page=1, limit=None))
        
        response = {
            "Domains": [],
            "Techstack": [],
            "time_filter": get_time_filter_options(),
            "message": "Project filters fetched successfully"
        }
        for domain in all_domains:
            response["Domains"].append(domain.domain)
        for techstack in all_techstack:
            response["Techstack"].append(techstack.techstack_name)
        return response
    except Exception as exc:
        logging.exception("Could not fetch project filter options")
        raise CantFetchFilterException() from exc

async def download_case_study_service(
    db: AsyncSession,
    project_id: UUID,
    user_id: UUID | None = None,
) -> FileDownloadResponse:
    """
    Prepare the case study file for download.

    Steps:
    1. Retrieve the S3 object key for the project case study.
    2. Create an asynchronous S3 file stream.
    3. Prepare the file metadata required by the API layer.

    The complete file is NOT loaded into backend memory.
    The file is streamed from S3 in chunks.
    """

    # Get the S3 object key stored for this project.
    object_key = await get_project_case_study_service(
        db,
        project_id,
    )

    # Extract the original filename from the S3 object key.
    file_name = object_key.split("/")[-1]

    # Create the asynchronous S3 stream.
    file_stream = stream_file(object_key)

    # read-only request: no business write to ride along on, so the row commits itself
    await log_activity(
        db,
        LogAction.CASE_STUDY_DOWNLOADED,
        user_id,
        entity_type="project",
        entity_id=project_id,
        entity_name=file_name,
        details={"file_name": file_name, "object_key": object_key},
        commit=True,
    )

    return FileDownloadResponse(
        file_stream=file_stream,
        file_name=file_name,
        content_type="application/octet-stream",
    )