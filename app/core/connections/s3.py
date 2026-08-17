from types_aiobotocore_s3 import S3Client
import aioboto3

from app.core.settings import settings
import logging
from app.exceptions.s3_exceptions import S3ConnectionException,S3ClientNotInitializedException

s3_client: S3Client | None = None
logger = logging.getLogger(__name__)

async def connect_s3() -> None:
    """
    Initialize the asynchronous S3 client.

    This should be called when the application starts.
    """
    try : 
        global s3_client

        session = aioboto3.Session()

        s3_client = await session.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        ).__aenter__()
        logger.info("AWS S3 Connection was successful")
    except Exception as e:
        logger.exception("Failed to connect to AWS S3")
        raise S3ConnectionException from e


def get_s3_client() -> S3Client:
    """
    Return the initialized asynchronous S3 client.
    """
    if s3_client is None:
        logger.error("S3 client has not been initialized")
        raise S3ClientNotInitializedException()

    return s3_client


async def disconnect_s3() -> None:
    """
    Close the asynchronous S3 client.

    This should be called when the application shuts down.
    """
    try : 
        global s3_client

        if s3_client is not None:
            await s3_client.__aexit__(None, None, None)
            s3_client = None
    except Exception as e:
        logger.exception("Failed to disconnect from AWS S3")
        raise S3ConnectionException from e