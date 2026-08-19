"""add outreach_subject to sales_enablement

Revision ID: a71c9e4d5b03
Revises: f0a3c7d21b48
Create Date: 2026-08-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a71c9e4d5b03'
down_revision: Union[str, None] = 'f0a3c7d21b48'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Nullable with no server default: every existing row predates the subject line, and an
    # empty string would be indistinguishable from one the user deliberately cleared. Text
    # rather than String(n) to match outreach_template, its neighbour on the table.
    op.add_column(
        'sales_enablement',
        sa.Column('outreach_subject', sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('sales_enablement', 'outreach_subject')
