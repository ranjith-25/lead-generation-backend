from typing import BinaryIO
from botocore.exceptions import ClientError

from app.core.settings import settings
from app.core.s3_connection import get_s3_client


def upload_fileobj(
    file_obj: BinaryIO,
    object_key: str,
    content_type: str | None = None,
) -> str:
    """
    Stream a file-like object (e.g. upload_profile.file from FastAPI) directly to S3.
    Prevents high RAM usage on t3.micro.
    """
    s3_client = get_s3_client()
    extra_args = {}
    if content_type:
        extra_args["ContentType"] = content_type

    s3_client.upload_fileobj(
        Fileobj=file_obj,
        Bucket=settings.AWS_S3_BUCKET,
        Key=object_key,
        ExtraArgs=extra_args if extra_args else None,
    )
    return object_key


def upload_file(
    file_path: str,
    object_key: str,
    content_type: str | None = None,
) -> str:
    """
    Upload an existing local file from disk to S3.
    """
    s3_client = get_s3_client()
    extra_args = {}
    if content_type:
        extra_args["ContentType"] = content_type

    s3_client.upload_file(
        Filename=file_path,
        Bucket=settings.AWS_S3_BUCKET,
        Key=object_key,
        ExtraArgs=extra_args if extra_args else None,
    )
    return object_key


def upload_bytes(
    file_data: bytes,
    object_key: str,
    content_type: str | None = None,
) -> str:
    """
    Upload raw bytes directly to S3 (best for small payloads/thumbnails).
    """
    s3_client = get_s3_client()
    extra_args = {}
    if content_type:
        extra_args["ContentType"] = content_type

    s3_client.put_object(
        Bucket=settings.AWS_S3_BUCKET,
        Key=object_key,
        Body=file_data,
        **extra_args,
    )
    return object_key


def download_file(
    object_key: str,
    file_path: str,
) -> None:
    """
    Download an S3 object to the local filesystem.
    """
    s3_client = get_s3_client()
    s3_client.download_file(
        Bucket=settings.AWS_S3_BUCKET,
        Key=object_key,
        Filename=file_path,
    )


def download_bytes(
    object_key: str,
) -> bytes:
    """
    Download an S3 object and return its contents as bytes.
    """
    s3_client = get_s3_client()
    response = s3_client.get_object(
        Bucket=settings.AWS_S3_BUCKET,
        Key=object_key,
    )
    return response["Body"].read()


def delete_file(
    object_key: str,
) -> None:
    """
    Delete an object from S3.
    """
    s3_client = get_s3_client()
    s3_client.delete_object(
        Bucket=settings.AWS_S3_BUCKET,
        Key=object_key,
    )


def file_exists(
    object_key: str,
) -> bool:
    """
    Check whether an object exists in S3.
    """
    s3_client = get_s3_client()
    try:
        s3_client.head_object(
            Bucket=settings.AWS_S3_BUCKET,
            Key=object_key,
        )
        return True
    except ClientError as exc:
        error_code = str(exc.response.get("Error", {}).get("Code", ""))
        if error_code in ("404", "NoSuchKey", "NotFound"):
            return False
        raise


def generate_presigned_url(
    object_key: str,
    expiration: int = 3600,
    http_method: str = "get_object",
) -> str:
    """
    Generate a temporary URL for downloading (get_object) or uploading (put_object).
    """
    s3_client = get_s3_client()
    return s3_client.generate_presigned_url(
        ClientMethod=http_method,
        Params={
            "Bucket": settings.AWS_S3_BUCKET,
            "Key": object_key,
        },
        ExpiresIn=expiration,
    )