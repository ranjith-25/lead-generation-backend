from datetime import datetime
from typing import Optional

import uuid
from sqlalchemy import (
    String,
    DateTime,
    ForeignKey,func,text
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Feature(Base):
    __tablename__ = "features"

    feature_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )

    feature_key: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False
    )

    display_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    description : Mapped[str] =  mapped_column(
        String(255),
        nullable=True
    )

    parent_feature_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("features.feature_id"),
        nullable=True
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now()
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )

    parent: Mapped["Feature"] = relationship(
        remote_side=[feature_id],
        back_populates="children"
    )

    children: Mapped[list["Feature"]] = relationship(
        back_populates="parent"
    )