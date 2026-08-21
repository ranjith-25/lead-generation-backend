import logging
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.config import BENCH_STATUS_NAME, LogAction
from app.exceptions.custom import NotFoundException
from app.models.user_project import UserProject
from app.models.user import User
from app.responses.user_project import (
    CreateUserProjectResponse,
    DeleteUserProjectResponse,
    GetUserProjectResponse,
    UpdateUserProjectResponse,
    UserProjectConfigurationsData,
    UserProjectConfigurationsResponse,
)
from app.schemas.user_project import (
    ProjectInfo,
    RoleInfo,
    TechStackInfo,
    UserProjectCreate,
    UserProjectDTO,
    UserProjectDetailDTO,
    UserProjectUpdate,
)
from app.services.db.user_bench import (
    count_allocations_for_users,
    get_bench_status_id,
    get_working_status_map,
    set_working_status,
)
from app.services.db.user import get_user_by_id
from app.services.db.user_project import (
    create_user_project,
    delete_user_project,
    get_all_user_projects,
    get_allocation_user_id,
    get_user_project_by_id,
    get_user_project_configurations,
    update_user_project,
)
from app.services.system_log import log_activity


async def sync_bench_status(
    db: AsyncSession, user_ids: Sequence[UUID], actor_id: UUID | None
) -> int:
    """Move any of `user_ids` left with zero allocations onto the bench status. Returns how many.

    Called after an allocation is soft-deleted or a project is removed, so it decides on the
    state that is already committed rather than predicting one. `count_allocations_for_users`
    counts only live allocations, so a soft-deleted one correctly frees its holder.

    Three deliberate non-behaviours:

    1. It never moves anybody *off* bench. Gaining an allocation is not evidence that a
       deliberate status such as Notice Period or Resigned should be overwritten, so
       un-benching stays a manual act.
    2. A missing bench row in `user_status` is a warning, not an error — auditing an org's
       lookup data is not worth failing the delete that triggered this.
    3. Users already on bench are skipped, so re-deleting allocations for the same person does
       not fill the system log with no-ops.
    """
    if not user_ids:
        return 0

    unique_ids = list(dict.fromkeys(user_ids))

    bench_status_id = await get_bench_status_id(db)
    if bench_status_id is None:
        logging.warning(
            "No active user_status row named %r — skipping the auto-bench sync for %s user(s)",
            BENCH_STATUS_NAME,
            len(unique_ids),
        )
        return 0

    allocation_counts = await count_allocations_for_users(db, unique_ids)
    # Absent from the grouped count means no allocation rows at all — that is the bench case.
    projectless_ids = [uid for uid in unique_ids if allocation_counts.get(uid, 0) == 0]
    if not projectless_ids:
        return 0

    status_map = await get_working_status_map(db, projectless_ids)

    to_bench = [
        uid
        for uid in projectless_ids
        # No personal-info row means no working_status_id to move, so there is nothing to do.
        if uid in status_map and status_map[uid][0] != bench_status_id
    ]
    if not to_bench:
        return 0

    # Resolved once and passed as the User object: log_activity would otherwise re-query the
    # same actor for every row it stages.
    actor = await get_user_by_id(db, actor_id) if actor_id else None

    # Staged before the write so that the commit below flushes the log rows in the same
    # transaction as the status change, matching handle_delete_user_personal_info.
    for user_id in to_bench:
        previous_status_id, user_name = status_map[user_id]
        await log_activity(
            db,
            LogAction.USER_BENCHED,
            actor or actor_id,
            entity_type="user",
            entity_id=user_id,
            entity_name=user_name,
            details={
                "reason": "no_active_project_allocations",
                "previous_working_status_id": previous_status_id,
                "new_working_status_id": bench_status_id,
            },
        )

    updated = await set_working_status(db, to_bench, bench_status_id)
    await db.commit()

    logging.info("Auto-benched %s user(s) left without any project allocation", updated)
    return updated


async def handle_get_user_project_configurations(
    db: AsyncSession, current_user: User
) -> UserProjectConfigurationsResponse:
    try:
        projects, roles, techstacks = await get_user_project_configurations(db)

        return UserProjectConfigurationsResponse(
            data=UserProjectConfigurationsData(
                projects=list(projects),
                roles=list(roles),
                techstacks=list(techstacks),
            ),
            message="User Project configurations fetched successfully",
        )
    except Exception as e:
        logging.exception("Some error occurred while getting User Project configurations")
        raise e


