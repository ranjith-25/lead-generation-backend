"""Forgiving `str.format` rendering for the copy held in `app/config/` and `app/templates/`.

Shared by the notification builder and the email sender. Both render administrator-visible
copy where a template defect must not fail the request that triggered it: a notification is
better delivered with a blank placeholder than not at all, and a password-reset email is
better sent with one field missing than swallowed by a 500.

Imports stdlib only, so it stays safe to import from anywhere in the service layer.
"""

import logging
from typing import Any


class _SafeContext(dict):
    """Keeps template rendering forgiving — missing or None placeholders become empty strings."""

    def __getitem__(self, key):
        value = super().__getitem__(key)
        if value is None:
            return ""
        return value

    def __missing__(self, key):
        logging.warning(f"Missing template placeholder: {key}")
        return ""


def render(template: str | None, context: dict[str, Any]) -> str | None:
    """Substitute `{placeholder}` values, degrading rather than raising.

    A missing or None placeholder becomes an empty string. A literal brace that is not a
    placeholder — a CSS block or `@media` query added to one of the HTML templates, a JSON
    snippet — makes `format_map` raise, and the raw template is returned instead. That path
    is why the email templates can be edited as ordinary HTML files without a stray brace
    turning into a 500 on user-invite or password-reset.
    """
    if not template:
        return template
    try:
        return template.format_map(_SafeContext(context))
    except (IndexError, ValueError):
        logging.warning("Could not render template, using it as-is")
        return template
