from datetime import datetime
import logging
from typing import Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import LogAction, NotificationEvent
from app.exceptions.custom import AppException, NotFoundException
from app.exceptions.pipeline_opportunity_resource import InvalidResourceAssignmentException
from app.exceptions.error_codes import ErrorCode
from app.models.pipeline_opportunity_resource import PipelineOpportunityResourceModel
from app.models.user import User
from app.responses.pipeline_opportunity_resource import (
    AssignPipelineOpportunityResourcesResponse,
    CreatePipelineOpportunityResourceResponse,
    DeletePipelineOpportunityResourceResponse,
    GetPipelineOpportunityResourceResponse,
    UpdatePipelineOpportunityResourceResponse,
    SelectPipelineOpportunityResourcesResponse
)
from app.schemas.pipeline_opportunity_resource import (
    ApprovalStatus,
    PipelineOpportunityResourceCreate,
    PipelineOpportunityResourceDTO,
    PipelineOpportunityResourceUpdate,
    PipelineOpportunityResourceStatusUpdate,
    PipelineOpportunityResourceSelectRequest,
    PipelineOpportunityResourceAssignToTLRequest,
    PipelineOpportunityResourceApproveRequest,
    PipelineOpportunityResourceAutoApproveRequest,
    PipelineOpportunityResourceRejectRequest,
)
from app.services.db.pipeline_opportunity_resource import (
    create_pipeline_opportunity_resource,
    delete_pipeline_opportunity_resource,
    get_all_pipeline_opportunity_resources,
    get_approved_pipeline_opportunity_resource_by_opportunity_id,
    get_pipeline_opportunity_resource_by_id,
    update_pipeline_opportunity_resource,
    get_pipeline_opportunity_resource_by_opportunity_id,
    update_multiple_pipeline_opportunity_resource,
    get_multiple_pipeline_opportunity_resource_by_id
)
from app.schemas.ai import AITechnicalPreperationRequest
from app.services.db.opportunity import get_opportunity_details_by_id
from app.services.db.user import get_user_by_id
from app.services.notification_dispatcher import (
    NotificationEventContext,
    dispatch_notification_event,
    notify_users,
)
from app.services.system_log import log_activity
from app.models.opportunity import Opportunity
import json
from app.schemas.opportunity import OpportunityRead
from app.services.ai import handleTechnicalPreperation
from app.schemas.notification import NotificationType
from fastapi import BackgroundTasks
from sqlalchemy.exc import IntegrityError
from app.core.security import hasPermissions

async def _apply_pipeline_opportunity_resource_status(
    db: AsyncSession,
    current_user: User,
    pipeline_opportunity_resource_id: UUID,
    status_data: PipelineOpportunityResourceStatusUpdate,
    message: str,
) -> UpdatePipelineOpportunityResourceResponse:
    """Persist a dedicated status transition (assign / approve / reject).

    Status changes deliberately bypass PipelineOpportunityResourceUpdate so that the
    generic update endpoint cannot move a resource through the workflow arbitrarily.
    """
    status_data.updatedBy = current_user.user_id
    updated_pipeline_opportunity_resource = await update_pipeline_opportunity_resource(
        db,
        status_data.model_dump(exclude_unset=True),
        pipeline_opportunity_resource_id,
    )
    if updated_pipeline_opportunity_resource is None:
        raise NotFoundException()

    return UpdatePipelineOpportunityResourceResponse(
        updatedPipelineOpportunityResource=PipelineOpportunityResourceDTO.model_validate(
            updated_pipeline_opportunity_resource
        ),
        message=message,
        status_code=200,
    )


async def _apply_pipeline_opportunity_resource_status_list(
    db: AsyncSession,
    current_user: User,
    pipeline_opportunity_resource_id_list: list[UUID],
    status_data: PipelineOpportunityResourceStatusUpdate,
) -> list[PipelineOpportunityResourceDTO]:
    """The same transition applied to a batch, for /select and /assign.

    Returns the updated rows rather than a response — the two routes name their payload
    differently, so the envelope belongs to the handler.
    """
    status_data.updatedBy = current_user.user_id
    updated_pipeline_opportunity_resources = await update_multiple_pipeline_opportunity_resource(
        db = db,
        update_data= status_data,
        pipeline_opportunity_resource_ids= pipeline_opportunity_resource_id_list
    )
    if updated_pipeline_opportunity_resources is None:
        raise NotFoundException()

    return [
        PipelineOpportunityResourceDTO.model_validate(row)
        for row in updated_pipeline_opportunity_resources
    ]


