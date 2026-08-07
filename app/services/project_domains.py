from app.services.db.project_domains import (
    get_all_project_domain_db,
    get_project_domain_by_id,
    create_project_domain,
    update_project_domain,
    delete_project_domain
)
from app.responses.project_domains import (
    GetProjectDomainResponse,
    CreateProjectDomainResponse,
    UpdateProjectDomainResponse,
    DeleteProjectDomainResponse
)
from app.schemas.project_domains import (
    ProjectDomainCreate,
    ProjectDomainUpdate,
    ProjectDomainDTO
)
from app.services.db.project import (
    count_projects_db
)
from app.schemas.project import ProjectFilters
from app.schemas.project_domains import ProjectDomainFilters
from app.models.project_domains import ProjectDomain
from app.models.user import User
from app.exceptions.custom import NotFoundException
import logging
from sqlalchemy.ext.asyncio import AsyncSession

async def handle_get_project_domains(db:AsyncSession, current_user : User, page: int, limit: int) -> GetProjectDomainResponse:
    try:
        projectDomains = await get_all_project_domain_db(db, ProjectDomainFilters(page=page, limit=limit))

        if projectDomains is None:
            raise NotFoundException()

        for projectDomain in projectDomains:
            filters = ProjectFilters(
                project_domains = [projectDomain.domain]
            )
            projectDomain.count = await count_projects_db(db, filters)
            
        projectDomainsResponse = GetProjectDomainResponse(
            projectDomainList= [ProjectDomainDTO.model_validate(projectDomain) for projectDomain in projectDomains] ,
            message="Project Domains fetched successfully",
            status_code=200
        )
        return projectDomainsResponse
    
    except NotFoundException as e:
        logging.exception("Couldnot find Project domains")
        raise e

    except Exception as e:
        logging.exception("Some error occoured while getting Project domains list")
        raise e 

async def handle_get_project_domain_by_id(db:AsyncSession,current_user : User,projectDomainID: int) -> GetProjectDomainResponse:
    try:
        projectDomainDetails = await get_project_domain_by_id(db,projectDomainID)

        if projectDomainDetails is None:
            raise NotFoundException()

        projectDomainDetailsResponse = GetProjectDomainResponse(
            projectDomain=projectDomainDetails,
            message="Project Domain fetched successfully",
            status_code=200
        )

        return projectDomainDetailsResponse
    
    except NotFoundException as e:
        logging.exception("Couldnot find Project domains")
        raise e

    except Exception as e:
        logging.exception("Some error occoured while getting Project domains list")
        raise e 

async def handle_create_project_domain(db:AsyncSession,current_user : User,projectDomainCreate : ProjectDomainCreate) -> CreateProjectDomainResponse:
    try:

        newProjectDomain = ProjectDomain(**projectDomainCreate.model_dump(),
        createdBy = current_user.user_id,updatedBy = current_user.user_id)
        projectDomain = await create_project_domain(db,newProjectDomain)
        projectDomainResponse = CreateProjectDomainResponse(
            newProjectDomain=projectDomain,
            message="Project Domain created successfully"
        )

        return projectDomainResponse
    
    except Exception as e:
        logging.exception("Some error occoured while creating Project domain")
        raise e 

async def handle_update_project_domain(db:AsyncSession,current_user : User,projectDomainUpdate : ProjectDomainUpdate,domainID : int) -> UpdateProjectDomainResponse:
    try:

        updatedProjectDomain = projectDomainUpdate.model_dump(exclude_unset=True,exclude_none= True)
        updatedProjectDomain["updatedBy"] = current_user.user_id
        updatedProjectDomain = await update_project_domain(db,updatedProjectDomain,domainID)
        projectDomainResponse = UpdateProjectDomainResponse(
            updatedProjectDomain=updatedProjectDomain,
            message="Project Domain updated successfully"
        )

        return projectDomainResponse
    except Exception as e:
        logging.exception("Some error occoured while updating Project domain")
        raise e 

async def handle_delete_project_domain(db:AsyncSession,current_user : User,projectDomainID: int) -> DeleteProjectDomainResponse:
    try:
        projectDomainDetails = await delete_project_domain(db,projectDomainID)

        if projectDomainDetails is None:
            raise NotFoundException()

        projectDomainDetailsResponse = DeleteProjectDomainResponse(
            message="Project Domain deleted successfully"
        )
        return projectDomainDetailsResponse
    
    except NotFoundException as e:
        logging.exception("Couldnot find Project domains")
        raise e

    except Exception as e:
        logging.exception("Some error occoured while deleting Project domains")
        raise e 