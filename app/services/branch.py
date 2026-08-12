import logging
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.exceptions.custom import NotFoundException
from app.models.branch import Branch
from app.models.user import User
from app.responses.branch import (
    CreateBranchResponse,
    DeleteBranchResponse,
    GetBranchResponse,
    UpdateBranchResponse,
)
from app.schemas.branch import BranchCreate, BranchDTO, BranchUpdate
from app.services.db.branch import (
    create_branch,
    delete_branch,
    get_all_branches,
    get_branch_by_id,
    update_branch,
)


async def handle_get_all_branches(
    db: AsyncSession
) -> GetBranchResponse:
    try:
        branches = await get_all_branches(db)

        return GetBranchResponse(
            branchList=[BranchDTO.model_validate(b) for b in branches],
            message="Branches fetched successfully",
            status_code=200,
        )
    except Exception as e:
        logging.exception("Some error occurred while getting Branches list")
        raise e


async def handle_get_branch_by_id(db: AsyncSession, current_user: User, branch_id: UUID) -> GetBranchResponse:
    try:
        branch = await get_branch_by_id(db, branch_id)
        if branch is None:
            raise NotFoundException()

        return GetBranchResponse(
            branch=BranchDTO.model_validate(branch),
            message="Branch fetched successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find Branch")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while getting Branch details")
        raise e


async def handle_create_branch(
    db: AsyncSession, current_user: User, branch_create: BranchCreate
) -> CreateBranchResponse:
    try:
        new_branch = Branch(
            **branch_create.model_dump(),
            createdBy=current_user.user_id,
            updatedBy=current_user.user_id,
        )
        created_branch = await create_branch(db, new_branch)
        return CreateBranchResponse(
            newBranch=BranchDTO.model_validate(created_branch),
            message="Branch created successfully",
            status_code=200,
        )
    except Exception as e:
        logging.exception("Some error occurred while creating Branch")
        raise e


async def handle_update_branch(
    db: AsyncSession, current_user: User, branch_update: BranchUpdate, branch_id: UUID
) -> UpdateBranchResponse:
    try:
        update_data = branch_update.model_dump(exclude_unset=True, exclude_none=True)
        update_data["updatedBy"] = current_user.user_id
        updated_branch = await update_branch(db, update_data, branch_id)
        if updated_branch is None:
            raise NotFoundException()

        return UpdateBranchResponse(
            updatedBranch=BranchDTO.model_validate(updated_branch),
            message="Branch updated successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find Branch")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while updating Branch")
        raise e


async def handle_delete_branch(
    db: AsyncSession, current_user: User, branch_id: UUID
) -> DeleteBranchResponse:
    try:
        deleted_branch = await delete_branch(db, branch_id)
        if deleted_branch is None:
            raise NotFoundException()

        return DeleteBranchResponse(
            message="Branch deleted successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find Branch")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while deleting Branch")
        raise e
