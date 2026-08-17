from botocore.client import BaseClient
import boto3

from app.core.settings import settings


s3_client: BaseClient | None = None


def connect_s3() -> None:
    global s3_client

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )


def get_s3_client() -> BaseClient:
    if s3_client is None:
        raise RuntimeError("S3 client has not been initialized")

    return s3_client


def disconnect_s3() -> None:
    global s3_client

    if s3_client is not None:
        s3_client.close()
        s3_client = None