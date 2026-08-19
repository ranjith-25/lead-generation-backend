"""add comments table

Revision ID: e5c13f4d9f32
Revises: d4b02e3c8e21
Create Date: 2026-08-19 00:00:01.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'e5c13f4d9f32'
down_revision: Union[str, None] = 'd4b02e3c8e21'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# The type already exists (created at e3f7a1c65b04, extended at d4b02e3c8e21) — create_type
# False keeps this migration from trying to build a second one.
page_name_enum = postgresql.ENUM(
    "OPPORTUNITY_ANALYSIS",
    "RESOURCE_MATCH",
    "TECHNICAL_PREPARATION",
    name="page_name",
    create_type=False,
)


# Backfills the legacy technical-preparation comments — a JSON array of bare strings with no
# author and no per-item timestamp — into the new table, one row per element.
#
#   * created_by NULL / created_by_name 'Unknown User': the column stored no author, so there
#     is nothing to attribute these to.
#   * WITH ORDINALITY plus a per-element microsecond offset: every element of one row shares
#     that row's "createdAt", and the list query orders by created_at. Without the offset the
#     original array order would be lost to an arbitrary tie-break on the first read.
#   * The source column is left as it is. Nothing empties it, so a downgrade loses only
#     comments written after this migration (C-D6).
BACKFILL_TECH_PREP_COMMENTS = """
INSERT INTO comments (
    id,
    page_name,
    entity_id,
    opportunity_id,
    parent_comment_id,
    comment,
    created_by,
    created_by_name,
    is_edited,
    is_deleted,
    created_at
)
SELECT
    gen_random_uuid(),
    'TECHNICAL_PREPARATION'::page_name,
    tp.id,
    tp.opportunity_id,
    NULL,
    element.value #>> '{}',
    NULL,
    'Unknown User',
    false,
    false,
    tp."createdAt" + ((element.ord - 1) * INTERVAL '1 microsecond')
FROM pipeline_opportunity_technical_preperation AS tp
CROSS JOIN LATERAL jsonb_array_elements(
    -- The CASE, not a WHERE clause, is what skips null and non-array values: WHERE is
    -- applied after the set-returning function has already run, so a non-array would raise
    -- before it could be filtered out. An empty array yields no rows and the CROSS JOIN
    -- then drops the parent row, which is exactly the wanted "skip empty" behaviour.
    CASE
        WHEN jsonb_typeof(tp.comments::jsonb) = 'array' THEN tp.comments::jsonb
        ELSE '[]'::jsonb
    END
) WITH ORDINALITY AS element(value, ord)
WHERE NULLIF(BTRIM(element.value #>> '{}'), '') IS NOT NULL
"""


def upgrade() -> None:
    op.create_table('comments',
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('page_name', page_name_enum, nullable=False),
    # No foreign key on purpose: entity_id addresses opportunities,
    # pipeline_opportunity_resource or pipeline_opportunity_technical_preperation depending on
    # page_name. opportunity_id below is the real cascading key that keeps the table clean.
    sa.Column('entity_id', sa.UUID(), nullable=False),
    sa.Column('opportunity_id', sa.UUID(), nullable=False),
    sa.Column('parent_comment_id', sa.UUID(), nullable=True),
    sa.Column('comment', sa.Text(), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('created_by_name', sa.String(length=255), nullable=False),
    sa.Column('is_edited', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['users.user_id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['opportunity_id'], ['opportunities.opportunityID'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['parent_comment_id'], ['comments.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_comments_page_name_entity_id_created_at', 'comments', ['page_name', 'entity_id', 'created_at'], unique=False)
    op.create_index('ix_comments_parent_comment_id', 'comments', ['parent_comment_id'], unique=False)
    op.create_index('ix_comments_opportunity_id', 'comments', ['opportunity_id'], unique=False)

    op.execute(BACKFILL_TECH_PREP_COMMENTS)


def downgrade() -> None:
    op.drop_index('ix_comments_opportunity_id', table_name='comments')
    op.drop_index('ix_comments_parent_comment_id', table_name='comments')
    op.drop_index('ix_comments_page_name_entity_id_created_at', table_name='comments')
    op.drop_table('comments')

    # page_name is not dropped: it predates this revision and opportunity_edit_history still
    # uses it. The legacy technical-preparation array column was never emptied, so the
    # backfilled comments survive this downgrade in their original home.
