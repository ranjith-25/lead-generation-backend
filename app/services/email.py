import logging
from functools import lru_cache
from pathlib import Path

from app.core.settings import settings
from app.exceptions.auth import EmailSendFailedException
from app.config import EMAIL_SUBJECTS
from app.services.templating import render
import aioboto3
from botocore.exceptions import ClientError, BotoCoreError
logger = logging.getLogger(__name__)

# app/services/email.py -> app/ -> app/templates/email, so the path does not depend on the
# working directory the server was started from.
_TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates" / "email"


@lru_cache(maxsize=None)
def load_email_template(filename: str) -> str:
    """One template file, read once per process.

    `encoding` is explicit and must stay that way: `read_text()` with no argument uses
    `locale.getencoding()`, which is cp1252 on a Windows host and UTF-8 in a Linux
    container — a non-ASCII character in a template would then break on one platform only.
    Reading lazily rather than at import means a missing file surfaces as a catchable
    request-time error instead of killing startup.
    """
    return (_TEMPLATE_DIR / filename).read_text(encoding="utf-8")


async def send_otp_email(email: str, otp: str) -> None:

    context = {"otp": otp, "expiry_minutes": settings.OTP_EXPIRE_MINUTES}

    text_content = render(load_email_template("otp.txt"), context)
    html_content = render(load_email_template("otp.html"), context)

    try:
        await send_mail(EMAIL_SUBJECTS["OTP"], text_content, html_content, email)
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
       