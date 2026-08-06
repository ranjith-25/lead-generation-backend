import uuid
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.security import require_permission
from app.models.user import User
from app.responses.user_invitation import (
    CreateUserInvitationResponse,
    DeleteUserInvitationResponse,
    GetUserInvitationResponse,
    UpdateUserInvitationResponse,
)
from app.schemas.user_invitation import UserInvitationCreate, UserInvitationUpdate
from app.services.user_invitation import (
    handle_create_user_invitation,
    handle_delete_user_invitation,
    handle_get_all_user_invitations,
    handle_get_user_invitation_by_id,
    handle_update_user_invitation,
    handle_cancel_user_invitation
)

user_invitation_router = APIRouter(prefix="/user-invitation", tags=["User Invitation"])


@user_invitation_router.get("/")
async def get_all_user_invitations(
    current_user: User = Depends(require_permission("invitation", "read")),
    db: AsyncSession = Depends(get_db),
):
    response: GetUserInvitationResponse = await handle_get_all_user_invitations(db, current_user)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )


@user_invitation_router.get("/{id}")
async def get_user_invitation_by_id(
    id: uuid.UUID,
    current_user: User = Depends(require_permission("invitation", "read")),
    db: AsyncSession = Depends(get_db),
):
    response: GetUserInvitationResponse = await handle_get_user_invitation_by_id(db, current_user, id)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )


@user_invitation_router.post("/")
async def create_user_invitation(
    user_invitation: UserInvitationCreate,
    current_user: User = Depends(require_permission("invitation", "create")),
    db: AsyncSession = Depends(get_db),
):
    response: CreateUserInvitationResponse = await handle_create_user_invitation(db, current_user, user_invitation)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )


@user_invitation_router.put("/{id}")
async def update_user_invitation(
    id: uuid.UUID,
    user_invitation: UserInvitationUpdate,
    current_user: User = Depends(require_permission("invitation", "update")),
    db: AsyncSession = Depends(get_db),
):
    response: UpdateUserInvitationResponse = await handle_update_user_invitation(db, current_user, user_invitation, id)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )


@user_invitation_router.delete("/cancel/{id}")
async def cancel_user_invitation(
    id: uuid.UUID,
    current_user: User = Depends(require_permission("invitation", "update")),
    db: AsyncSession = Depends(get_db),
):
    response: DeleteUserInvitationResponse = await handle_cancel_user_invitation(db, current_user, id)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )

@user_invitation_router.delete("/{id}")
async def delete_user_invitation(
    id: uuid.UUID,
    current_user: User = Depends(require_permission("invitation", "delete")),
    db: AsyncSession = Depends(get_db),
):
    response: DeleteUserInvitationResponse = await handle_delete_user_invitation(db, current_user, id)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )
