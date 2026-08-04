from sqlalchemy import ForeignKey, DateTime, func , Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
import sqlalchemy as sa
from app.models.base import Base


class RolePermission(Base):
    __tablename__ = "rolePermissions"

    role_permission_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    isDeleted : Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        server_default= sa.false()
    )

    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.role_id"),
        nullable=False
    )

    feature_id: Mapped[int] = mapped_column(
        ForeignKey("features.feature_id"),
        nullable=False
    )
    
    permission_id: Mapped[int] = mapped_column(
        ForeignKey("permissions.permission_id"),
        nullable=False
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now()
    )

    # Relationships
    role = relationship("Role", back_populates="role_permissions")
    module = relationship("Feature")
    permission = relationship("Permission")