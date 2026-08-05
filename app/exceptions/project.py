from fastapi import status

from app.exceptions.custom import AppException
from app.exceptions.error_codes import ErrorCode


class ProjectNotFoundException(AppException):

    def __init__(self):
        super().__init__(
            message="Project not found",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=ErrorCode.PROJECT_NOT_FOUND,
        )


class ProjectAlreadyExistsException(AppException):

    def __init__(self):
        super().__init__(
            message="A project with this name already exists",
            status_code=status.HTTP_409_CONFLICT,
            error_code=ErrorCode.PROJECT_ALREADY_EXISTS,
        )


class DomainNotFoundException(AppException):

    def __init__(self, domain_ids=None):
        super().__init__(
            message="One or more domains were not found",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=ErrorCode.DOMAIN_NOT_FOUND,
            details={"domain_ids": domain_ids} if domain_ids else None,
        )


class TechStackNotFoundException(AppException):

    def __init__(self, techstack_ids=None):
        super().__init__(
            message="One or more techstacks were not found",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=ErrorCode.TECHSTACK_NOT_FOUND,
            details={"techstack_ids": techstack_ids} if techstack_ids else None,
        )
