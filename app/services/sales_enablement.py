from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.sales_enablement import (
    SalesEnablementRead,
    SalesEnablementCreate,
    SalesEnablementUpdate,
    OutreachTemplateUpdate,
)
from app.responses.base import BaseResponse
from app.models.sales_enablement import SalesEnablement
from app.exceptions.opportunity import InvalidOpportunityIdException, OpportunityNotFoundException
from app.exceptions.sales_enablement import InvalidSalesEnablementIdException, SalesEnablementNotFoundException, SalesEnablementAlreadyExistsException
from app.services.db.opportunity import get_opportunity_by_id
from app.services.db.sales_enablement import get_sales_enablement_by_id_db, get_sales_enablement_by_opp_db, add_sales_enablement_db, update_sales_enablement_db, delete_sales_enablement_db
from app.config import LogAction
from app.services.system_log import log_activity

async def check_opportunity_access(db: AsyncSession, opportunity_id: UUID, user_id: UUID) -> None:

    opportunity = await get_opportunity_by_id(db, opportunity_id, user_id)
    if not opportunity:
        raise OpportunityNotFoundException(opportunity_id)

async def get_sales_enablement_service(db: AsyncSession, se_id: UUID | str, user_id: UUID) -> SalesEnablementRead:

    try:
        parsed_id = UUID(str(se_id))
    except (ValueError, TypeError):
        raise InvalidSalesEnablementIdException(se_id)

    se = await get_sales_enablement_by_id_db(db, parsed_id)
    if not se:
        raise SalesEnablementNotFoundException(parsed_id)

    await check_opportunity_access(db, se.opportunityID, user_id)

    return SalesEnablementRead.model_validate(se)

async def get_sales_enablement_by_opp_service(db: AsyncSession, opp_id: UUID | str, user_id: UUID) -> SalesEnablementRead:

    try:
        parsed_opp_id = UUID(str(opp_id))
    except (ValueError, TypeError):
        raise InvalidOpportunityIdException(opp_id)

    await check_opportunity_access(db, parsed_opp_id, user_id)

    se = await get_sales_enablement_by_opp_db(db, parsed_opp_id)
    if not se:
        # No id to report - the exception details key is the sales-enablement id, not the
        # opportunity id we looked it up by.
        raise SalesEnablementNotFoundException()

    return SalesEnablementRead.model_validate(se)

async def create_sales_enablement_service(db: AsyncSession, se_data: SalesEnablementCreate, user_id: UUID) -> SalesEnablementRead:

    await check_opportunity_access(db, se_data.opportunityID, user_id)

    existing = await get_sales_enablement_by_opp_db(db, se_data.opportunityID)
    if existing:
        raise SalesEnablementAlreadyExistsException(se_data.opportunityID)

    se_dict = se_data.model_dump()
    se_dict['createdBy'] = user_id
    se_dict['updatedBy'] = user_id
    new_se = SalesEnablement(**se_dict)

    await log_activity(
        db,
        LogAction.SALES_ENABLEMENT_CREATED,
        user_id,
        entity_type="sales_enablement",
        details={"opportunityID": se_data.opportunityID},
    )

    saved_se = await add_sales_enablement_db(db, new_se)
    return SalesEnablementRead.model_validate(saved_se)

async def update_sales_enablement_service(db: AsyncSession, se_id: UUID | str, se_data: SalesEnablementUpdate, user_id: UUID) -> SalesEnablementRead:

    try:
        parsed_id = UUID(str(se_id))
    except (ValueError, TypeError):
        raise InvalidSalesEnablementIdException(se_id)

    se = await get_sales_enablement_by_id_db(db, parsed_id)
    if not se:
        raise SalesEnablementNotFoundException(parsed_id)

    await check_opportunity_access(db, se.opportunityID, user_id)

    update_dict = se_data.model_dump(exclude_unset=True)
    update_dict['updatedBy'] = user_id

    await log_activity(
        db,
        LogAction.SALES_ENABLEMENT_UPDATED,
        user_id,
        entity_type="sales_enablement",
        entity_id=se.id,
        details={
            "opportunityID": se.opportunityID,
            "updatedFields": sorted(update_dict.keys()),
        },
    )

    updated_se = await update_sales_enablement_db(db, se, update_dict)
    return SalesEnablementRead.model_validate(updated_se)

async def update_sales_enablement_by_opportunity_service(
    db: AsyncSession,
    opp_id: UUID | str,
    se_data: SalesEnablementUpdate | OutreachTemplateUpdate,
    user_id: UUID,
) -> SalesEnablementRead:
    """Edit sales enablement addressed by opportunity, so the client needs no prior GET.

    Either payload schema is accepted — both are dumped with `exclude_unset=True` and their
    fields are all columns, so the outreach-template endpoint reuses this one write path
    instead of opening a second.
    """

    try:
        parsed_opp_id = UUID(str(opp_id))
    except (ValueError, TypeError):
        raise InvalidOpportunityIdException(opp_id)

    # Ownership boundary - must run before any read or write on the row.
    await check_opportunity_access(db, parsed_opp_id, user_id)

    update_dict = se_data.model_dump(exclude_unset=True)
    details = {
        "opportunityID": parsed_opp_id,
        "updatedFields": sorted(update_dict.keys()),
    }

    se = await get_sales_enablement_by_opp_db(db, parsed_opp_id)

    if not se:
        # Upsert: an opportunity added by hand never went through AI ingest, so it has no row to
        # edit - a 404 on a screen that plainly offers editing would be the wrong answer.
        new_se = SalesEnablement(
            opportunityID=parsed_opp_id,
            createdBy=user_id,
            updatedBy=user_id,
            **update_dict,
        )

        await log_activity(
            db,
            LogAction.SALES_ENABLEMENT_CREATED,
            user_id,
            entity_type="sales_enablement",
            details=details,
        )

        saved_se = await add_sales_enablement_db(db, new_se)
        return SalesEnablementRead.model_validate(saved_se)

    update_dict['updatedBy'] = user_id

    await log_activity(
        db,
        LogAction.SALES_ENABLEMENT_UPDATED,
        user_id,
        entity_type="sales_enablement",
        entity_id=se.id,
        details=details,
    )

    updated_se = await update_sales_enablement_db(db, se, update_dict)
    return SalesEnablementRead.model_validate(updated_se)

async def update_outreach_template_service(db: AsyncSession, opp_id: UUID | str, template_data: OutreachTemplateUpdate, user_id: UUID) -> SalesEnablementRead:
    return await update_sales_enablement_by_opportunity_service(db, opp_id, template_data, user_id)

async def delete_sales_enablement_service(db: AsyncSession, se_id: UUID | str, user_id: UUID) -> BaseResponse:

    try:
        parsed_id = UUID(str(se_id))
    except (ValueError, TypeError):
        raise InvalidSalesEnablementIdException(se_id)

    se = await get_sales_enablement_by_id_db(db, parsed_id)
    if not se:
        raise SalesEnablementNotFoundException(parsed_id)

    await check_opportunity_access(db, se.opportunityID, user_id)

    await log_activity(
        db,
        LogAction.SALES_ENABLEMENT_DELETED,
        user_id,
        entity_type="sales_enablement",
        entity_id=se.id,
        details={"opportunityID": se.opportunityID},
    )

    await delete_sales_enablement_db(db, se)
    return BaseResponse(success=True, message="Sales Enablement deleted successfully")
