from fastapi import status

from app.exceptions.custom import AppException
from app.exceptions.error_codes import ErrorCode


class SystemLogNotFoundException(AppException):

    def __init__(self, log_id=None):
        super().__init__(
            message="System log not found",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=ErrorCode.SYSTEM_LOG_NOT_FOUND,
            details={"log_id": str(log_id)} if log_id else None,
        )
