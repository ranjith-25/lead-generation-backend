from datetime import datetime
from typing import Any

import uuid
from sqlalchemy import DateTime, String, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AppConfig(Base):
    """Runtime tunables, changed with an UPDATE rather than a deploy.

    Holds values the application reads at request time and nothing else — not row
    identities. A row naming another table's row (a role or status by display name) belongs
    on that table as a `*_key` column instead; see
    app/.docs/plans/system-row-references.md.

    Keys are declared in `AppConfigKey` (app/config/system_keys.py) and read through
    `get_config_value` (app/services/db/app_config.py), which falls back to a code default
    when a row is absent.
    """

    __tablename__ = "app_config"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )

    config_key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    # JSONB rather than text plus a type column: the stored values are a number and an
    # array, and JSONB round-trips both without the reader parsing anything.
    config_value: Mapped[Any] = mapped_column(JSONB, nullable=False)

    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
