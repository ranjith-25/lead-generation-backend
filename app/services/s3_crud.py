from typing import AsyncIterator, BinaryIO

from botocore.exceptions import ClientError

from app.core.settings import settings
from app.core.connections.s3 import get_s3_client
from app.exceptions.s3_exceptions import (
    S3DeleteException,
    S3DownloadException,
    S3FileExistsCheckException,
    S3FileNotFoundException,
    S3InvalidObjectKeyException,
    S3PresignedUrlException,
    S3StreamException,
    S3UploadException,
)
import logging

logger = logging.getLogger(__name__)

def _validate_object_key(object_key: str) -> None:
    """
    Validate the S3 object key before performing an operation.
    """
    if not object_key or not object_key.strip():
        raise S3InvalidObjectKeyException(object_key)


def _is_file_not_found_error(exc: ClientError) -> bool:
    """
    Determine whether an AWS ClientError indicates that
    the requested S3 object does not exist.
    """
    error_code = str(
        exc.response.get("Error", {}).get("Code", "")
    )

    return error_code in (
        "404",
        "NoSuchKey",
        "NotFound",
    )


async def upload_fileobj(
    file_obj: BinaryIO,
    object_key: str,
    content_type: str | None = None,
) -> str:
    """
    Upload a file-like object directly to S3.

    The file object is streamed to S3 instead of loading
    the complete file into application memory.

    Args:
        file_obj:
            File-like object to upload.

        object_key:
            Destination key inside the S3 bucket.

        content_type:
            Optional MIME type of the file.

    Returns:
        The S3 object key.
    """
    _validate_object_key(object_key)

    if file_obj is None:
        raise S3UploadException(object_key)

    extra_args = {}

    if content_type:
        extra_args["ContentType"] = content_type

    s3_client = get_s3_client()

    try:
        await s3_client.upload_fileobj(
            Fileobj=file_obj,
            Bucket=settings.AWS_S3_BUCKET,
            Key=object_key,
            ExtraArgs=extra_args if extra_args else None,
        )

        return object_key

    except ClientError as exc:
        logger.exception("Error uploading file for object key: %s", object_key)
        raise S3UploadException(object_key) from exc

    except Exception as exc:
        logger.exception("Error uploading file for object key: %s", object_key)
        raise S3UploadException(object_key) from exc


async def upload_file(
    file_path: str,
    object_key: str,
    content_type: str | None = None,
) -> str:
    """
    Upload an existing local file from disk to S3.

    Args:
        file_path:
            Local path of the file.

        object_key:
            Destination key inside the S3 bucket.

        content_type:
            Optional MIME type of the file.

    Returns:
        The S3 object key.
    """
    _validate_object_key(object_key)

    if not file_path:
        logger.error("File path is required")
        raise S3UploadException(object_key)

    extra_args = {}

    if content_type:
        extra_args["ContentType"] = content_type

    s3_client = get_s3_client()

    try:
        await s3_client.upload_file(
            Filename=file_path,
            Bucket=settings.AWS_S3_BUCKET,
            Key=object_key,
            ExtraArgs=extra_args if extra_args else None,
        )

        return object_key

    except ClientError as exc:
        logger.exception("Error uploading file from path %s for object key: %s", file_path, object_key)
        raise S3UploadException(object_key) from exc

    except Exception as exc:
        logger.exception("Error uploading file from path %s for object key: %s", file_path, object_key)
        raise S3UploadException(object_key) from exc


async def upload_bytes(
    file_data: bytes,
    object_key: str,
    content_type: str | None = None,
) -> str:
    """
    Upload raw bytes directly to S3.

    Best suited for small payloads such as thumbnails
    or generated files that already exist in memory.

    Args:
        file_data:
            File contents.

        object_key:
            Destination key inside the S3 bucket.

        content_type:
            Optional MIME type of the file.

    Returns:
        The S3 object key.
    """
    _validate_object_key(object_key)

    if file_data is None:
        raise S3UploadException(object_key)

    extra_args = {}

    if content_type:
        extra_args["ContentType"] = content_type

    s3_client = get_s3_client()

    try:
        await s3_client.put_object(
            Bucket=settings.AWS_S3_BUCKET,
            Key=object_key,
            Body=file_data,
            **extra_args,
        )

        return object_key

    except ClientError as exc:
        logger.exception("Error uploading bytes for object key: %s", object_key)
        raise S3UploadException(object_key) from exc

    except Exception as exc:
        logger.exception("Error uploading bytes for object key: %s", object_key)
        raise S3UploadException(object_key) from exc


async def download_file(
    object_key: str,
    file_path: str,
) -> None:
    """
    Download an S3 object to the local filesystem.

    Args:
        object_key:
            S3 object key.

        file_path:
            Destination path on the local filesystem.
    """
    _validate_object_key(object_key)

    if not file_path:
        raise S3DownloadException(object_key)

    s3_client = get_s3_client()

    try:
        await s3_client.download_file(
            Bucket=settings.AWS_S3_BUCKET,
            Key=object_key,
            Filename=file_path,
        )

    except ClientError as exc:
        if _is_file_not_found_error(exc):
            logger.exception("File not found for object key: %s", object_key)
            raise S3FileNotFoundException(object_key) from exc

        logger.exception("Error downloading file for object key: %s", object_key)
        raise S3DownloadException(object_key) from exc

    except Exception as exc:
        logger.exception("Error downloading file for object key: %s", object_key)
        raise S3DownloadException(object_key) from exc