def _resource_display_name(
    pipeline_opportunity_resource: PipelineOpportunityResourceModel,
) -> str:
    """Prefer the person's name over the variant title when naming an approved resource."""
    user_details = pipeline_opportunity_resource.user_details
    if user_details and user_details.fullName and user_details.fullName != "Unknown User":
        return user_details.fullName
    return pipeline_opportunity_resource.variant_title


async def _build_notification_context(
    db: AsyncSession,
    current_user: User,
    pipeline_opportunity_resource: PipelineOpportunityResourceModel,
    opportunity: Opportunity | None = None,
    **extra: Any,
) -> NotificationEventContext:
    """Assemble the single context an event's audiences all share.

    The dispatcher renders a different template per audience, but every one of them reads
    from this one dict: `build_notification_content` blanks out placeholders a template
    does not need, so a superset is safe and no per-audience assembly is required. Only
    the values that differ per event (who acted, why) come in through `extra`.

    `opportunity` is a parameter so the approve path can hand over the row it already
    loaded; the select and reject paths leave it None and let it be fetched here, which is
    what gives every event access to `job_title` and `company`.
    """
    if opportunity is None:
        opportunity = await get_opportunity_details_by_id(
            db, pipeline_opportunity_resource.opportunity_id
        )

    # user_details can be absent for a variant with no linked person, so the reporting
    # line is read defensively — an unresolved audience is skipped by the dispatcher.
    user_details = pipeline_opportunity_resource.user_details
    subject_reporting_to = user_details.reporting_to if user_details else None

    content = {
        "resource_name": _resource_display_name(pipeline_opportunity_resource),
        "variant_title": pipeline_opportunity_resource.variant_title,
        "job_title": opportunity.title if opportunity else "",
        "company": opportunity.company if opportunity else "",
        "opportunity_id": str(pipeline_opportunity_resource.opportunity_id),
        # Stringified like opportunity_id: the ids only ever land in url/body templates,
        # and a UUID object renders the same but is not JSON-serialisable on the push path.
        "pipeline_resource_id": str(pipeline_opportunity_resource.id),
        **extra,
    }

    return NotificationEventContext(
        actor_id=current_user.user_id,
        content=content,
        subject_id=pipeline_opportunity_resource.user_id,
        subject_reporting_to=subject_reporting_to,
        # createdBy on the opportunity is the BD who owns it — the audience that cares
        # about the outcome without being part of the reporting line.
        opportunity_owner_id=opportunity.createdBy if opportunity else None,
    )


async def _dispatch_resource_event(
    db: AsyncSession,
    event: NotificationEvent,
    current_user: User,
    pipeline_opportunity_resource: PipelineOpportunityResourceModel,
    opportunity: Opportunity | None = None,
    **extra: Any,
) -> None:
    """Build the context and dispatch, with the whole thing guarded.

    `dispatch_notification_event` swallows its own failures, but assembling the context
    can hit the database on the paths that do not already hold the opportunity. That read
    happens after the status change has committed, inside a handler whose `except` re-raises,
    so it needs the same guarantee the notification itself has: a notification problem must
    never turn a successful status change into a 500.
    """
    try:
        notification_context = await _build_notification_context(
            db,
            current_user,
            pipeline_opportunity_resource,
            opportunity=opportunity,
            **extra,
        )
        await dispatch_notification_event(db, event, notification_context)
    except Exception:
        logging.exception(
            "Could not dispatch %s for resource %s",
            event,
            pipeline_opportunity_resource.id,
        )


