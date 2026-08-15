"""add opportunity_edit_history table

Revision ID: e3f7a1c65b04
Revises: c47f1a9d3b62
Create Date: 2026-08-15 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'e3f7a1c65b04'
down_revision: Union[str, None] = 'c47f1a9d3b62'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


page_name_enum = postgresql.ENUM(
    "OPPORTUNITY_ANALYSIS",
    name="page_name",
    create_type=False,
)


def upgrade() -> None:
    # Create PostgreSQL ENUM type first
    page_name_enum.create(op.get_bind(), checkfirst=True)

    op.create_table('opportunity_edit_history',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('opportunity_id', sa.UUID(), nullable=False),
    sa.Column('page_name', page_name_enum, nullable=False),
    sa.Column('edited_by', sa.UUID(), nullable=True),
    sa.Column('edited_by_name', sa.String(length=255), nullable=False),
    sa.Column('changes', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('edited_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['edited_by'], ['users.user_id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['opportunity_id'], ['opportunities.opportunityID'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_opportunity_edit_history_id'), 'opportunity_edit_history', ['id'], unique=False)
    op.create_index(op.f('ix_opportunity_edit_history_opportunity_id'), 'opportunity_edit_history', ['opportunity_id'], unique=False)
    op.create_index(op.f('ix_opportunity_edit_history_page_name'), 'opportunity_edit_history', ['page_name'], unique=False)
    op.create_index(op.f('ix_opportunity_edit_history_edited_by'), 'opportunity_edit_history', ['edited_by'], unique=False)
    op.create_index(op.f('ix_opportunity_edit_history_edited_at'), 'opportunity_edit_history', ['edited_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_opportunity_edit_history_edited_at'), table_name='opportunity_edit_history')
    op.drop_index(op.f('ix_opportunity_edit_history_edited_by'), table_name='opportunity_edit_history')
    op.drop_index(op.f('ix_opportunity_edit_history_page_name'), table_name='opportunity_edit_history')
    op.drop_index(op.f('ix_opportunity_edit_history_opportunity_id'), table_name='opportunity_edit_history')
    op.drop_index(op.f('ix_opportunity_edit_history_id'), table_name='opportunity_edit_history')
    op.drop_table('opportunity_edit_history')

    # Drop PostgreSQL ENUM
    page_name_enum.drop(op.get_bind(), checkfirst=True)
