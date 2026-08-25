from uuid import UUID

from fastapi import status

from app.exceptions.custom import AppException
from app.exceptions.error_codes import ErrorCode


class InvalidResourceAssignmentException(AppException):
    """Every id in the batch that cannot be assigned, with why.

    The batch is rejected as a whole rather than partially applied, so the caller fixes
    every problem in one round trip instead of one per request.
    """

    def __init__(self, invalid: list[tuple[UUID, str]]):
        super().__init__(
            message="Some resources cannot be assigned",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=ErrorCode.INVALID_RESOURCE_ASSIGNMENT,
            # Stringified ids and stable reason slugs — `details` is JSON-encoded straight
            # into the error envelope, and the frontend maps the slug to its own copy.
            details={
                "invalid": [
                    {"id": str(resource_id), "reason": reason}
                    for resource_id, reason in invalid
                ]
            },
        )
