import asyncio
import json
import logging
from collections import defaultdict
from typing import Any, AsyncIterator
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.notification import NotificationRead

logger = logging.getLogger(__name__)

# The Postgres channel the emitting request and every worker's listener agree on.
NOTIFICATION_CHANNEL = "notifications_stream"

# pg_notify caps a payload at 8000 bytes. A recipient pair costs ~80 bytes of JSON, so
# 40 per message leaves generous room for the rendered title/body alongside it.
_RECIPIENTS_PER_MESSAGE = 40

# A browser that stops reading must not grow this process without bound.
_QUEUE_MAX_SIZE = 50

# user_id -> the queues of every stream this worker is currently holding for them.
# One user legitimately has several: a second tab, a second device.
_subscribers: dict[UUID, set[asyncio.Queue]] = defaultdict(set)


def subscribe(user_id: UUID) -> asyncio.Queue:
    queue: asyncio.Queue = asyncio.Queue(maxsize=_QUEUE_MAX_SIZE)
    _subscribers[user_id].add(queue)
    return queue


def unsubscribe(user_id: UUID, queue: asyncio.Queue) -> None:
    listeners = _subscribers.get(user_id)

    if not listeners:
        return

    listeners.discard(queue)

    if not listeners:
        # Without this the defaultdict keeps an empty set per user who ever connected.
        _subscribers.pop(user_id, None)


def connected_user_count() -> int:
    """Streams held by *this* worker — useful for a health endpoint, not a global count."""
    return len(_subscribers)


def _deliver_local(user_id: UUID, payload: dict[str, Any]) -> None:
    for queue in list(_subscribers.get(user_id, ())):
        try:
            queue.put_nowait(payload)
        except asyncio.QueueFull:
            # Dropping is the right call: the row is already persisted and the client
            # refetches on reconnect, so the worst case is a missing toast, not lost data.
            logger.warning("Dropped a streamed notification for %s — queue full", user_id)


def handle_channel_message(raw_payload: str) -> None:
    """Called by the Postgres listener; hands each recipient this worker holds their copy."""
    try:
        message = json.loads(raw_payload)
        content = message["content"]

        for user_id, notification_id in message["recipients"]:
            _deliver_local(
                UUID(user_id),
                {**content, "id": notification_id, "user_id": user_id},
            )
    except Exception:
        logger.exception("Malformed notification stream payload")


async def publish_notifications(
    db: AsyncSession, notifications: list[NotificationRead]
) -> None:
    """Announce freshly persisted notifications to every worker over LISTEN/NOTIFY.

    Rows created in one request have to reach streams held by *other* uvicorn workers, so
    the fan-out goes through Postgres rather than this process's `_subscribers` map.

    Deliberately swallows its own failures: the notification is already committed, and a
    missed toast must never turn the business action that raised it into a 500.
    """
    if not notifications:
        return

    try:
        # Bulk creates share one rendered title/body across many rows — send the content
        # once and list the recipients, rather than repeating it per user.
        grouped: dict[tuple, list[NotificationRead]] = defaultdict(list)

        for notification in notifications:
            grouped[
                (
                    notification.notification_type,
                    notification.title,
                    notification.body,
                    notification.url,
                )
            ].append(notification)

        for (notification_type, title, body, url), group in grouped.items():
            content = {
                "notification_type": notification_type.value,
                "title": title,
                "body": body,
                "url": url,
                "created_at": group[0].created_at.isoformat(),
            }

            for start in range(0, len(group), _RECIPIENTS_PER_MESSAGE):
                chunk = group[start : start + _RECIPIENTS_PER_MESSAGE]
                payload = json.dumps(
                    {
                        "content": content,
                        "recipients": [
                            [str(item.user_id), str(item.id)] for item in chunk
                        ],
                    }
                )
                await db.execute(
                    text("SELECT pg_notify(:channel, :payload)"),
                    {"channel": NOTIFICATION_CHANNEL, "payload": payload},
                )

        # NOTIFY is only delivered when its transaction commits, and the insert above
        # already committed — this closes the transaction the execute() just opened.
        await db.commit()
    except Exception:
        await db.rollback()
        logger.exception("Could not publish notifications to the stream channel")


async def notification_events(
    user_id: UUID, keepalive_seconds: float
) -> AsyncIterator[dict[str, Any] | None]:
    """Yield each notification for `user_id`, or `None` when the keepalive window lapses.

    The `None` tick is what lets the caller write a comment frame: it keeps proxies from
    culling an idle stream, and the failed write is how a vanished client is detected.
    """
    queue = subscribe(user_id)

    try:
        while True:
            try:
                yield await asyncio.wait_for(queue.get(), timeout=keepalive_seconds)
            except asyncio.TimeoutError:
                yield None
    finally:
        unsubscribe(user_id, queue)
