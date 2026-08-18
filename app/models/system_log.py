import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config import LogAction, LogModule
from app.models.base import Base
from app.models.user import User


class SystemLog(Base):
    """One row per curated business event — who did what, in which module, and when.

    Staged with a bare `db.add()` inside the business transaction, exactly like
    `OpportunityEditHistory`, so an action cannot persist without its log row.
    """

    __tablename__ = "system_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )

    action: Mapped[LogAction] = mapped_column(
        Enum(LogAction, name="log_action"), nullable=False, index=True
    )

    module: Mapped[LogModule] = mapped_column(
        Enum(LogModule, name="log_module"), nullable=False, index=True
    )

    performed_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Snapshot of the actor's name as it read at action time. The FK above goes null when a
    # user is deleted and fullName follows later renames — history must do neither.
    performed_by_name: Mapped[str] = mapped_column(String(255), nullable=False)

    entity_type: Mapped[str | None] = mapped_column(String(100), nullable=True)

    entity_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True
    )

    # Composed at write time so the sentence still reads correctly after the entity it
    # names is renamed or deleted.
    description: Mapped[str] = mapped_column(String(500), nullable=False)

    # The rich context. Deliberately not returned by the list endpoint.
    details: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    performed_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, index=True
    )

    performer: Mapped["User | None"] = relationship(
        "User", foreign_keys=[performed_by], lazy="selectin"
    )

    __table_args__ = (
        # Every list query orders by time, and `module` is the filter most likely to narrow it.
        Index(
            "ix_system_logs_performed_at_module", text("performed_at DESC"), "module"
        ),
    )