async def download_bytes(
    object_key: str,
) -> bytes:
    """
    Download an S3 object and return its complete contents as bytes.

    WARNING:
        The complete file is loaded into application memory.

    Use stream_file() when downloading potentially large files
    directly to a client.
    """
    _validate_object_key(object_key)

    s3_client = get_s3_client()

    try:
        response = await s3_client.get_object(
            Bucket=settings.AWS_S3_BUCKET,
            Key=object_key,
        )

        body = response["Body"]

        try:
            return await body.read()

        finally:
            body.close()

    except ClientError as exc:
        if _is_file_not_found_error(exc):
            logger.exception("File not found for object key: %s", object_key)
            raise S3FileNotFoundException(object_key) from exc

        logger.exception("Error downloading bytes for object key: %s", object_key)
        raise S3DownloadException(object_key) from exc

    except Exception as exc:
        logger.exception("Error downloading bytes for object key: %s", object_key)
        raise S3DownloadException(object_key) from exc


async def stream_file(
    object_key: str,
    chunk_size: int = 1024 * 1024,
) -> AsyncIterator[bytes]:
    """
    Asynchronously stream an S3 object in chunks.

    The complete file is never loaded into application memory.

    Args:
        object_key:
            S3 object key.

        chunk_size:
            Number of bytes to read per iteration.

            Default:
                1 MB

    Yields:
        Individual chunks of the S3 object.

    Intended usage:

        StreamingResponse(
            stream_file(object_key),
            media_type="application/pdf",
        )
    """
    _validate_object_key(object_key)

    if chunk_size <= 0:
        raise S3StreamException(object_key)

    s3_client = get_s3_client()

    body = None

    try:
        response = await s3_client.get_object(
            Bucket=settings.AWS_S3_BUCKET,
            Key=object_key,
        )

        body = response["Body"]

        while True:
            chunk = await body.read(chunk_size)

            if not chunk:
                break

            yield chunk

    except ClientError as exc:
        if _is_file_not_found_error(exc):
            logger.exception("File not found for streaming object key: %s", object_key)
            raise S3FileNotFoundException(object_key) from exc

        logger.exception("Error streaming file for object key: %s", object_key)
        raise S3StreamException(object_key) from exc

    except Exception as exc:
        logger.exception("Error streaming file for object key: %s", object_key)
        raise S3StreamException(object_key) from exc

    finally:
        if body is not None:
            body.close()


async def get_file_metadata(
    object_key: str,
) -> dict:
    """
    Retrieve metadata for an S3 object without downloading
    the object contents.

    Returns metadata such as:

        ContentType
        ContentLength
        Metadata
        LastModified
        ETag
    """
    _validate_object_key(object_key)

    s3_client = get_s3_client()

    try:
        response = await s3_client.head_object(
            Bucket=settings.AWS_S3_BUCKET,
            Key=object_key,
        )

        return response

    except ClientError as exc:
        if _is_file_not_found_error(exc):
            logger.exception("Error getting file metadata for object key: %s", object_key)
            raise S3FileNotFoundException(object_key) from exc
        logger.exception("Error getting file metadata for object key: %s", object_key)
        raise S3DownloadException(object_key) from exc

    except Exception as exc:
        logger.exception("Error getting file metadata for object key: %s", object_key)
        raise S3DownloadException(object_key) from exc


async def delete_file(
    object_key: str,
) -> None:
    """
    Delete an object from S3.
    """
    _validate_object_key(object_key)

    s3_client = get_s3_client()

    try:
        await s3_client.delete_object(
            Bucket=settings.AWS_S3_BUCKET,
            Key=object_key,
        )

    except ClientError as exc:
        logger.exception("Error deleting file for object key: %s", object_key)
        raise S3DeleteException(object_key) from exc

    except Exception as exc:
        logger.exception("Error deleting file for object key: %s", object_key)
        raise S3DeleteException(object_key) from exc


async def file_exists(
    object_key: str,
) -> bool:
    """
    Check whether an object exists in S3.

    Returns:
        True:
            Object exists.

        False:
            Object does not exist.

    Raises:
        S3FileExistsCheckException:
            If S3 returns an unexpected error while checking
            the object's existence.
    """
    _validate_object_key(object_key)

    s3_client = get_s3_client()

    try:
        await s3_client.head_object(
            Bucket=settings.AWS_S3_BUCKET,
            Key=object_key,
        )

        return True

    except ClientError as exc:
        if _is_file_not_found_error(exc):
            return False
        logger.exception("Error checking if file exists for object key: %s", object_key)
        raise S3FileExistsCheckException(object_key) from exc

    except Exception as exc:
        logger.exception("Error checking if file exists for object key: %s", object_key)
        raise S3FileExistsCheckException(object_key) from exc


def generate_presigned_url(
    object_key: str,
    expiration: int = 3600,
    http_method: str = "get_object",
) -> str:
    """
    Generate a temporary presigned URL.

    This operation does not require an S3 network request.
    Therefore, it remains synchronous.

    Args:
        object_key:
            S3 object key.

        expiration:
            URL validity duration in seconds.

        http_method:
            S3 operation for which the URL is generated.

            Usually:
                - get_object
                - put_object

    Returns:
        Presigned S3 URL.
    """
    _validate_object_key(object_key)

    if expiration <= 0:
        raise S3PresignedUrlException(object_key)

    if http_method not in ("get_object", "put_object"):
        raise S3PresignedUrlException(object_key)

    s3_client = get_s3_client()

    try:
        return s3_client.generate_presigned_url(
            ClientMethod=http_method,
            Params={
                "Bucket": settings.AWS_S3_BUCKET,
                "Key": object_key,
            },
            ExpiresIn=expiration,
        )

    except Exception as exc:
        logger.exception("Error generating presigned URL for object key: %s", object_key)
        raise S3PresignedUrlException(object_key) from exc