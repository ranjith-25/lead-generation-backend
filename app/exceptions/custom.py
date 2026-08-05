from fastapi import status
from app.exceptions.error_codes import ErrorCode
class AppException(Exception):

    def __init__(
        self,
        message: str,
        status_code: int,
        error_code: str,
        details=None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details

class NotFoundException(AppException):
    def __init__(self):
        super().__init__(
            message="Data not found",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=ErrorCode.DATA_NOT_FOUND,
        )