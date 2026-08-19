import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config import PageName
from app.models.base import Base
from app.models.user import User


class Comment(Base):
    """One comment on one of the three commentable pages. A reply is the same row with
    `parent_comment_id` set — the service caps nesting at one level, so a reply to a reply
    re-points at the top-level comment rather than growing a tree."""

    __tablename__ = "comments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    # The existing `page_name` PostgreSQL type, shared with opportunity_edit_history. New
    # members reach the type through an ALTER TYPE migration, never through SQLAlchemy.
    page_name: Mapped[PageName] = mapped_column(
        Enum(PageName, name="page_name"),
        nullable=False,
    )

    # Deliberately no ForeignKey: this addresses a row in one of three tables — opportunities,
    # pipeline_opportunity_resource or pipeline_opportunity_technical_preperation — depending
    # on `page_name`, and no single constraint can express that. What normally makes a
    # polymorphic key dangerous is orphan rows; that does not apply here, because
    # `opportunity_id` below is a real cascading FK and all three parents already hang off
    # `opportunities`. Deleting an opportunity therefore reaps its comments on every page
    # without a trigger or an application-level sweep.
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    # Always populated, resolved from the entity at write time. This is the cleanup guarantee.
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("opportunities.opportunityID", ondelete="CASCADE"),
        nullable=False,
    )

    # CASCADE here only serves the opportunity-level reap, where the whole thread is going
    # anyway. Deleting a single parent is a soft delete, so its replies survive it.
    parent_comment_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("comments.id", ondelete="CASCADE"),
        nullable=True,
    )

    comment: Mapped[str] = mapped_column(Text, nullable=False)

    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="SET NULL"),
        nullable=True,
    )

    # Snapshot of the author's name as it read when the comment was written, for the same
    # reason as OpportunityEditHistory.edited_by_name: the FK goes null on a soft delete and
    # User.fullName follows later renames. A thread must show who said it at the time.
    created_by_name: Mapped[str] = mapped_column(String(255), nullable=False)

    is_edited: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=text("false"), nullable=False
    )

    is_deleted: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=text("false"), nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # Null until the first edit — no server_default, so "never edited" stays distinguishable.
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )

    author: Mapped["User | None"] = relationship(
        "User", foreign_keys=[created_by], lazy="selectin"
    )

    # `lazy="noload"` on purpose: nothing reads a comment's parent, and a second selectin
    # across a self-referential pair would have each reply re-load the parent that just
    # loaded it. It exists so `replies` has a `back_populates` partner and so the
    # adjacency-list direction is stated explicitly by `remote_side`.
    parent: Mapped["Comment | None"] = relationship(
        "Comment",
        remote_side=[id],
        back_populates="replies",
        lazy="noload",
    )

    # Oldest first: a thread reads top-down, unlike the top-level list which is newest first.
    # `passive_deletes` defers to the ON DELETE CASCADE above instead of nulling the FK.
    replies: Mapped[list["Comment"]] = relationship(
        "Comment",
        back_populates="parent",
        order_by="Comment.created_at",
        lazy="selectin",
        passive_deletes=True,
    )

    __table_args__ = (
        # The list query: one page's comments for one row, ordered by time.
        Index(
            "ix_comments_page_name_entity_id_created_at",
            "page_name",
            "entity_id",
            "created_at",
        ),
        # Reply fan-out: every reply for a whole page of parents in one query.
        Index("ix_comments_parent_comment_id", "parent_comment_id"),
        # The FK cascade, and cross-page reads of one opportunity's comments later.
        Index("ix_comments_opportunity_id", "opportunity_id"),
    )
