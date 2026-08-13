"""Added TL assignment columns to pipeline opportunity resource

RECONSTRUCTED. The original file for this revision was never committed and is
not recoverable, but the live DB is stamped at it. The DDL below was recovered
by diffing the live schema and is an exact match for what is in the database:
three nullable columns on pipeline_opportunity_resource plus the FK on
assigned_to_tl_by. No model describes these columns - see
app/.docs/plans/legacy-role-protection.md before dropping or keeping them.

Revision ID: 5de82cc586ab
Revises: 9232aa10c0ce
Create Date: unknown - reconstructed 2026-08-13

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '5de82cc586ab'
down_revision: Union[str, None] = '9232aa10c0ce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('pipeline_opportunity_resource', sa.Column('role', sa.String(length=255), nullable=True))
    op.add_column('pipeline_opportunity_resource', sa.Column('candidate_name', sa.String(length=255), nullable=True))
    op.add_column('pipeline_opportunity_resource', sa.Column('assigned_to_tl_by', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        'pipeline_opportunity_resource_assigned_to_tl_by_fkey',
        'pipeline_opportunity_resource',
        'users',
        ['assigned_to_tl_by'],
        ['user_id'],
        ondelete='SET NULL',
    )


def downgrade() -> None:
    op.drop_constraint(
        'pipeline_opportunity_resource_assigned_to_tl_by_fkey',
        'pipeline_opportunity_resource',
        type_='foreignkey',
    )
    op.drop_column('pipeline_opportunity_resource', 'assigned_to_tl_by')
    op.drop_column('pipeline_opportunity_resource', 'candidate_name')
    op.drop_column('pipeline_opportunity_resource', 'role')
