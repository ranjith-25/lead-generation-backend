from fastapi import status

from app.exceptions.error_codes import ErrorCode
from app.exceptions.custom import AppException


class S3FileNotFoundException(AppException):
    def __init__(self, object_key=None):
        super().__init__(
            message="The requested file was not found",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=ErrorCode.S3_FILE_NOT_FOUND,
            details={"object_key": str(object_key)} if object_key else None,
        )


class S3UploadException(AppException):
    def __init__(self, object_key=None):
        super().__init__(
            message="Failed to upload the file",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=ErrorCode.S3_UPLOAD_FAILED,
            details={"object_key": str(object_key)} if object_key else None,
        )


class S3DownloadException(AppException):
    def __init__(self, object_key=None):
        super().__init__(
            message="Failed to download the file",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=ErrorCode.S3_DOWNLOAD_FAILED,
            details={"object_key": str(object_key)} if object_key else None,
        )


class S3StreamException(AppException):
    def __init__(self, object_key=None):
        super().__init__(
            message="Failed to stream the file",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=ErrorCode.S3_STREAM_FAILED,
            details={"object_key": str(object_key)} if object_key else None,
        )


class S3DeleteException(AppException):
    def __init__(self, object_key=None):
        super().__init__(
            message="Failed to delete the file",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=ErrorCode.S3_DELETE_FAILED,
            details={"object_key": str(object_key)} if object_key else None,
        )


class S3FileExistsCheckException(AppException):
    def __init__(self, object_key=None):
        super().__init__(
            message="Failed to verify whether the file exists",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=ErrorCode.S3_FILE_EXISTS_CHECK_FAILED,
            details={"object_key": str(object_key)} if object_key else None,
        )


class S3ConnectionException(AppException):
    def __init__(self):
        super().__init__(
            message="Unable to connect to file storage",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code=ErrorCode.S3_CONNECTION_FAILED,
        )


class S3ClientNotInitializedException(AppException):
    def __init__(self):
        super().__init__(
            message="S3 client has not been initialized",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=ErrorCode.S3_CLIENT_NOT_INITIALIZED,
        )


class S3InvalidObjectKeyException(AppException):
    def __init__(self, object_key=None):
        super().__init__(
            message="Invalid file object key",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=ErrorCode.S3_INVALID_OBJECT_KEY,
            details={"object_key": str(object_key)} if object_key else None,
        )


class S3PresignedUrlException(AppException):
    def __init__(self, object_key=None):
        super().__init__(
            message="Failed to generate the file access URL",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=ErrorCode.S3_PRESIGNED_URL_FAILED,
            details={"object_key": str(object_key)} if object_key else None,
        )