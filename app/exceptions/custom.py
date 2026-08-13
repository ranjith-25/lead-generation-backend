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

class InvitationCancelledException(AppException):
    def __init__(self):
        super().__init__(
            message="Invitation is cancelled",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=ErrorCode.INVITATION_CANCELLED,
        )

class InvitationRegisteredException(AppException):
    def __init__(self):
        super().__init__(
            message="User has already registered using this invitation.",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=ErrorCode.INVITATION_USED,
        )
        
class IncorrectPasswordException(AppException):
    def __init__(self):
        super().__init__(
            message = "Enter the correct password", 
            status_code = status.HTTP_401_UNAUTHORIZED,
            error_code = ErrorCode.INCORRECT_PASSWORD,
        )
        
class ConfirmPasswordMismatchException(AppException):
    def __init__(self):
        super().__init__(
            message="Passwords do not match",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=ErrorCode.CONFIRM_PASSWORD_MISMATCH,
        )

class LegacyRoleDeleteException(AppException):
    def __init__(self):
        super().__init__(
            message="This is a default role and cannot be deleted",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=ErrorCode.LEGACY_ROLE_DELETE_NOT_ALLOWED,
        )


class LegacyRoleUpdateException(AppException):
    def __init__(self):
        super().__init__(
            message="This is a default role and cannot be renamed",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=ErrorCode.LEGACY_ROLE_UPDATE_NOT_ALLOWED,
        )


class OpportunityAlreadyExistsException(AppException):
    def __init__(self, opportunity_id=None):
        super().__init__(
            message="An opportunity for this job posting URL already exists",
            status_code=status.HTTP_409_CONFLICT,
            error_code=ErrorCode.OPPORTUNITY_ALREADY_EXISTS,
            details={"opportunityID": str(opportunity_id)} if opportunity_id else None,
        )