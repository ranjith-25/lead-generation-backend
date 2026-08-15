import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config import PageName
from app.models.base import Base
from app.models.user import User


class OpportunityEditHistory(Base):
    """One row per edit made to an opportunity, with the before/after of every field touched."""

    __tablename__ = "opportunity_edit_history"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )

    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("opportunities.opportunityID", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    page_name: Mapped[PageName] = mapped_column(
        Enum(PageName, name="page_name"),
        default=PageName.OPPORTUNITY_ANALYSIS,
        nullable=False,
        index=True,
    )

    edited_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Snapshot of the editor's name as it read at edit time. The FK above can go null when a
    # user is deleted and fullName follows later renames — history must do neither.
    edited_by_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # {field: {"old": ..., "new": ...}} — only fields whose value actually changed.
    changes: Mapped[dict] = mapped_column(JSONB, nullable=False)

    edited_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, index=True
    )

    editor: Mapped["User | None"] = relationship(
        "User", foreign_keys=[edited_by], lazy="selectin"
    )

    @property
    def editedFields(self) -> list[str]:
        return list(self.changes.keys()) if self.changes else []
