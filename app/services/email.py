import logging
from email.message import EmailMessage

from app.core.settings import settings
from app.exceptions.auth import EmailSendFailedException

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

    message = EmailMessage()
    message["From"] = settings.EMAIL_FROM or settings.SMTP_USER
    message["To"] = email
    message["Subject"] = "Your password reset code"
    message.set_content(
        f"Your password reset code is {otp}.\n\n"
        f"It expires in {settings.OTP_EXPIRE_MINUTES} minutes. "
        "If you did not request this, please ignore this email."
    )

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER or None,
            password=settings.SMTP_PASSWORD or None,
            # use_tls=not settings.SMTP_USE_TLS,
            # start_tls=settings.SMTP_USE_TLS,
            use_tls=False,
            start_tls=True
        )
    except Exception as e:
        print("Error:     ",e)
        logger.exception("Could not send the password reset OTP to %s", email)
        raise EmailSendFailedException()
