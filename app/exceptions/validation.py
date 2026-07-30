from fastapi import status

from app.exceptions.custom import AppException
from app.exceptions.error_codes import ErrorCode


class UserAlreadyExists(AppException):

    def __init__(self):
        super().__init__(
            message="User already exists",
            status_code=status.HTTP_409_CONFLICT,
            error_code=ErrorCode.USER_ALREADY_EXISTS,
        )