async def _approve_pipeline_opportunity_resource(
    db: AsyncSession,
    current_user: User,
    pipeline_opportunity_resource: PipelineOpportunityResourceModel,
    background_tasks: BackgroundTasks,
    is_auto_approved: bool,
    message: str,
) -> UpdatePipelineOpportunityResourceResponse:
    """Approve a resource and kick off its technical preparation.

    Shared by the reporting user approval and the auto approval granted to roles
    holding the pipeline_opportunity_technical_preperation auto_approve permission.
    """
    already_approved_resource = await get_approved_pipeline_opportunity_resource_by_opportunity_id(
        db, pipeline_opportunity_resource.opportunity_id
    )
    if already_approved_resource is not None:
        raise AppException(
            message="Another resource is already approved for this opportunity",
            status_code=409,
            error_code=ErrorCode.DUPLICATE_RECORD,
        )

    # One call site for both approvals — the action distinguishes the reporting-user
    # approval from the auto approval, mirroring the two notification events below.
    await log_activity(
        db,
        LogAction.PIPELINE_RESOURCE_AUTO_APPROVED
        if is_auto_approved
        else LogAction.PIPELINE_RESOURCE_APPROVED,
        current_user,
        entity_type="pipeline_resource",
        entity_id=pipeline_opportunity_resource.id,
        entity_name=_resource_display_name(pipeline_opportunity_resource),
        details={
            "opportunity_id": pipeline_opportunity_resource.opportunity_id,
            "user_id": pipeline_opportunity_resource.user_id,
            "previous_status": pipeline_opportunity_resource.status,
            "new_status": ApprovalStatus.APPROVED,
            "is_auto_approved": is_auto_approved,
        },
    )

    try:
        result: UpdatePipelineOpportunityResourceResponse = await _apply_pipeline_opportunity_resource_status(
            db=db,
            current_user=current_user,
            pipeline_opportunity_resource_id=pipeline_opportunity_resource.id,
            status_data=PipelineOpportunityResourceStatusUpdate(
                status=ApprovalStatus.APPROVED,
                is_auto_approved=is_auto_approved,
                approved_at=datetime.now(),
                approved_by=current_user.user_id,
                rejected_at=None,
                rejected_by=None,
                reject_reason=None,
            ),
            message=message,
        )
    except IntegrityError as e:
        # Loses the race against the unique partial index (one APPROVED resource per opportunity)
        logging.exception("Duplicate approval for Pipeline Opportunity Resource")
        raise AppException(
            message="Another resource is already approved for this opportunity",
            status_code=409,
            error_code=ErrorCode.DUPLICATE_RECORD,
        ) from e

    job_details: Opportunity = await get_opportunity_details_by_id(db, result.updatedPipelineOpportunityResource.opportunity_id)
    job_details_schema: OpportunityRead = OpportunityRead.model_validate(job_details)
    technicalPreperationRequest: AITechnicalPreperationRequest = AITechnicalPreperationRequest(
        user_id=current_user.user_id,
        action="Technical Preparation",
        job_details=json.dumps(job_details_schema.model_dump(mode="json")),
        variant_id=str(result.updatedPipelineOpportunityResource.variant_id),
        matching_skills=result.updatedPipelineOpportunityResource.matching_skills,
        missing_skills=result.updatedPipelineOpportunityResource.missing_skills,
    )
    background_tasks.add_task(handleTechnicalPreperation, technicalPreperationRequest, result.updatedPipelineOpportunityResource.opportunity_id)

    # Hooked here rather than in the two callers so the manual approval and the auto
    # approval both notify — `job_details` is reused instead of re-querying the opportunity.
    # A self-approval bypassed the reporting Team Lead, which changes who hears about it
    # and what they are told, so it is a separate event rather than a branch in the code —
    # the difference lives in NOTIFICATION_EVENTS.
    event = (
        NotificationEvent.RESOURCE_SELF_APPROVED
        if is_auto_approved
        else NotificationEvent.RESOURCE_APPROVED
    )
    await _dispatch_resource_event(
        db,
        event,
        current_user,
        pipeline_opportunity_resource,
        opportunity=job_details,
        approved_by_name=current_user.fullName,
        is_auto_approved=is_auto_approved,
    )

    return result


def _ensure_approval_authority(
    pipeline_opportunity_resource: PipelineOpportunityResourceModel,
    current_user: User,
    action: str,
) -> None:
    """The approver is whoever /assign recorded.

    Rows assigned before approval_authority_id was written fall back to the resource's
    reporting user, so nothing already in flight needs a backfill.
    """
    user_details = pipeline_opportunity_resource.user_details
    approval_authority_id = pipeline_opportunity_resource.approval_authority_id or (
        user_details.reporting_to if user_details else None
    )
    if approval_authority_id is None or approval_authority_id != current_user.user_id:
        raise AppException(
            message=f"Only the assigned approver can {action} this resource",
            status_code=403,
            error_code=ErrorCode.NOT_ALLOWED,
        )


