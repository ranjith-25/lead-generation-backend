import uuid
from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class UserProject(Base):
    __tablename__ = "user_projects"

    user_project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))

    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.project_id", ondelete="CASCADE"), nullable=False)

    role_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("job_roles.id", ondelete="RESTRICT"), nullable=False)

    techstack_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tech_stacks.techstack_id", ondelete="RESTRICT"), nullable=False)

    # deliberately not unique: one user is allocated to many projects, so user_id
    # repeats across rows — the surrogate user_project_id is what identifies an allocation
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)

    allocated_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)

    # nobody has revised the allocation until it is actually edited
    allocation_updated_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)

    # Allocations are never hard-deleted: `sync_bench_status` and the system log both read the
    # allocation history to explain why a user was benched, and a real DELETE would erase the
    # evidence. Matches the soft-delete flag already carried by `users` and `comments`.
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=text("false"), nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
