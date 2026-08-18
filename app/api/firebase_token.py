from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.api.deps import get_db
from app.core.security import require_permission
from app.models.user import User
from app.responses.firebase_token import (
    CreateFirebaseTokenResponse,
    DeleteFirebaseTokenResponse,
    GetFirebaseTokenResponse,
    UpdateFirebaseTokenResponse,
)
from app.schemas.firebase_token import (
    FirebaseTokenCreate,
    FirebaseTokenUpdate,
)
from app.services.firebase_token import (
    handle_create_firebase_token,
    handle_delete_firebase_token,
    handle_get_all_firebase_tokens,
    handle_get_firebase_token_by_id,
    handle_update_firebase_token,
    handle_get_firebase_token_by_user_id,
)
from app.responses.firebase_notification import SimplePushResponse
from app.schemas.firebase_messaging import SimplePushRequest
from app.services.firebase_messaging import handle_send_simple_push

firebase_token_router = APIRouter(prefix="/firebase-token", tags=["Firebase Token"])


@firebase_token_router.get("/")
async def get_all_firebase_tokens(
    page: int = 1,
    limit: int = 10,
    current_user: User = Depends(require_permission("firebase_token", "read")),
    db: AsyncSession = Depends(get_db),
):
    response: GetFirebaseTokenResponse = await handle_get_all_firebase_tokens(db, current_user, page, limit)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )


@firebase_token_router.get("/{id}")
async def get_firebase_token_by_id(
    id: UUID,
    current_user: User = Depends(require_permission("firebase_token", "read")),
    db: AsyncSession = Depends(get_db),
):
    response: GetFirebaseTokenResponse = await handle_get_firebase_token_by_id(db, current_user, id)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )


@firebase_token_router.get("/user/{user_id}")
async def get_firebase_token_by_user_id(
    user_id: UUID,
    current_user: User = Depends(require_permission("firebase_token", "read")),
    db: AsyncSession = Depends(get_db),
):
    response: GetFirebaseTokenResponse = await handle_get_firebase_token_by_user_id(db, current_user, user_id)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )


@firebase_token_router.post("/")
async def create_firebase_token(
    firebase_token: FirebaseTokenCreate,
    current_user: User = Depends(require_permission("firebase_token", "create")),
    db: AsyncSession = Depends(get_db),
):
    response: CreateFirebaseTokenResponse = await handle_create_firebase_token(db, current_user, firebase_token)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )


@firebase_token_router.put("/{id}")
async def update_firebase_token(
    id: UUID,
    firebase_token: FirebaseTokenUpdate,
    current_user: User = Depends(require_permission("firebase_token", "update")),
    db: AsyncSession = Depends(get_db),
):
    response: UpdateFirebaseTokenResponse = await handle_update_firebase_token(db, current_user, firebase_token, id)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )


@firebase_token_router.delete("/{id}")
async def delete_firebase_token(
    id: UUID,
    current_user: User = Depends(require_permission("firebase_token", "delete")),
    db: AsyncSession = Depends(get_db),
):
    response: DeleteFirebaseTokenResponse = await handle_delete_firebase_token(db, current_user, id)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )


@firebase_token_router.post("/push", response_model=SimplePushResponse)
async def send_push(
    request: SimplePushRequest,
    current_user: User = Depends(require_permission("firebase_token", "create")),
):
    """Send a push notification to a single FCM device token."""
    response = handle_send_simple_push(request)
    return JSONResponse(
        content=response,
        status_code=200,
    )
