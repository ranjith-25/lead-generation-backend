import logging
from typing import Any

from app.exceptions.notification import NotificationTypeNotConfiguredException
from app.schemas.notification import NotificationContentBase, NotificationType
from app.config import NOTIFICATION_CONTENT, NOTIFICATION_NAVIGATION, NOTIFICATION_TYPE_NAVIGATION


class _SafeContext(dict):
    """Keeps template rendering forgiving — missing or None placeholders become empty strings."""

    def __getitem__(self, key):
        value = super().__getitem__(key)
        if value is None:
            return ""
        return value

    def __missing__(self, key):
        logging.warning(f"Missing notification template placeholder: {key}")
        return ""


def _render(template: str | None, context: dict[str, Any]) -> str | None:
    if not template:
        return template
    try:
        return template.format_map(_SafeContext(context))
    except (IndexError, ValueError):
        # Braces that are not placeholders (json snippets, css, …) — keep the raw template.
        logging.warning("Could not render notification template, using it as-is")
        return template


def _resolve_navigation_url(notification_type: NotificationType, context: dict[str, Any]) -> str | None:
    """notification type -> page key (NOTIFICATION_TYPE_NAVIGATION) -> link (NOTIFICATION_NAVIGATION)."""
    page_key = NOTIFICATION_TYPE_NAVIGATION.get(notification_type.value)

    if not page_key:
        # Deliberately unnavigable notification type — not a misconfiguration. Logged at
        # debug so the next genuinely missing mapping is findable without crying wolf.
        logging.debug(
            f"Notifications type {notification_type.value} has no navigation page configured"
        )
        return None

    link = NOTIFICATION_NAVIGATION.get(page_key)

    if not link:
        logging.warning(
            f"Notifications type {notification_type.value} points at unknown navigation page: {page_key}"
        )
        return None

    return _render(link, context)


def build_notification_content(content: NotificationContentBase) -> dict:
    notification_type = content.notification_type
    configured = NOTIFICATION_CONTENT.get(notification_type.value)

    if configured is None:
        raise NotificationTypeNotConfiguredException(notification_type.value)

    title = content.title or _render(configured.get("title", ""), content.context)
    body = content.body or _render(configured.get("body", ""), content.context)
    url = content.url or _resolve_navigation_url(notification_type, content.context)

    return {
        "notification_type": notification_type,
        "title": title or "",
        "body": body or "",
        "url": url,
        "created_by": content.created_by,
        "updated_by": content.created_by,
    }