def _resolve_common_reporting_user(
    pipeline_opportunity_resources: list[PipelineOpportunityResourceModel],
) -> UUID | None:
    """The one user every resource reports to, or None when they differ.

    The None-in-set check is the subtlety: a batch whose reporting_to is NULL throughout
    yields a set of one and would otherwise read as "same TL" with nobody to assign to.
    """
    reporting_to_ids = {
        resource.user_details.reporting_to if resource.user_details else None
        for resource in pipeline_opportunity_resources
    }
    if len(reporting_to_ids) == 1 and None not in reporting_to_ids:
        return next(iter(reporting_to_ids))
    return None


async def _resolve_approval_authority(db: AsyncSession, approval_authority_id: UUID) -> User:
    """Validate the approver the frontend nominated.

    The hierarchy is deliberately not walked: a selection spanning several TLs is meant
    to land on a Manager who need not be anyone's reporting user. All that is checked is
    that the nominee can actually act on the resource.
    """
    approval_authority = await get_user_by_id(db, approval_authority_id)
    if approval_authority is None or approval_authority.is_deleted:
        raise AppException(
            message="The selected approver does not exist.",
            status_code=400,
            error_code=ErrorCode.VALIDATION_ERROR,
        )

    can_approve = await hasPermissions(
        db=db,
        role_id=approval_authority.role_id,
        feature_key="pipeline_opportunity_resource",
        permission_name="approve",
    )
    can_reject = await hasPermissions(
        db=db,
        role_id=approval_authority.role_id,
        feature_key="pipeline_opportunity_resource",
        permission_name="reject",
    )
    if not can_approve and not can_reject:
        raise AppException(
            message="The selected approver doesn't have permission to approve or reject this resource.",
            status_code=400,
            error_code=ErrorCode.VALIDATION_ERROR,
        )

    return approval_authority


async def handle_get_all_pipeline_opportunity_resources(
    db: AsyncSession, current_user: User, page: int = 1, limit: int = 10
) -> GetPipelineOpportunityResourceResponse:
    try:
        pipeline_opportunity_resources, total = await get_all_pipeline_opportunity_resources(db, page, limit)

        return GetPipelineOpportunityResourceResponse(
            pipelineOpportunityResourceList=[
                PipelineOpportunityResourceDTO.model_validate(resource) for resource in pipeline_opportunity_resources
            ],
            total=total,
            page=page,
            limit=limit,
            total_pages=(total + limit - 1) // limit if total > 0 else 1,
            message="Pipeline Opportunity Resources fetched successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find Pipeline Opportunity Resources")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while getting Pipeline Opportunity Resources list")
        raise e


async def handle_get_pipeline_opportunity_resource_by_id(
    db: AsyncSession, current_user: User, pipeline_opportunity_resource_id: UUID
) -> GetPipelineOpportunityResourceResponse:
    try:
        pipeline_opportunity_resource = await get_pipeline_opportunity_resource_by_id(db, pipeline_opportunity_resource_id)
        if pipeline_opportunity_resource is None:
            raise NotFoundException()

        return GetPipelineOpportunityResourceResponse(
            pipelineOpportunityResource=PipelineOpportunityResourceDTO.model_validate(pipeline_opportunity_resource),
            message="Pipeline Opportunity Resource fetched successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find Pipeline Opportunity Resource")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while getting Pipeline Opportunity Resource details")
        raise e


async def handle_get_pipeline_opportunity_resource_by_opportunity_id(
    db: AsyncSession, current_user: User, pipeline_opportunity_id: UUID
) -> GetPipelineOpportunityResourceResponse:
    try:
        pipeline_opportunity_resources = await get_pipeline_opportunity_resource_by_opportunity_id(db, pipeline_opportunity_id)

        return GetPipelineOpportunityResourceResponse(
            pipelineOpportunityResourceList=[PipelineOpportunityResourceDTO.model_validate(resource) for resource in pipeline_opportunity_resources],
            message="Pipeline Opportunity Resource fetched successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find Pipeline Opportunity Resource")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while getting Pipeline Opportunity Resource details")
        raise e


