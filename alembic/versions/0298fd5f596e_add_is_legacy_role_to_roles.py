"""add is_legacy_role to roles

Revision ID: 0298fd5f596e
Revises: 5de82cc586ab
Create Date: 2026-08-13 19:45:17.801913

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0298fd5f596e'
down_revision: Union[str, None] = '5de82cc586ab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'roles',
        sa.Column(
            'is_legacy_role',
            sa.Boolean(),
            server_default=sa.text('false'),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column('roles', 'is_legacy_role')
