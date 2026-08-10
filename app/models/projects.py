from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

import uuid
from sqlalchemy import DateTime, func, String,ForeignKey, text  , Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.project_domains import ProjectDomain
    from app.models.techstacks import TechStacks

class Projects(Base):
    __tablename__= 'projects'

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )
    project_name: Mapped[str] = mapped_column(
        String(255),
        unique=True,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    
    is_draft: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
        server_default=text("true")
    )

    # free-form label -> URL map: a column per link type would mean a migration every time
    # the business wants to record a new kind of link
    links: Mapped[dict[str, str]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default=text("'{}'::jsonb")
    )

    # only the location of the uploaded document lives in the DB; the bytes sit under
    # settings.CASE_STUDY_DIR
    case_study: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )

    projectDomainID: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("project_domains.id", ondelete="RESTRICT"),
        nullable=False
    )

    projectDomain: Mapped["ProjectDomain"] = relationship(
        back_populates="projects",
        lazy="selectin"
    )

    techstacks: Mapped[List["TechStacks"]] = relationship(
        secondary="project_techstacks",
        back_populates="projects",
        lazy="selectin"
    )

    createdAt: Mapped[datetime] = mapped_column(
            DateTime,
            server_default=func.now()
        )

    updatedAt: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )
