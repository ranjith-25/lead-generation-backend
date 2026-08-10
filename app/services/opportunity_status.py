import logging
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.exceptions.custom import NotFoundException
from app.models.opportunity_status import OpportunityStatus
from app.models.user import User
from app.responses.opportunity_status import (
    CreateOpportunityStatusResponse,
    DeleteOpportunityStatusResponse,
    GetOpportunityStatusResponse,
    UpdateOpportunityStatusResponse,
)
from app.schemas.opportunity_status import OpportunityStatusCreate, OpportunityStatusDTO, OpportunityStatusUpdate, OpportunityStatusListRead
from app.services.db.opportunity_status import (
    create_opportunity_status,
    delete_opportunity_status,
    get_all_opportunity_statuses,
    get_opportunity_status_by_id,
    update_opportunity_status,
    fetch_new_opportunity_status_id,
)


async def handle_get_all_opportunity_statuses(db: AsyncSession, current_user: User, search: str | None = None, page: int = 1, limit: int = 10) -> GetOpportunityStatusResponse:
    try:
        opportunity_statuses, total = await get_all_opportunity_statuses(db, search, page, limit)

        return GetOpportunityStatusResponse(
            opportunityStatusList=[OpportunityStatusListRead.model_validate(status) for status in opportunity_statuses],
            total=total,
            page=page,
            limit=limit,
            total_pages=(total + limit - 1) // limit if total > 0 else 1,
            message="Opportunity Statuses fetched successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find Opportunity Statuses")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while getting Opportunity Statuses list")
        raise e


async def handle_get_opportunity_status_by_id(db: AsyncSession, current_user: User, opportunity_status_id: UUID) -> GetOpportunityStatusResponse:
    try:
        opportunity_status = await get_opportunity_status_by_id(db, opportunity_status_id)
        if opportunity_status is None:
            raise NotFoundException()

        return GetOpportunityStatusResponse(
            opportunityStatus=OpportunityStatusDTO.model_validate(opportunity_status),
            message="Opportunity Status fetched successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find Opportunity Status")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while getting Opportunity Status details")
        raise e


async def handle_create_opportunity_status(
    db: AsyncSession, current_user: User, opportunity_status_create: OpportunityStatusCreate
) -> CreateOpportunityStatusResponse:
    try:
        new_opportunity_status = OpportunityStatus(**opportunity_status_create.model_dump())
        created_opportunity_status = await create_opportunity_status(db, new_opportunity_status)
        return CreateOpportunityStatusResponse(
            newOpportunityStatus=OpportunityStatusDTO.model_validate(created_opportunity_status),
            message="Opportunity Status created successfully",
            status_code=200,
        )
    except Exception as e:
        logging.exception("Some error occurred while creating Opportunity Status")
        raise e


async def handle_update_opportunity_status(
    db: AsyncSession, current_user: User, opportunity_status_update: OpportunityStatusUpdate, opportunity_status_id: UUID
) -> UpdateOpportunityStatusResponse:
    try:
        update_data = opportunity_status_update.model_dump(exclude_unset=True, exclude_none=True)
        updated_opportunity_status = await update_opportunity_status(db, update_data, opportunity_status_id)
        if updated_opportunity_status is None:
            raise NotFoundException()

        return UpdateOpportunityStatusResponse(
            updatedOpportunityStatus=OpportunityStatusDTO.model_validate(updated_opportunity_status),
            message="Opportunity Status updated successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find Opportunity Status")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while updating Opportunity Status")
        raise e


async def handle_delete_opportunity_status(
    db: AsyncSession, current_user: User, opportunity_status_id: UUID
) -> DeleteOpportunityStatusResponse:
    try:
        deleted_opportunity_status = await delete_opportunity_status(db, opportunity_status_id)
        if deleted_opportunity_status is None:
            raise NotFoundException()

        return DeleteOpportunityStatusResponse(
            message="Opportunity Status deleted successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find Opportunity Status")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while deleting Opportunity Status")
        raise e


async def get_new_opportunity_status_id(db: AsyncSession):
    try:
        status_id = await fetch_new_opportunity_status_id(db)
        if status_id:
            return status_id
        else:
            raise NotFoundException("Could not find Opportunity Status")
    except NotFoundException as e:
        logging.exception("Could not find Opportunity Status")
        raise e
    except Exception as e:
        logging.exception("Could not find Opportunity Status")
        raise e
