"""add assigned_to_tl approval status

Revision ID: df39bb697e6c
Revises: 0298fd5f596e
Create Date: 2026-08-14 08:58:59.956861

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'df39bb697e6c'
down_revision: Union[str, None] = '0298fd5f596e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TYPE approvalstatus ADD VALUE IF NOT EXISTS 'ASSIGNED_TO_TL'"
    )


def downgrade() -> None:
    pass
