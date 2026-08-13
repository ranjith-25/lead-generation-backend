import asyncio
import logging

import asyncpg

from app.core.settings import settings
from app.services.notification_stream import NOTIFICATION_CHANNEL, handle_channel_message

logger = logging.getLogger(__name__)

# Deliberately outside the SQLAlchemy pool. LISTEN owns its connection for the whole life
# of the process, and this app's ceiling is DB_POOL_SIZE + DB_MAX_OVERFLOW — borrowing one
# permanently would starve request handling.
_connection: asyncpg.Connection | None = None
_supervisor: asyncio.Task | None = None

_RECONNECT_BACKOFF_SECONDS = (1, 2, 5, 10, 30)

# A dropped TCP connection does not always flip `is_closed()`, so prove liveness instead.
_HEALTHCHECK_SECONDS = 30


def _asyncpg_dsn() -> str:
    # SQLAlchemy's driver-qualified URL is not a libpq DSN; asyncpg rejects the "+asyncpg".
    return settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://", 1)


def _on_notify(connection, pid, channel, payload) -> None:
    handle_channel_message(payload)


async def _close_connection() -> None:
    global _connection

    if _connection is None:
        return

    try:
        await _connection.close()
    except Exception:
        logger.warning("Notification listener connection did not close cleanly")
    finally:
        _connection = None


async def _listen_forever() -> None:
    """Hold one LISTEN connection open, reconnecting for as long as the app runs."""
    global _connection

    attempt = 0

    while True:
        try:
            _connection = await asyncpg.connect(_asyncpg_dsn())
            await _connection.add_listener(NOTIFICATION_CHANNEL, _on_notify)
            attempt = 0
            logger.info("Listening on Postgres channel '%s'", NOTIFICATION_CHANNEL)

            # asyncpg dispatches the callback from its own reader task; this loop exists
            # only to notice the connection dying so the backoff below can rebuild it.
            while True:
                await asyncio.sleep(_HEALTHCHECK_SECONDS)
                await _connection.execute("SELECT 1")
        except asyncio.CancelledError:
            await _close_connection()
            raise
        except Exception:
            await _close_connection()
            delay = _RECONNECT_BACKOFF_SECONDS[
                min(attempt, len(_RECONNECT_BACKOFF_SECONDS) - 1)
            ]
            attempt += 1
            logger.exception(
                "Notification listener dropped — reconnecting in %ss", delay
            )
            await asyncio.sleep(delay)


async def connect_notification_listener() -> None:
    global _supervisor

    if _supervisor is not None:
        return

    _supervisor = asyncio.create_task(_listen_forever())


async def disconnect_notification_listener() -> None:
    global _supervisor

    if _supervisor is None:
        return

    _supervisor.cancel()

    try:
        await _supervisor
    except asyncio.CancelledError:
        pass
    finally:
        _supervisor = None
