"""Add durable staff note and plain-language summary records."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

from civiccode.migrations.guards import idempotent_create_table


revision = "civiccode_0005_staff_summaries"
down_revision = "civiccode_0004_section_lifecycle"
branch_labels = None
depends_on = None


def _created_at() -> sa.Column:
    return sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())


def _updated_at() -> sa.Column:
    return sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())


def upgrade() -> None:
    idempotent_create_table(
        "staff_interpretation_note_records",
        sa.Column("note_id", sa.String(255), primary_key=True),
        sa.Column("section_id", sa.String(255), nullable=False),
        sa.Column("note_text", sa.Text(), nullable=False),
        sa.Column("status", sa.String(80), nullable=False),
        sa.Column("visibility", sa.String(80), nullable=False),
        sa.Column("created_by", sa.String(255), nullable=False),
        _created_at(),
        schema="civiccode",
    )
    idempotent_create_table(
        "staff_workbench_audit_event_records",
        sa.Column("event_id", sa.String(255), primary_key=True),
        sa.Column("event_type", sa.String(120), nullable=False),
        sa.Column("actor", sa.String(255), nullable=False),
        sa.Column("section_id", sa.String(255), nullable=True),
        sa.Column("target_id", sa.String(255), nullable=True),
        _created_at(),
        schema="civiccode",
    )
    idempotent_create_table(
        "plain_language_summary_records",
        sa.Column("summary_id", sa.String(255), primary_key=True),
        sa.Column("section_id", sa.String(255), nullable=False),
        sa.Column("section_version_id", sa.String(255), nullable=False),
        sa.Column("summary_text", sa.Text(), nullable=False),
        sa.Column("status", sa.String(80), nullable=False),
        sa.Column("language_code", sa.String(40), nullable=False),
        sa.Column("created_by", sa.String(255), nullable=False),
        sa.Column("approved_by", sa.String(255), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        _created_at(),
        _updated_at(),
        schema="civiccode",
    )
    idempotent_create_table(
        "plain_language_summary_audit_event_records",
        sa.Column("event_id", sa.String(255), primary_key=True),
        sa.Column("event_type", sa.String(120), nullable=False),
        sa.Column("actor", sa.String(255), nullable=False),
        sa.Column("section_id", sa.String(255), nullable=False),
        sa.Column("target_id", sa.String(255), nullable=False),
        _created_at(),
        schema="civiccode",
    )


def downgrade() -> None:
    op.drop_table("plain_language_summary_audit_event_records", schema="civiccode")
    op.drop_table("plain_language_summary_records", schema="civiccode")
    op.drop_table("staff_workbench_audit_event_records", schema="civiccode")
    op.drop_table("staff_interpretation_note_records", schema="civiccode")
