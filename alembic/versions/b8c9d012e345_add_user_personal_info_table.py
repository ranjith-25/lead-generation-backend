"""Add user_personal_info table

Revision ID: b8c9d012e345
Revises: e7184806c225
Create Date: 2026-08-03 18:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b8c9d012e345'
down_revision: Union[str, None] = 'e7184806c225'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'user_personal_info',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('work_email', sa.String(length=100), nullable=False),
        sa.Column('date_of_birth', sa.String(length=10), nullable=False),
        sa.Column('primary_role', sa.String(length=100), nullable=False),
        sa.Column('branch', sa.String(length=100), nullable=False),
        sa.Column('highest_qualification', sa.String(length=100), nullable=False),
        sa.Column('specialization', sa.String(length=100), nullable=False),
        sa.Column('year_of_passout', sa.Integer(), nullable=False),
        sa.Column('working_status', sa.String(length=50), nullable=False),
        sa.Column('createdAt', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updatedAt', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )


def downgrade() -> None:
    op.drop_table('user_personal_info')