async def handle_create_pipeline_opportunity_resource(
    db: AsyncSession, current_user: User, pipeline_opportunity_resource_create: PipelineOpportunityResourceCreate
) -> CreatePipelineOpportunityResourceResponse:
    try:
        create_data = pipeline_opportunity_resource_create.model_dump()
        create_data.pop("is_active", None)
        new_pipeline_opportunity_resource = PipelineOpportunityResourceModel(
            **create_data,
            createdBy=current_user.user_id,
            updatedBy=current_user.user_id,
        )
        await log_activity(
            db,
            LogAction.PIPELINE_RESOURCE_CREATED,
            current_user,
            entity_type="pipeline_resource",
            entity_name=new_pipeline_opportunity_resource.candidate_name
            or new_pipeline_opportunity_resource.variant_title,
            details={
                "opportunity_id": create_data.get("opportunity_id"),
                "user_id": create_data.get("user_id"),
                "variant_title": create_data.get("variant_title"),
            },
        )
        created_pipeline_opportunity_resource = await create_pipeline_opportunity_resource(db, new_pipeline_opportunity_resource)
        return CreatePipelineOpportunityResourceResponse(
            newPipelineOpportunityResource=PipelineOpportunityResourceDTO.model_validate(created_pipeline_opportunity_resource),
            message="Pipeline Opportunity Resource created successfully",
            status_code=200,
        )
    except Exception as e:
        logging.exception("Some error occurred while creating Pipeline Opportunity Resource")
        raise e


async def handle_update_pipeline_opportunity_resource(
    db: AsyncSession,
    current_user: User,
    pipeline_opportunity_resource_update: PipelineOpportunityResourceUpdate,
    pipeline_opportunity_resource_id: UUID,
) -> UpdatePipelineOpportunityResourceResponse:
    try:
        update_data = pipeline_opportunity_resource_update.model_dump(exclude_unset=True, exclude_none=True)
        update_data.pop("is_active", None)
        update_data["updatedBy"] = current_user.user_id
        await log_activity(
            db,
            LogAction.PIPELINE_RESOURCE_UPDATED,
            current_user,
            entity_type="pipeline_resource",
            entity_id=pipeline_opportunity_resource_id,
            entity_name=update_data.get("candidate_name") or update_data.get("variant_title"),
            details={"updated_fields": [key for key in update_data if key != "updatedBy"]},
        )
        updated_pipeline_opportunity_resource = await update_pipeline_opportunity_resource(
            db, update_data, pipeline_opportunity_resource_id
        )
        if updated_pipeline_opportunity_resource is None:
            raise NotFoundException()

        return UpdatePipelineOpportunityResourceResponse(
            updatedPipelineOpportunityResource=PipelineOpportunityResourceDTO.model_validate(updated_pipeline_opportunity_resource),
            message="Pipeline Opportunity Resource updated successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find Pipeline Opportunity Resource")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while updating Pipeline Opportunity Resource")
        raise e


async def handle_delete_pipeline_opportunity_resource(
    db: AsyncSession, current_user: User, pipeline_opportunity_resource_id: UUID
) -> DeletePipelineOpportunityResourceResponse:
    try:
        # Read while the row still exists so the log keeps its name/context after the delete.
        pipeline_opportunity_resource = await get_pipeline_opportunity_resource_by_id(
            db, pipeline_opportunity_resource_id
        )
        if pipeline_opportunity_resource is not None:
            await log_activity(
                db,
                LogAction.PIPELINE_RESOURCE_DELETED,
                current_user,
                entity_type="pipeline_resource",
                entity_id=pipeline_opportunity_resource.id,
                entity_name=_resource_display_name(pipeline_opportunity_resource),
                details={
                    "opportunity_id": pipeline_opportunity_resource.opportunity_id,
                    "user_id": pipeline_opportunity_resource.user_id,
                    "status": pipeline_opportunity_resource.status,
                },
            )

        deleted_pipeline_opportunity_resource = await delete_pipeline_opportunity_resource(db, pipeline_opportunity_resource_id)
        if deleted_pipeline_opportunity_resource is None:
            raise NotFoundException()

        return DeletePipelineOpportunityResourceResponse(
            message="Pipeline Opportunity Resource deleted successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find Pipeline Opportunity Resource")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while deleting Pipeline Opportunity Resource")
        raise e


