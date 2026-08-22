import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import APP_CONFIG_DEFAULTS, AppConfigKey
from app.models.app_config import AppConfig


async def get_config_value(db: AsyncSession, key: AppConfigKey) -> Any:
    """One tunable, read fresh from `app_config`.

    Falls back to `APP_CONFIG_DEFAULTS[key]` and logs a warning when the row is absent, so a
    database that has not had the migration applied — or one where a row was deleted by hand —
    keeps working on the value the code shipped with rather than failing password reset or
    scraping outright.

    Deliberately uncached. Both callers are low-frequency (once per OTP submission, once per
    scrape) and already issue several queries, so a lookup on a two-row table costs nothing
    measurable — while a cache would reintroduce the restart these values were moved into the
    database to avoid.
    """
    try:
        result = await db.execute(
            select(AppConfig.config_value).where(AppConfig.config_key == key.value)
        )
        value = result.scalars().first()
    except SQLAlchemyError:
        logging.exception("Could not read app_config for key: %s", key.value)
        raise

    if value is None:
        logging.warning(
            "No app_config row for %r - using the built-in default %r",
            key.value,
            APP_CONFIG_DEFAULTS[key],
        )
        return APP_CONFIG_DEFAULTS[key]

    return value
