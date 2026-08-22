"""Email subject lines.

The bodies live in `app/templates/email/` as ordinary `.html` / `.txt` files and are read
through `load_email_template` in `app/services/email.py`.

Subjects stay here rather than becoming one-line files: they carry no placeholders, and a
file read would append a trailing newline, which in an SES `Subject.Data` is a header
injection risk rather than a cosmetic difference.
"""


EMAIL_SUBJECTS = {
    "INVITATION": "You're invited to join Lead Generation",
    "OTP": "Your password reset code",
}