def _to_detail_dto(row) -> UserProjectDetailDTO:
    """Map a (UserProject, project_name, role_name, techstack_name) row to the read DTO."""

    user_project, project_name, role_name, techstack_name = row

    return UserProjectDetailDTO(
        project=ProjectInfo(
            project_id=user_project.project_id,
            project_name=project_name,
        ),
        role=RoleInfo(
            role_id=user_project.role_id,
            role_name=role_name,
        ),
        techstack=TechStackInfo(
            techstack_id=user_project.techstack_id,
            techstack_name=techstack_name,
        ),
        user_id=user_project.user_id,
        user_project_id=user_project.user_project_id,
        allocated_by=user_project.allocated_by,
        allocation_updated_by=user_project.allocation_updated_by,
        created_at=user_project.created_at,
        updated_at=user_project.updated_at,
    )


async def handle_search_user_projects(
    db: AsyncSession, current_user: User, user_id: UUID | None = None
) -> GetUserProjectResponse:
    try:
        user_projects = await get_all_user_projects(db, user_id)

        return GetUserProjectResponse(
            userProjectList=[_to_detail_dto(row) for row in user_projects],
            message="User Projects fetched successfully")
    except Exception as e:
        logging.exception("Some error occurred while getting User Projects list")
        raise e


async def handle_get_user_project_by_id(
    db: AsyncSession, current_user: User, user_project_id: UUID
) -> GetUserProjectResponse:
    try:
        user_project = await get_user_project_by_id(db, user_project_id)
        if user_project is None:
            raise NotFoundException()

        return GetUserProjectResponse(
            userProject=_to_detail_dto(user_project),
            message="User Project fetched successfully")
    except NotFoundException as e:
        logging.exception("Could not find User Project")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while getting User Project details")
        raise e


async def handle_create_user_project(
    db: AsyncSession, current_user: User, user_project_create: UserProjectCreate
) -> CreateUserProjectResponse:
    try:
        new_user_project = UserProject(
            **user_project_create.model_dump(),
            allocated_by=current_user.user_id,
        )
        created_user_project = await create_user_project(db, new_user_project)
        return CreateUserProjectResponse(
            newUserProject=UserProjectDTO.model_validate(created_user_project),
            message="User Project created successfully")
    except Exception as e:
        logging.exception("Some error occurred while creating User Project")
        raise e


async def handle_update_user_project(
    db: AsyncSession,
    current_user: User,
    user_project_update: UserProjectUpdate,
    user_project_id: UUID,
) -> UpdateUserProjectResponse:
    try:
        update_data = user_project_update.model_dump(exclude_unset=True, exclude_none=True)
        update_data["allocation_updated_by"] = current_user.user_id

        # Read before the update: reassigning an allocation can leave its previous holder with
        # nothing, and after the write that id is no longer on the row.
        previous_user_id = await get_allocation_user_id(db, user_project_id)

        updated_user_project = await update_user_project(db, update_data, user_project_id)
        if updated_user_project is None:
            raise NotFoundException()

        # Read off the ORM row before the sync commits and expires it.
        new_user_id = updated_user_project.user_id
        response_dto = UserProjectDTO.model_validate(updated_user_project)

        # Only the previous holder can have been emptied — the new one now owns this row, so
        # syncing them would always be a no-op.
        if previous_user_id is not None and previous_user_id != new_user_id:
            await sync_bench_status(db, [previous_user_id], current_user.user_id)

        return UpdateUserProjectResponse(
            updatedUserProject=response_dto,
            message="User Project updated successfully")
    except NotFoundException as e:
        logging.exception("Could not find User Project")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while updating User Project")
        raise e


async def handle_delete_user_project(
    db: AsyncSession, current_user: User, user_project_id: UUID
) -> DeleteUserProjectResponse:
    try:
        # Captured before the delete — afterwards the row reads as deleted, so the lookup that
        # names the freed user no longer returns them.
        freed_user_id = await get_allocation_user_id(db, user_project_id)

        # Soft delete: the row is flagged, not removed. An id that is unknown *or* already
        # deleted comes back as None and surfaces as the same 404.
        deleted_user_project = await delete_user_project(db, user_project_id)
        if deleted_user_project is None:
            raise NotFoundException()

        if freed_user_id is not None:
            await sync_bench_status(db, [freed_user_id], current_user.user_id)

        return DeleteUserProjectResponse(
            message="User Project deleted successfully"
        )
    except NotFoundException as e:
        logging.exception("Could not find User Project")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while deleting User Project")
        raise e