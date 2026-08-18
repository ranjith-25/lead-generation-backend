import logging
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.custom import NotFoundException
from app.models.firebase_token import FirebaseTokens
from app.models.user import User
from app.responses.firebase_token import (
    CreateFirebaseTokenResponse,
    DeleteFirebaseTokenResponse,
    GetFirebaseTokenResponse,
    UpdateFirebaseTokenResponse,
)
from app.schemas.firebase_token import (
    FirebaseTokenCreate,
    FirebaseTokenDTO,
    FirebaseTokenUpdate,
)
from app.services.db.firebase_token import (
    create_firebase_token,
    delete_firebase_token,
    get_all_firebase_tokens,
    get_firebase_token_by_id,
    update_firebase_token,
    get_firebase_token_by_user_id,
    
)

from app.config import NotificationType
from app.schemas.firebase_token import FirebaseNotificationPayload

async def handle_get_all_firebase_tokens(
    db: AsyncSession, current_user: User, page: int = 1, limit: int = 10
) -> GetFirebaseTokenResponse:
    try:
        firebase_tokens, total = await get_all_firebase_tokens(db, page, limit)

        return GetFirebaseTokenResponse(
            firebaseTokenList=[
                FirebaseTokenDTO.model_validate(token) for token in firebase_tokens
            ],
            total=total,
            page=page,
            limit=limit,
            total_pages=(total + limit - 1) // limit if total > 0 else 1,
            message="Firebase Tokens fetched successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find Firebase Tokens")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while getting Firebase Tokens list")
        raise e


async def handle_get_firebase_token_by_id(
    db: AsyncSession, current_user: User, firebase_token_id: UUID
) -> GetFirebaseTokenResponse:
    try:
        firebase_token = await get_firebase_token_by_id(db, firebase_token_id)
        if firebase_token is None:
            raise NotFoundException()

        return GetFirebaseTokenResponse(
            firebaseToken=FirebaseTokenDTO.model_validate(firebase_token),
            message="Firebase Token fetched successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find Firebase Token")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while getting Firebase Token details")
        raise e


async def handle_get_firebase_token_by_user_id(
    db: AsyncSession, current_user: User, user_id: UUID
) -> GetFirebaseTokenResponse:
    try:
        firebase_tokens = await get_firebase_token_by_user_id(db, user_id)

        return GetFirebaseTokenResponse(
            firebaseTokenList=[FirebaseTokenDTO.model_validate(token) for token in firebase_tokens],
            message="Firebase Token fetched successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find Firebase Token")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while getting Firebase Token details")
        raise e


async def handle_create_firebase_token(
    db: AsyncSession, current_user: User, firebase_token_create: FirebaseTokenCreate
) -> CreateFirebaseTokenResponse:
    try:
        new_firebase_token = FirebaseTokens(
            fcm_token=firebase_token_create.fcm_token,
            user_id = current_user.user_id,
            is_active= True,
            created_by=current_user.user_id,
            updated_by=current_user.user_id,
        )
        created_firebase_token : FirebaseTokenDTO = await create_firebase_token(db, new_firebase_token)

        firebaseNotificationPayload = FirebaseNotificationPayload(
            notification_type = NotificationType.EMPTY,
            title = "Notification socket implemented",
            body = "Your Session is connected with firebase for notifications",
            data = {}
        )
        send_push_notification(firebase_notification=firebaseNotificationPayload,
        tokens=[new_firebase_token.fcm_token])
        return CreateFirebaseTokenResponse(
            newFirebaseToken=FirebaseTokenDTO.model_validate(created_firebase_token),
            message="Firebase Token created successfully",
            status_code=200,
        )
    except Exception as e:
        logging.exception("Some error occurred while creating Firebase Token")
        raise e


async def handle_update_firebase_token(
    db: AsyncSession,
    current_user: User,
    firebase_token_update: FirebaseTokenUpdate,
    firebase_token_id: UUID,
) -> UpdateFirebaseTokenResponse:
    try:
        update_data = firebase_token_update.model_dump(exclude_unset=True, exclude_none=True)
        update_data.pop("is_active", None)
        update_data["updated_by"] = current_user.user_id
        updated_firebase_token = await update_firebase_token(
            db, update_data, firebase_token_id
        )
        if updated_firebase_token is None:
            raise NotFoundException()

        return UpdateFirebaseTokenResponse(
            updatedFirebaseToken=FirebaseTokenDTO.model_validate(updated_firebase_token),
            message="Firebase Token updated successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find Firebase Token")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while updating Firebase Token")
        raise e


async def handle_delete_firebase_token(
    db: AsyncSession, current_user: User, firebase_token_id: UUID
) -> DeleteFirebaseTokenResponse:
    try:
        deleted_firebase_token = await delete_firebase_token(db, firebase_token_id)
        if deleted_firebase_token is None:
            raise NotFoundException()

        return DeleteFirebaseTokenResponse(
            message="Firebase Token deleted successfully",
            status_code=200,
        )
    except NotFoundException as e:
        logging.exception("Could not find Firebase Token")
        raise e
    except Exception as e:
        logging.exception("Some error occurred while deleting Firebase Token")
        raise e

def send_push_notification(firebase_notification:FirebaseNotificationPayload,tokens: list[str]):
    """
    Send a push notification to multiple FCM tokens.
    """

    message = messaging.MulticastMessage(
        notification=messaging.Notification(
            title=firebase_notification.title,
            body=firebase_notification.body,
        ),
        data=firebase_notification.data or {},
        tokens=tokens,
    )

    response = messaging.send_each_for_multicast(message)

    return response