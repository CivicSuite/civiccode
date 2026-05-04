"""Add durable operational retry, replay, and cursor state."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from civiccode.migrations.guards import idempotent_create_table


revision = "civiccode_0009_operational_state"
down_revision = "civiccode_0008_codifier_sync"
branch_labels = None
depends_on = None


def upgrade() -> None:
    idempotent_create_table(
        "operational_state_records",
        sa.Column("record_id", sa.String(255), primary_key=True),
        sa.Column("lane", sa.String(80), nullable=False),
        sa.Column("record_type", sa.String(80), nullable=False),
        sa.Column("subject_id", sa.String(255), nullable=False),
        sa.Column("status", sa.String(80), nullable=False),
        sa.Column("actor", sa.String(255), nullable=False),
        sa.Column("attempt_count", sa.Integer(), nullable=False),
        sa.Column("next_attempt_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cursor_key", sa.String(120), nullable=True),
        sa.Column("cursor_value", sa.String(255), nullable=True),
        sa.Column("replay_of", sa.String(255), nullable=True),
        sa.Column("payload_hash", sa.String(255), nullable=True),
        sa.Column("details", postgresql.JSONB(), nullable=False),
        sa.Column("failure", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        schema="civiccode",
    )


def downgrade() -> None:
    op.drop_table("operational_state_records", schema="civiccode")
