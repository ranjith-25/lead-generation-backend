import logging

from app.core.settings import settings
from app.exceptions.auth import EmailSendFailedException
from app.config import ( 
    EMAIL_MESSAGE_CONTENT
)
import aioboto3
from botocore.exceptions import ClientError, BotoCoreError
logger = logging.getLogger(__name__)


async def send_otp_email(email: str, otp: str) -> None:
    
    template = EMAIL_MESSAGE_CONTENT["OTP_TEMPLATE"]
    
    text_content = template["text_template"].format(
        otp=otp,
        expiry_minutes=settings.OTP_EXPIRE_MINUTES
    )
    html_content = template["html_template"].format(
        otp=otp,
        expiry_minutes=settings.OTP_EXPIRE_MINUTES
    )

    try:
        await send_mail(EMAIL_MESSAGE_CONTENT["OTP_TEMPLATE"]["subject"],text_content, html_content, email)
    except Exception as e:
        logger.exception("Could not send the password reset OTP to %s", email)
        raise EmailSendFailedException()


async def send_mail(
    subject: str,
    text_content: str,
    html_content: str,
    email: str,
):
    try:
        session = aioboto3.Session()

        async with session.client(
            "ses",
            aws_access_key_id=settings.SES_ACCESS_KEY_ID,
            aws_secret_access_key=settings.SES_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        ) as ses_client:

            response = await ses_client.send_email(
                Source=settings.EMAIL_FROM,
                Destination={
                    "ToAddresses": [email],
                },
                Message={
                    "Subject": {
                        "Data": subject,
                        "Charset": "UTF-8",
                    },
                    "Body": {
                        "Text": {
                            "Data": text_content,
                            "Charset": "UTF-8",
                        },
                        "Html": {
                            "Data": html_content,
                            "Charset": "UTF-8",
                        },
                    },
                },
            )

        logger.info(
            "Email sent successfully via AWS SES. "
            "Recipient: %s, MessageId: %s",
            email,
            response.get("MessageId"),
        )

        return response

    except (ClientError, BotoCoreError):
        logger.exception(
            "AWS SES failed to send email to %s",
            email,
        )
        raise

    except Exception:
        logger.exception(
            "Unexpected error while sending email to %s",
            email,
        )
        raise
       