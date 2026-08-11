import logging
from email.message import EmailMessage

from app.core.settings import settings
from app.exceptions.auth import EmailSendFailedException
from app.config import ( 
    EMAIL_MESSAGE_CONTENT
)

logger = logging.getLogger(__name__)

try:
    import aiosmtplib
except ImportError:  # pragma: no cover
    aiosmtplib = None


def _smtp_configured() -> bool:
    return bool(settings.SMTP_HOST) and aiosmtplib is not None


async def send_otp_email(email: str, otp: str) -> None:
    if not _smtp_configured():
        if settings.ENVIRONMENT == "DEV":
            logger.warning("[DEV] Password reset OTP for %s: %s", email, otp)
            return
        logger.error(
            "SMTP is not configured (or aiosmtplib is not installed) — the OTP for %s "
            "was never delivered.",
            email,
        )
        raise EmailSendFailedException()
    
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

async def send_mail(subject, text_content, html_content, email):
    try:
        message = EmailMessage()
        message["From"] = settings.EMAIL_FROM or settings.SMTP_USER
        message["To"] = email
        message["Subject"] = subject
        message.set_content(text_content)
        message.add_alternative(html_content, subtype="html")
        
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER or None,
            password=settings.SMTP_PASSWORD or None,
            use_tls=False,
            start_tls=True,
        )
    except:
        raise