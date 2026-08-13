from datetime import datetime
import logging
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import RESOURCE_APPROVAL_NOTIFY_ROLES, RESOURCE_REJECTION_NOTIFY_ROLES
from app.exceptions.custom import AppException, NotFoundException
from app.exceptions.error_codes import ErrorCode
from app.models.pipeline_opportunity_resource import PipelineOpportunityResourceModel
from app.models.user import User
from app.responses.pipeline_opportunity_resource import (
    CreatePipelineOpportunityResourceResponse,
    DeletePipelineOpportunityResourceResponse,
    GetPipelineOpportunityResourceResponse,
    UpdatePipelineOpportunityResourceResponse,
)
from app.schemas.pipeline_opportunity_resource import (
    ApprovalStatus,
    PipelineOpportunityResourceCreate,
    PipelineOpportunityResourceDTO,
    PipelineOpportunityResourceUpdate,
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
    get_pipeline_opportunity_resource_by_opportunity_id
)
from app.schemas.ai import AITechnicalPreperationRequest
from app.schemas.notification import NotificationType
from app.services.db.opportunity import get_opportunity_details_by_id
from app.services.db.user import get_user_ids_by_role_names
from app.services.notifications import notify_users
from app.models.opportunity import Opportunity
import json
from app.schemas.opportunity import OpportunityRead
from app.services.ai import handleTechnicalPreperation
from app.services.notifications import notify_users
from app.schemas.notification import NotificationType
from fastapi import BackgroundTasks
from sqlalchemy.exc import IntegrityError


