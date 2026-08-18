from fastapi import status

from app.exceptions.error_codes import ErrorCode
from app.exceptions.custom import AppException


class FirebaseConnectionException(AppException):
    def __init__(self):
        super().__init__(
            message="Unable to connect to Firebase",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code=ErrorCode.FIREBASE_CONNECTION_FAILED,
        )


class FirebaseClientNotInitializedException(AppException):
    def __init__(self):
        super().__init__(
            message="Firebase client has not been initialized",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=ErrorCode.FIREBASE_CLIENT_NOT_INITIALIZED,
        )


class FirebaseInvalidCredentialsException(AppException):
    def __init__(self):
        super().__init__(
            message="Invalid Firebase credentials",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=ErrorCode.FIREBASE_INVALID_CREDENTIALS,
        )


class FirebaseTokenInvalidException(AppException):
    def __init__(self, token=None):
        super().__init__(
            message="The Firebase device token is invalid",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=ErrorCode.FIREBASE_INVALID_TOKEN,
            details={"token": str(token)} if token else None,
        )


class FirebaseTokenNotRegisteredException(AppException):
    def __init__(self, token=None):
        super().__init__(
            message="The Firebase device token is no longer registered",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=ErrorCode.FIREBASE_TOKEN_NOT_REGISTERED,
            details={"token": str(token)} if token else None,
        )


class FirebaseNotificationSendException(AppException):
    def __init__(self):
        super().__init__(
            message="Failed to send push notification",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=ErrorCode.FIREBASE_NOTIFICATION_SEND_FAILED,
        )


class FirebaseNotificationBatchSendException(AppException):
    def __init__(self):
        super().__init__(
            message="Failed to send one or more push notifications",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=ErrorCode.FIREBASE_BATCH_NOTIFICATION_SEND_FAILED,
        )


class FirebaseTopicSubscriptionException(AppException):
    def __init__(self, topic=None):
        super().__init__(
            message="Failed to subscribe devices to the Firebase topic",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=ErrorCode.FIREBASE_TOPIC_SUBSCRIPTION_FAILED,
            details={"topic": str(topic)} if topic else None,
        )


class FirebaseTopicUnsubscriptionException(AppException):
    def __init__(self, topic=None):
        super().__init__(
            message="Failed to unsubscribe devices from the Firebase topic",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=ErrorCode.FIREBASE_TOPIC_UNSUBSCRIPTION_FAILED,
            details={"topic": str(topic)} if topic else None,
        )


class FirebaseInvalidTopicException(AppException):
    def __init__(self, topic=None):
        super().__init__(
            message="Invalid Firebase notification topic",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=ErrorCode.FIREBASE_INVALID_TOPIC,
            details={"topic": str(topic)} if topic else None,
        )


class FirebaseNotificationPayloadException(AppException):
    def __init__(self):
        super().__init__(
            message="Invalid Firebase notification payload",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=ErrorCode.FIREBASE_INVALID_NOTIFICATION_PAYLOAD,
        )