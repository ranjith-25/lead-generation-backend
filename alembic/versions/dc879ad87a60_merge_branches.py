"""merge branches

Revision ID: dc879ad87a60
Revises: 49bcb3987397, fe761be02bab
Create Date: 2026-08-04 16:56:14.262745

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dc879ad87a60'
down_revision: Union[str, None] = ('49bcb3987397', 'fe761be02bab')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
