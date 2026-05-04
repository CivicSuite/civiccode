"""Add durable popular-question discovery records."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from civiccode.migrations.guards import idempotent_create_table


revision = "civiccode_0003_popular_questions"
down_revision = "civiccode_0002_sources"
branch_labels = None
depends_on = None


def _timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    ]


def upgrade() -> None:
    idempotent_create_table(
        "popular_question_records",
        sa.Column("question_id", sa.String(255), primary_key=True),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("section_id", sa.String(255), nullable=False),
        sa.Column("section_number", sa.String(120), nullable=False),
        sa.Column("section_heading", sa.String(500), nullable=False),
        sa.Column("answer_excerpt", sa.Text(), nullable=False),
        sa.Column("citation_payload", postgresql.JSONB(), nullable=False),
        sa.Column("audience", sa.String(80), nullable=False),
        sa.Column("status", sa.String(80), nullable=False),
        sa.Column("is_popular", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("approved_by", sa.String(255), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        *_timestamps(),
        schema="civiccode",
    )


def downgrade() -> None:
    op.drop_table("popular_question_records", schema="civiccode")