async def handle_select_pipeline_opportunity_resource(
    db: AsyncSession,
    current_user: User,
    request: PipelineOpportunityResourceSelectRequest,
) -> SelectPipelineOpportunityResourcesResponse:
    try:
        pipeline_opportunity_resources : list[PipelineOpportunityResourceModel] = await get_multiple_pipeline_opportunity_resource_by_id(
            db, request.pipeline_resource_id_list
        )
        if not pipeline_opportunity_resources:
            raise NotFoundException()

        selectable_resources = [
            pipeline_opportunity_resource
            for pipeline_opportunity_resource in pipeline_opportunity_resources
            if pipeline_opportunity_resource.status
            in (ApprovalStatus.SUGGESTED, ApprovalStatus.SELECTED)
        ]

        if not selectable_resources:
            raise NotFoundException()

        # One shared reporting user means the approver is already known at select time;
        # a split selection leaves it unset for /assign to name.
        reporting_authority = _resolve_common_reporting_user(selectable_resources)

        # Per resource, not once for whichever the validation loop happened to leave
        # bound — a five-resource select owes five audit rows.
        for pipeline_opportunity_resource in selectable_resources:
            await log_activity(
                db,
                LogAction.PIPELINE_RESOURCE_SELECTED,
                current_user,
                entity_type="pipeline_resource",
                entity_id=pipeline_opportunity_resource.id,
                entity_name=_resource_display_name(pipeline_opportunity_resource),
                details={
                    "opportunity_id": pipeline_opportunity_resource.opportunity_id,
                    "user_id": pipeline_opportunity_resource.user_id,
                    "previous_status": pipeline_opportunity_resource.status,
                    "new_status": ApprovalStatus.SELECTED,
                },
            )

        selected_pipeline_opportunity_resources = await _apply_pipeline_opportunity_resource_status_list(
            db=db,
            current_user=current_user,
            pipeline_opportunity_resource_id_list=[r.id for r in selectable_resources],
            status_data=PipelineOpportunityResourceStatusUpdate(
                status=ApprovalStatus.SELECTED,
                approval_authority_id=reporting_authority,
            ),
        )

        # SELECTED is the state that puts the resource in the reporting Team Lead's
        # approval queue, so they are told only once the transition has committed.
        for pipeline_opportunity_resource in selectable_resources:
            await _dispatch_resource_event(
                db,
                NotificationEvent.RESOURCE_SELECTED,
                current_user,
                pipeline_opportunity_resource,
                selected_by_name=current_user.fullName,
            )

        return SelectPipelineOpportunityResourcesResponse(
            selectedPipelineOpportunityResources=selected_pipeline_opportunity_resources,
            message="Pipeline Opportunity Resource selected successfully",
            status_code=200,
        )
    except (NotFoundException, AppException) as e:
        raise e
    except Exception as e:
        logging.exception("Some error occurred while selecting Pipeline Opportunity Resource")
        raise e


async def handle_assign_pipeline_opportunity_resource_to_tl(
    db: AsyncSession,
    current_user: User,
    request: PipelineOpportunityResourceAssignToTLRequest,
) -> AssignPipelineOpportunityResourcesResponse:
    """Hand a batch of selected resources over to the approver the frontend nominated.

    The update permission is enforced on the route, so reaching this handler already
    means the caller (BD team) is allowed to move the resources through the workflow.
    Who approves is client-supplied by design — the frontend knows whether a selection
    belongs to one TL or to a Manager sitting above several — and is recorded on every
    resource as approval_authority_id, which is what approve/reject then authorise against.

    One approver for the whole batch, and the batch is all-or-nothing: every id is checked
    before anything is written, so the caller fixes every problem in one round trip.
    """
    try:
        # Sending the same id twice is not an error, and the write is idempotent per row.
        resource_ids = list(dict.fromkeys(request.pipeline_resource_id_list))

        pipeline_opportunity_resources: list[PipelineOpportunityResourceModel] = await get_multiple_pipeline_opportunity_resource_by_id(
            db, resource_ids
        )
        resources_by_id = {resource.id: resource for resource in pipeline_opportunity_resources}

        # Collected rather than short-circuited: an id missing from the loaded set was
        # dropped silently before, which read as success for a resource nothing happened to.
        invalid: list[tuple[UUID, str]] = []
        for resource_id in resource_ids:
            pipeline_opportunity_resource = resources_by_id.get(resource_id)
            if pipeline_opportunity_resource is None:
                invalid.append((resource_id, "not_found"))
            elif pipeline_opportunity_resource.status == ApprovalStatus.ASSIGNED_TO_TL:
                invalid.append((resource_id, "already_assigned"))
            elif pipeline_opportunity_resource.status != ApprovalStatus.SELECTED:
                invalid.append((resource_id, "invalid_status"))

        if invalid:
            raise InvalidResourceAssignmentException(invalid)

        # The frontend names an approver only when it has to; a batch sharing one
        # reporting user resolves to that TL here.
        approval_authority_id = request.approval_authority_id or _resolve_common_reporting_user(
            pipeline_opportunity_resources
        )
        if approval_authority_id is None:
            raise AppException(
                message="Selected resources report to different team leads; an approving manager is required",
                status_code=400,
                error_code=ErrorCode.VALIDATION_ERROR,
            )

        approval_authority = await _resolve_approval_authority(db, approval_authority_id)

        for pipeline_opportunity_resource in pipeline_opportunity_resources:
            await log_activity(
                db,
                LogAction.PIPELINE_RESOURCE_ASSIGNED_TO_TL,
                current_user,
                entity_type="pipeline_resource",
                entity_id=pipeline_opportunity_resource.id,
                entity_name=_resource_display_name(pipeline_opportunity_resource),
                details={
                    "opportunity_id": pipeline_opportunity_resource.opportunity_id,
                    "user_id": pipeline_opportunity_resource.user_id,
                    "approval_authority_id": approval_authority.user_id,
                    "previous_status": pipeline_opportunity_resource.status,
                    "new_status": ApprovalStatus.ASSIGNED_TO_TL,
                },
            )

        assigned_pipeline_opportunity_resources = await _apply_pipeline_opportunity_resource_status_list(
            db=db,
            current_user=current_user,
            pipeline_opportunity_resource_id_list=resource_ids,
            status_data=PipelineOpportunityResourceStatusUpdate(
                status=ApprovalStatus.ASSIGNED_TO_TL,
                assigned_to_tl_by=current_user.user_id,
                approval_authority_id=approval_authority.user_id,
            ),
        )

        # One per resource: RESOURCE_MATCH deep-links to a single resource, so a batch
        # cannot share a notification without a navigation target that addresses a set.
        for pipeline_opportunity_resource in pipeline_opportunity_resources:
            await notify_users(
                db,
                user_ids=[approval_authority.user_id],
                notification_type=NotificationType.RESOURCE_ASSIGNED_TO_TL,
                context={
                    "opportunity_id": str(pipeline_opportunity_resource.opportunity_id),
                    "pipeline_resource_id": str(pipeline_opportunity_resource.id),
                    "candidate_name": pipeline_opportunity_resource.candidate_name,
                    "variant_title": pipeline_opportunity_resource.variant_title,
                },
                created_by=current_user.user_id,
            )

        return AssignPipelineOpportunityResourcesResponse(
            assignedPipelineOpportunityResources=assigned_pipeline_opportunity_resources,
            message="Pipeline Opportunity Resources assigned to TL successfully",
            status_code=200,
        )
    except (NotFoundException, AppException) as e:
        raise e
    except Exception as e:
        logging.exception("Some error occurred while assigning Pipeline Opportunity Resource to TL")
        raise e


async def handle_approve_pipeline_opportunity_resource(
    db: AsyncSession,
    current_user: User,
    request: PipelineOpportunityResourceApproveRequest,
    background_tasks : BackgroundTasks
) -> UpdatePipelineOpportunityResourceResponse:
    try:
        pipeline_opportunity_resource :PipelineOpportunityResourceModel = await get_pipeline_opportunity_resource_by_id(
            db, request.pipeline_resource_id
        )

        if pipeline_opportunity_resource is None:
            raise NotFoundException()

        _ensure_approval_authority(pipeline_opportunity_resource, current_user, "approve")

        if pipeline_opportunity_resource.status == ApprovalStatus.APPROVED:
            raise AppException(
                message="This resource is already Approved.",
                status_code=400,
                error_code=ErrorCode.VALIDATION_ERROR,
            )

        if pipeline_opportunity_resource.status !=  ApprovalStatus.ASSIGNED_TO_TL:
            raise AppException(
                message="Only TL assigned resources can be approved",
                status_code=400,
                error_code=ErrorCode.VALIDATION_ERROR,
            )

        return await _approve_pipeline_opportunity_resource(
            db=db,
            current_user=current_user,
            pipeline_opportunity_resource=pipeline_opportunity_resource,
            background_tasks=background_tasks,
            is_auto_approved=False,
            message="Pipeline Opportunity Resource approved successfully",
        )
    except (NotFoundException, AppException) as e:
        raise e
    except Exception as e:
        logging.exception("Some error occurred while approving Pipeline Opportunity Resource")
        raise e


