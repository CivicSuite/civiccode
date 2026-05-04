"""Add durable section lifecycle records."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from civiccode.migrations.guards import idempotent_create_table


revision = "civiccode_0004_section_lifecycle"
down_revision = "civiccode_0003_popular_questions"
branch_labels = None
depends_on = None


def _created_at() -> sa.Column:
    return sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())


def upgrade() -> None:
    idempotent_create_table(
        "code_title_records",
        sa.Column("title_id", sa.String(255), primary_key=True),
        sa.Column("title_number", sa.String(80), nullable=False),
        sa.Column("title_name", sa.String(500), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default=sa.text("0")),
        _created_at(),
        schema="civiccode",
    )
    idempotent_create_table(
        "code_chapter_records",
        sa.Column("chapter_id", sa.String(255), primary_key=True),
        sa.Column("title_id", sa.String(255), nullable=False),
        sa.Column("chapter_number", sa.String(80), nullable=False),
        sa.Column("chapter_name", sa.String(500), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default=sa.text("0")),
        _created_at(),
        schema="civiccode",
    )
    idempotent_create_table(
        "code_section_records",
        sa.Column("section_id", sa.String(255), primary_key=True),
        sa.Column("chapter_id", sa.String(255), nullable=False),
        sa.Column("section_number", sa.String(120), nullable=False),
        sa.Column("section_heading", sa.String(500), nullable=False),
        sa.Column("parent_section_id", sa.String(255), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("administrative_regulation_refs", postgresql.JSONB(), nullable=False),
        sa.Column("resolution_refs", postgresql.JSONB(), nullable=False),
        sa.Column("policy_refs", postgresql.JSONB(), nullable=False),
        sa.Column("approved_summary_refs", postgresql.JSONB(), nullable=False),
        _created_at(),
        schema="civiccode",
    )
    idempotent_create_table(
        "section_version_records",
        sa.Column("version_id", sa.String(255), primary_key=True),
        sa.Column("section_id", sa.String(255), nullable=False),
        sa.Column("source_id", sa.String(255), nullable=False),
        sa.Column("version_label", sa.String(255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("effective_start", sa.Date(), nullable=False),
        sa.Column("effective_end", sa.Date(), nullable=True),
        sa.Column("status", sa.String(80), nullable=False),
        sa.Column("is_current", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("adoption_event_id", sa.String(255), nullable=True),
        sa.Column("amendment_event_id", sa.String(255), nullable=True),
        sa.Column("amendment_summary", sa.Text(), nullable=True),
        sa.Column("prior_version_id", sa.String(255), nullable=True),
        _created_at(),
        schema="civiccode",
    )


def downgrade() -> None:
    op.drop_table("section_version_records", schema="civiccode")
    op.drop_table("code_section_records", schema="civiccode")
    op.drop_table("code_chapter_records", schema="civiccode")
    op.drop_table("code_title_records", schema="civiccode")
