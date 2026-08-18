import logging
from typing import Any
from uuid import UUID

from firebase_admin import messaging
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.firebase import FirebaseNotificationSendException
from app.schemas.firebase_messaging import FirebaseNotificationPayload, SimplePushRequest
from app.schemas.notification import NotificationType
from app.services.db.firebase_token import get_firebase_token_by_user_id

logger = logging.getLogger(__name__)


def send_push_notification(
    firebase_notification: FirebaseNotificationPayload, tokens: list[str]
):
    """Send a push notification to multiple FCM tokens via multicast.

    Moved from firebase_token.py — kept sync per project preference.
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


def send_single_push(
    title: str,
    body: str,
    token: str,
    url: str | None = None,
) -> str:
    """Send a push notification to a single FCM token.

    Returns the Firebase message ID on success.
    Raises FirebaseNotificationSendException on failure.
    """
    data: dict[str, str] = {}
    if url:
        data["url"] = url

    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        data=data or None,
        token=token,
    )

    try:
        message_id = messaging.send(message)
        return message_id
    except Exception:
        logger.exception("Failed to send single push notification to token")
        raise FirebaseNotificationSendException()


def handle_send_simple_push(request: SimplePushRequest) -> dict:
    """Handle the simple push endpoint — sends a single push notification.

    Returns dict suitable for SimplePushResponse.
    """
    message_id = send_single_push(
        title=request.title,
        body=request.message,
        token=request.fcm_token,
        url=request.url,
    )
    return {
        "success": True,
        "message_id": message_id,
        "message": "Push notification sent successfully",
    }


async def send_firebase_push_for_notifications(
    db: AsyncSession,
    user_ids: list[UUID],
    notification_type: NotificationType,
    title: str,
    body: str,
    url: str | None = None,
    context: dict[str, Any] | None = None,
) -> None:
    """Delivers Firebase push notifications to all active FCM tokens belonging to target users.

    Isolated with try-except to ensure Firebase failures never break in-app notification flows.
    Moved from notifications.py.
    """
    if not user_ids:
        return

    try:
        data: dict[str, str] = {}
        if url:
            data["url"] = str(url)
        if context:
            for k, v in context.items():
                if v is not None:
                    data[str(k)] = str(v)

        payload = FirebaseNotificationPayload(
            notification_type=notification_type,
            title=title or "",
            body=body or "",
            data=data or None,
        )

        for user_id in user_ids:
            try:
                tokens = await get_firebase_token_by_user_id(db, user_id)
                active_tokens = [
                    t.fcm_token
                    for t in tokens
                    if getattr(t, "is_active", True) and getattr(t, "fcm_token", None)
                ]

                if not active_tokens:
                    logger.info(
                        "No active FCM tokens found for user_id=%s (notification_type=%s)",
                        user_id,
                        notification_type.value if hasattr(notification_type, "value") else notification_type,
                    )
                    continue

                logger.info(
                    "Sending Firebase push notification to %d token(s) for user_id=%s (notification_type=%s)",
                    len(active_tokens),
                    user_id,
                    notification_type.value if hasattr(notification_type, "value") else notification_type,
                )

                response = send_push_notification(
                    firebase_notification=payload,
                    tokens=active_tokens,
                )

                success_count = getattr(response, "success_count", 0)
                failure_count = getattr(response, "failure_count", 0)
                logger.info(
                    "Firebase push result for user_id=%s: %d succeeded, %d failed",
                    user_id,
                    success_count,
                    failure_count,
                )
            except Exception:
                logger.exception(
                    "Error sending Firebase push notification for user_id=%s (notification_type=%s)",
                    user_id,
                    notification_type.value if hasattr(notification_type, "value") else notification_type,
                )
    except Exception:
        logger.exception(
            "Unexpected error in send_firebase_push_for_notifications for notification_type=%s",
            notification_type.value if hasattr(notification_type, "value") else notification_type,
        )
