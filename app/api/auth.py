from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse
from app.api.deps import get_current_user, oauth2_scheme
from app.core.connections.postgres import get_db
from app.services.auth import authenticate_user, logout_user,handle_signup_invitation
from app.models.user import User
from app.schemas.user import UserRead,UserRegistrationFromInvitation
from app.responses.authentication import AuthenticationResponse
from app.responses.base import BaseResponse
from app.responses.authentication import UserRegistrationFromInvitationResponse
from app.services.hierarchy import handleGetHierarchy
from app.responses.authentication import HierarchyResponse
from app.core.security import require_permission
import uuid
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=AuthenticationResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
) -> AuthenticationResponse:
    return await authenticate_user(db, form_data)


@router.post("/logout", response_model=BaseResponse)
async def logout(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> BaseResponse:
    return await logout_user(db, token)


@router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(current_user)

@router.get("/reportingHierarchy",response_model=HierarchyResponse)
async def get_hierarchy(current_user : User = Depends(require_permission("user_hierarchy","read")),db: AsyncSession = Depends(get_db)) : 

    response : HierarchyResponse = await handleGetHierarchy(db)
    return JSONResponse(
        status_code= 200,
        content=response.model_dump(mode="json")
    ) 

@router.post("/signup/{invitationID}")
async def signup_from_invitation(invitationID: uuid.UUID,registration_data : UserRegistrationFromInvitation,db: AsyncSession = Depends(get_db)):
    response : UserRegistrationFromInvitationResponse = await handle_signup_invitation(db,invitationID,registration_data)
    return JSONResponse(
        status_code= 200,
        content=response.model_dump(mode="json")
    ) 