async def handle_auto_approve_pipeline_opportunity_resource(
    db: AsyncSession,
    current_user: User,
    request: PipelineOpportunityResourceAutoApproveRequest,
    background_tasks: BackgroundTasks,
) -> UpdatePipelineOpportunityResourceResponse:
    """Approve a resource without the reporting user step.

    The auto_approve permission is enforced on the route, so reaching this handler
    already means the caller is allowed to bypass the reporting user approval.
    """
    try:
        pipeline_opportunity_resource: PipelineOpportunityResourceModel = await get_pipeline_opportunity_resource_by_id(
            db, request.pipeline_resource_id
        )

        if pipeline_opportunity_resource is None:
            raise NotFoundException()

        if pipeline_opportunity_resource.status != ApprovalStatus.SELECTED:
            raise AppException(
                message="Resource must be selected before approving.",
                status_code=400,
                error_code=ErrorCode.VALIDATION_ERROR,
            )

        if pipeline_opportunity_resource.status == ApprovalStatus.APPROVED:
            raise AppException(
                message="This resource is already Approved.",
                status_code=400,
                error_code=ErrorCode.VALIDATION_ERROR,
            )

        if pipeline_opportunity_resource.status not in (
            ApprovalStatus.SUGGESTED,
            ApprovalStatus.SELECTED,
        ):
            raise AppException(
                message=f"A resource that is already {pipeline_opportunity_resource.status.value} cannot be auto approved",
                status_code=400,
                error_code=ErrorCode.VALIDATION_ERROR,
            )

        return await _approve_pipeline_opportunity_resource(
            db=db,
            current_user=current_user,
            pipeline_opportunity_resource=pipeline_opportunity_resource,
            background_tasks=background_tasks,
            is_auto_approved=True,
            message="Pipeline Opportunity Resource auto approved successfully",
        )
    except (NotFoundException, AppException) as e:
        raise e
    except Exception as e:
        logging.exception("Some error occurred while auto approving Pipeline Opportunity Resource")
        raise e


async def handle_reject_pipeline_opportunity_resource(
    db: AsyncSession,
    current_user: User,
    request: PipelineOpportunityResourceRejectRequest,
) -> UpdatePipelineOpportunityResourceResponse:
    try:
        pipeline_opportunity_resource : PipelineOpportunityResourceModel = await get_pipeline_opportunity_resource_by_id(
            db, request.pipeline_resource_id
        )

        if pipeline_opportunity_resource is None:
            raise NotFoundException()

        _ensure_approval_authority(pipeline_opportunity_resource, current_user, "reject")

        if pipeline_opportunity_resource.status == ApprovalStatus.REJECTED:
            raise AppException(
                message="This resource is already Rejected.",
                status_code=400,
                error_code=ErrorCode.VALIDATION_ERROR,
            )

        if pipeline_opportunity_resource.status != ApprovalStatus.ASSIGNED_TO_TL:
            raise AppException(
                message="Only TL assigned resources can be rejected",
                status_code=400,
                error_code=ErrorCode.VALIDATION_ERROR,
            )

        await log_activity(
            db,
            LogAction.PIPELINE_RESOURCE_REJECTED,
            current_user,
            entity_type="pipeline_resource",
            entity_id=pipeline_opportunity_resource.id,
            entity_name=_resource_display_name(pipeline_opportunity_resource),
            details={
                "opportunity_id": pipeline_opportunity_resource.opportunity_id,
                "user_id": pipeline_opportunity_resource.user_id,
                "previous_status": pipeline_opportunity_resource.status,
                "new_status": ApprovalStatus.REJECTED,
                "reject_reason": request.reject_reason,
            },
        )

        response = await _apply_pipeline_opportunity_resource_status(
            db=db,
            current_user=current_user,
            pipeline_opportunity_resource_id=request.pipeline_resource_id,
            status_data=PipelineOpportunityResourceStatusUpdate(
                status=ApprovalStatus.REJECTED,
                rejected_at=datetime.now(),
                rejected_by=current_user.user_id,
                reject_reason=request.reject_reason,
                approved_at=None,
                approved_by=None,
            ),
            message="Pipeline Opportunity Resource rejected successfully",
        )

        # Fired after the transition has committed, so a notification problem can never
        # undo a rejection that already happened.
        await _dispatch_resource_event(
            db,
            NotificationEvent.RESOURCE_REJECTED,
            current_user,
            pipeline_opportunity_resource,
            rejected_by_name=current_user.fullName,
            reject_reason=request.reject_reason or "No reason provided",
        )

        return response
    except (NotFoundException, AppException) as e:
        raise e
    except Exception as e:
        logging.exception("Some error occurred while rejecting Pipeline Opportunity Resource")
        raise e