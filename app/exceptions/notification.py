from fastapi import status

from app.exceptions.custom import AppException
from app.exceptions.error_codes import ErrorCode


class NotificationNotFoundException(AppException):

    def __init__(self, notification_id=None):
        super().__init__(
            message="Notification not found",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=ErrorCode.NOTIFICATION_NOT_FOUND,
            details={"notification_id": str(notification_id)} if notification_id else None,
        )


class NotificationTypeNotConfiguredException(AppException):

    def __init__(self, notification_type=None):
        super().__init__(
            message="No content is configured for this notification type",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=ErrorCode.NOTIFICATION_TYPE_NOT_CONFIGURED,
            details={"notification_type": str(notification_type)} if notification_type else None,
        )
