from uuid import UUID

from fastapi import status

from app.exceptions.custom import AppException
from app.exceptions.error_codes import ErrorCode


class UnknownFeatureException(AppException):
    def __init__(self, feature_ids: list[UUID]):
        super().__init__(
            message="Unknown feature in the permission payload",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=ErrorCode.FEATURE_NOT_FOUND,
            # the offending ids have to travel back as strings — `details` is JSON-encoded
            # straight into the error envelope and UUID is not serializable
            details={"featureIDs": [str(feature_id) for feature_id in feature_ids]},
        )


class UnknownPermissionException(AppException):
    def __init__(self, permission_ids: list[UUID]):
        super().__init__(
            message="Unknown permission in the permission payload",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=ErrorCode.PERMISSION_NOT_FOUND,
            details={"permissionIDs": [str(permission_id) for permission_id in permission_ids]},
        )


class ConflictingPermissionToggleException(AppException):
    """The same feature/permission pair was sent twice with opposite values — there is no
    sensible way to pick a winner, so the whole request is rejected rather than half-applied."""

    def __init__(self, pairs: list[tuple[UUID, UUID]]):
        super().__init__(
            message="The same permission was toggled both on and off in one request",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=ErrorCode.CONFLICTING_PERMISSION_TOGGLE,
            details={
                "conflicts": [
                    {"featureID": str(feature_id), "permissionID": str(permission_id)}
                    for feature_id, permission_id in pairs
                ]
            },
        )
