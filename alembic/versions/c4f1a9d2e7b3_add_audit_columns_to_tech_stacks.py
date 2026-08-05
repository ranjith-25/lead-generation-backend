"""add ownership and audit columns to tech_stacks

Revision ID: c4f1a9d2e7b3
Revises: 35291a034c2b
Create Date: 2026-08-06 00:00:00.000000

Brings tech_stacks in line with project_domains: who added the row, who last changed it,
when, and whether it is still selectable. tech_stacks was empty when this was written, so
createdBy / updatedBy go straight in as NOT NULL with no backfill step. If the table has
rows by the time this runs, split each of those two into add-nullable -> backfill ->
alter to NOT NULL.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c4f1a9d2e7b3'
down_revision: Union[str, None] = '35291a034c2b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('tech_stacks', sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False))
    op.add_column('tech_stacks', sa.Column('createdAt', sa.DateTime(), server_default=sa.text('now()'), nullable=False))
    op.add_column('tech_stacks', sa.Column('updatedAt', sa.DateTime(), nullable=True))
    op.add_column('tech_stacks', sa.Column('createdBy', postgresql.UUID(as_uuid=True), nullable=False))
    op.add_column('tech_stacks', sa.Column('updatedBy', postgresql.UUID(as_uuid=True), nullable=False))
    op.create_foreign_key(
        'tech_stacks_createdBy_fkey', 'tech_stacks', 'users',
        ['createdBy'], ['user_id'], ondelete='CASCADE'
    )
    op.create_foreign_key(
        'tech_stacks_updatedBy_fkey', 'tech_stacks', 'users',
        ['updatedBy'], ['user_id'], ondelete='CASCADE'
    )
    # techstack_name is already UNIQUE (tech_stacks_techstack_name_key) — nothing to add


def downgrade() -> None:
    op.drop_constraint('tech_stacks_updatedBy_fkey', 'tech_stacks', type_='foreignkey')
    op.drop_constraint('tech_stacks_createdBy_fkey', 'tech_stacks', type_='foreignkey')
    op.drop_column('tech_stacks', 'updatedBy')
    op.drop_column('tech_stacks', 'createdBy')
    op.drop_column('tech_stacks', 'updatedAt')
    op.drop_column('tech_stacks', 'createdAt')
    op.drop_column('tech_stacks', 'is_active')
