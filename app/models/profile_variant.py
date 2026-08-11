import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func, text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base
from app.models.job_role import JobRole
from app.models.project_domains import ProjectDomain
from app.models.projects import Projects
from app.models.user import User


class ProfileVariant(Base):
    __tablename__ = "profile_variants"

    profile_variant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    role: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("job_roles.id", ondelete="RESTRICT"), nullable=False)

    experience: Mapped[str] = mapped_column(String(255), nullable=False)

    highlighted_skills: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=False)

    upload_profile: Mapped[str] = mapped_column(String(255), nullable=False)

    certificate: Mapped[List[str] | None] = mapped_column(ARRAY(String), nullable=True)

    is_draft: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true", nullable=False)

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)

    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)

    updated_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    projects: Mapped[List["ProfileVariantProject"]] = relationship(
        "ProfileVariantProject",
        back_populates="profile_variant",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    user: Mapped["User"] = relationship("User", foreign_keys=[user_id], lazy="selectin")

    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by], lazy="selectin")

    updater: Mapped["User"] = relationship("User", foreign_keys=[updated_by], lazy="selectin")

    job_role_details: Mapped["JobRole"] = relationship("JobRole", foreign_keys=[role], lazy="selectin")

    @property
    def project_ids(self) -> List[uuid.UUID]:
        return [p.project_id for p in self.projects] if self.projects else []


class ProfileVariantProject(Base):
    __tablename__ = "profile_variant_projects"

    profile_variant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("profile_variants.profile_variant_id", ondelete="CASCADE"), primary_key=True)

    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.project_id", ondelete="CASCADE"), primary_key=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    project_name: Mapped[str] = mapped_column(String(255))

    projectDomainID: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("project_domains.id", ondelete="RESTRICT"), nullable=False)

    techstacks: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=False)

    description: Mapped[str] = mapped_column(Text, nullable=False)

    links: Mapped[dict[str, str]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default=text("'{}'::jsonb"),
    )

    # Relationships
    profile_variant: Mapped["ProfileVariant"] = relationship(
        "ProfileVariant",
        back_populates="projects",
        lazy="selectin",
    )
    project_details: Mapped["Projects"] = relationship(
        "Projects",
        foreign_keys=[project_id],
        lazy="selectin",
    )
    project_domain: Mapped["ProjectDomain"] = relationship(
        "ProjectDomain",
        foreign_keys=[projectDomainID],
        lazy="selectin",
    )