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


class ProjectDomainNotFoundException(AppException):

    def __init__(self, project_domain_id=None):
        super().__init__(
            message="Project domain not found",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=ErrorCode.DOMAIN_NOT_FOUND,
            details={"projectDomainID": project_domain_id} if project_domain_id else None,
        )


class TechStackNotFoundException(AppException):

    def __init__(self, techstack_ids=None):
        super().__init__(
            message="One or more techstacks were not found",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=ErrorCode.TECHSTACK_NOT_FOUND,
            details={"techstack_ids": techstack_ids} if techstack_ids else None,
        )


class CaseStudyNotFoundException(AppException):

    def __init__(self):
        super().__init__(
            message="This project has no case study document",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=ErrorCode.CASE_STUDY_NOT_FOUND,
        )


class CaseStudyEmptyException(AppException):

    def __init__(self):
        super().__init__(
            message="The uploaded case study file is empty",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=ErrorCode.CASE_STUDY_INVALID,
        )


class CaseStudyUnsupportedTypeException(AppException):

    def __init__(self, allowed_extensions=None):
        super().__init__(
            message="Unsupported case study file type",
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            error_code=ErrorCode.CASE_STUDY_UNSUPPORTED_TYPE,
            details={"allowed": allowed_extensions} if allowed_extensions else None,
        )


class CaseStudyTooLargeException(AppException):

    def __init__(self, max_size_mb=None):
        super().__init__(
            message="The case study file is too large",
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            error_code=ErrorCode.CASE_STUDY_TOO_LARGE,
            details={"max_size_mb": max_size_mb} if max_size_mb else None,
        )

class CantFetchFilterException(AppException):

    def __init__(self):
        super().__init__(
            message="Can't fetch the filters for the project",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=ErrorCode.CANT_FETCH_PROJECT_FILTERS,
        )