async def _apply_pipeline_opportunity_resource_status(
    db: AsyncSession,
    current_user: User,
    pipeline_opportunity_resource_id: UUID,
    status_data: dict,
    message: str,
) -> UpdatePipelineOpportunityResourceResponse:
    """Persist a dedicated status transition (select / approve / reject).

    Status changes deliberately bypass PipelineOpportunityResourceUpdate so that the
    generic update endpoint cannot move a resource through the workflow arbitrarily.
    """
    status_data["updatedBy"] = current_user.user_id
    updated_pipeline_opportunity_resource = await update_pipeline_opportunity_resource(
        db, status_data, pipeline_opportunity_resource_id
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


async def _role_recipients(
    db: AsyncSession,
    role_names: list[str],
    exclude: set[UUID],
) -> list[UUID]:
    """User ids holding any of `role_names`, minus `exclude`.

    Recipients are resolved by role rather than by hierarchy — a status change on a
    resource is a pipeline-wide signal, not something scoped to the actor's reporting
    line. `exclude` keeps people from being told about their own action, and keeps
    anyone who gets a dedicated message from also receiving the broadcast.
    """
    recipient_ids = await get_user_ids_by_role_names(db, role_names)
    return [user_id for user_id in recipient_ids if user_id not in exclude]


def _resource_display_name(
    pipeline_opportunity_resource: PipelineOpportunityResourceModel,
) -> str:
    """Prefer the person's name over the variant title when naming an approved resource."""
    user_details = pipeline_opportunity_resource.user_details
    if user_details and user_details.fullName and user_details.fullName != "Unknown User":
        return user_details.fullName
    return pipeline_opportunity_resource.variant_title


async def _notify_resource_rejected(
    db: AsyncSession,
    current_user: User,
    pipeline_opportunity_resource: PipelineOpportunityResourceModel,
    reject_reason: str | None,
) -> None:
    try:
        recipient_ids = await _role_recipients(
            db,
            RESOURCE_REJECTION_NOTIFY_ROLES,
            exclude={current_user.user_id},
        )

        if not recipient_ids:
            return

        opportunity = await get_opportunity_details_by_id(
            db, pipeline_opportunity_resource.opportunity_id
        )

        await notify_users(
            db,
            user_ids=recipient_ids,
            notification_type=NotificationType.RESOURCE_REJECTED,
            context={
                "rejected_by_name": current_user.fullName,
                "variant_title": pipeline_opportunity_resource.variant_title,
                "job_title": opportunity.title if opportunity else "",
                "company": opportunity.company if opportunity else "",
                "reject_reason": reject_reason or "No reason provided",
                "opportunity_id": str(pipeline_opportunity_resource.opportunity_id),
            },
            created_by=current_user.user_id,
        )
    except Exception:
        # The rejection itself has already committed — a notification problem must not
        # turn a successful status change into a 500.
        logging.exception(
            "Could not send rejection notifications for resource %s",
            pipeline_opportunity_resource.id,
        )


async def _notify_resource_approved(
    db: AsyncSession,
    current_user: User,
    pipeline_opportunity_resource: PipelineOpportunityResourceModel,
    opportunity: Opportunity | None,
    is_auto_approved: bool,
) -> None:
    """Fan an approval out to two audiences.

    Everyone in RESOURCE_APPROVAL_NOTIFY_ROLES gets the announcement, while the person
    whose profile was approved gets a second-person message pointing at their technical
    preparation instead. The assignee is excluded from the announcement so that one
    approval never produces two notifications for the same person.
    """
    try:
        assignee_id = pipeline_opportunity_resource.user_id
        context = {
            "approved_by_name": current_user.fullName,
            "resource_name": _resource_display_name(pipeline_opportunity_resource),
            "variant_title": pipeline_opportunity_resource.variant_title,
            "job_title": opportunity.title if opportunity else "",
            "company": opportunity.company if opportunity else "",
            "opportunity_id": str(pipeline_opportunity_resource.opportunity_id),
            "is_auto_approved": is_auto_approved,
        }

        announcement_ids = await _role_recipients(
            db,
            RESOURCE_APPROVAL_NOTIFY_ROLES,
            exclude={current_user.user_id, assignee_id},
        )

        if announcement_ids:
            await notify_users(
                db,
                user_ids=announcement_ids,
                notification_type=NotificationType.RESOURCE_APPROVED,
                context=context,
                created_by=current_user.user_id,
            )

        # The approved person is notified regardless of the role they hold — the
        # assignment is about them, not about which bucket their role falls into.
        if assignee_id:
            await notify_users(
                db,
                user_ids=[assignee_id],
                notification_type=NotificationType.RESOURCE_ASSIGNED,
                context=context,
                created_by=current_user.user_id,
            )
    except Exception:
        logging.exception(
            "Could not send approval notifications for resource %s",
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

    try:
        result: UpdatePipelineOpportunityResourceResponse = await _apply_pipeline_opportunity_resource_status(
            db=db,
            current_user=current_user,
            pipeline_opportunity_resource_id=pipeline_opportunity_resource.id,
            status_data={
                "status": ApprovalStatus.APPROVED,
                "is_auto_approved": is_auto_approved,
                "approved_at": datetime.now(),
                "approved_by": current_user.user_id,
                "rejected_at": None,
                "rejected_by": None,
                "reject_reason": None,
            },
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
        job_details=json.dumps(job_details_schema.model_dump(mode="json")),
        variant_id=str(result.updatedPipelineOpportunityResource.variant_id),
        matching_skills=result.updatedPipelineOpportunityResource.matching_skills,
        missing_skills=result.updatedPipelineOpportunityResource.missing_skills,
    )
    background_tasks.add_task(handleTechnicalPreperation, technicalPreperationRequest, result.updatedPipelineOpportunityResource.opportunity_id)

    # Hooked here rather than in the two callers so the manual approval and the auto
    # approval both notify — `job_details` is reused instead of re-querying the opportunity.
    await _notify_resource_approved(
        db=db,
        current_user=current_user,
        pipeline_opportunity_resource=pipeline_opportunity_resource,
        opportunity=job_details,
        is_auto_approved=is_auto_approved,
    )

    return result


def _ensure_reporting_user(
    pipeline_opportunity_resource: PipelineOpportunityResourceModel,
    current_user: User,
    action: str,
) -> None:
    if pipeline_opportunity_resource.user_details.reporting_to != current_user.user_id:
        raise AppException(
            message=f"Only the reporting user can {action} this resource",
            status_code=403,
            error_code=ErrorCode.NOT_ALLOWED,
        )


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
) -> UpdatePipelineOpportunityResourceResponse:
    try:
        pipeline_opportunity_resource = await get_pipeline_opportunity_resource_by_id(
            db, request.pipeline_resource_id
        )
        if pipeline_opportunity_resource is None:
            raise NotFoundException()

        if pipeline_opportunity_resource.status not in (
            ApprovalStatus.SUGGESTED,
            ApprovalStatus.SELECTED,
        ):
            raise AppException(
                message=f"A resource that is already {pipeline_opportunity_resource.status.value} cannot be selected",
                status_code=400,
                error_code=ErrorCode.VALIDATION_ERROR,
            )

        return await _apply_pipeline_opportunity_resource_status(
            db=db,
            current_user=current_user,
            pipeline_opportunity_resource_id=request.pipeline_resource_id,
            status_data={"status": ApprovalStatus.SELECTED},
            message="Pipeline Opportunity Resource selected successfully",
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
) -> UpdatePipelineOpportunityResourceResponse:
    """Hand a selected resource over to the TL (the resource's reporting user).

    The update permission is enforced on the route, so reaching this handler already
    means the caller (BD team) is allowed to move the resource through the workflow.
    The TL is not stored on the resource — it is the reporting user of the resource's
    user, the same person the approve/reject handlers authorise against.
    """
    try:
        pipeline_opportunity_resource: PipelineOpportunityResourceModel = await get_pipeline_opportunity_resource_by_id(
            db, request.pipeline_resource_id
        )

        if pipeline_opportunity_resource is None:
            raise NotFoundException()

        if pipeline_opportunity_resource.status == ApprovalStatus.ASSIGNED_TO_TL:
            raise AppException(
                message="This resource is already assigned to the TL.",
                status_code=400,
                error_code=ErrorCode.VALIDATION_ERROR,
            )

        if pipeline_opportunity_resource.status != ApprovalStatus.SELECTED:
            raise AppException(
                message="Only selected resources can be assigned to the TL",
                status_code=400,
                error_code=ErrorCode.VALIDATION_ERROR,
            )

        tl_user_id = (
            pipeline_opportunity_resource.user_details.reporting_to
            if pipeline_opportunity_resource.user_details
            else None
        )
        if tl_user_id is None:
            raise AppException(
                message="This resource has no reporting user to assign to",
                status_code=400,
                error_code=ErrorCode.VALIDATION_ERROR,
            )

        result: UpdatePipelineOpportunityResourceResponse = await _apply_pipeline_opportunity_resource_status(
            db=db,
            current_user=current_user,
            pipeline_opportunity_resource_id=request.pipeline_resource_id,
            status_data={
                "status": ApprovalStatus.ASSIGNED_TO_TL,
                "assigned_to_tl_by": current_user.user_id,
            },
            message="Pipeline Opportunity Resource assigned to TL successfully",
        )

        await notify_users(
            db,
            user_ids=[tl_user_id],
            notification_type=NotificationType.RESOURCE_ASSIGNED_TO_TL,
            context={
                "opportunity_id": str(pipeline_opportunity_resource.opportunity_id),
                "pipeline_resource_id": str(pipeline_opportunity_resource.id),
                "candidate_name": pipeline_opportunity_resource.candidate_name,
                "variant_title": pipeline_opportunity_resource.variant_title,
            },
            created_by=current_user.user_id,
        )

        return result
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

        _ensure_reporting_user(pipeline_opportunity_resource, current_user, "approve")

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

        _ensure_reporting_user(pipeline_opportunity_resource, current_user, "reject")

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

        response = await _apply_pipeline_opportunity_resource_status(
            db=db,
            current_user=current_user,
            pipeline_opportunity_resource_id=request.pipeline_resource_id,
            status_data={
                "status": ApprovalStatus.REJECTED,
                "rejected_at": datetime.now(),
                "rejected_by": current_user.user_id,
                "reject_reason": request.reject_reason,
                "approved_at": None,
                "approved_by": None,
            },
            message="Pipeline Opportunity Resource rejected successfully",
        )

        await _notify_resource_rejected(
            db=db,
            current_user=current_user,
            pipeline_opportunity_resource=pipeline_opportunity_resource,
            reject_reason=request.reject_reason,
        )

        return response
    except (NotFoundException, AppException) as e:
        raise e
    except Exception as e:
        logging.exception("Some error occurred while rejecting Pipeline Opportunity Resource")
        raise e