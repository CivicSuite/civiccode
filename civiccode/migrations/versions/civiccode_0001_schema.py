"""Create CivicCode canonical schema."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from civiccode.migrations.guards import idempotent_create_table


revision = "civiccode_0001_schema"
down_revision = None
branch_labels = None
depends_on = None


def _id_column() -> sa.Column:
    return sa.Column(
        "id",
        postgresql.UUID(as_uuid=True),
        primary_key=True,
        server_default=sa.text("gen_random_uuid()"),
    )


def _timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    ]


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS civiccode")

    idempotent_create_table("code_sources", _id_column(), sa.Column("name", sa.String(255), nullable=False), sa.Column("publisher", sa.String(255), nullable=False), sa.Column("source_type", sa.String(80), nullable=False), sa.Column("source_category", sa.String(120), nullable=False), sa.Column("source_url", sa.Text(), nullable=True), sa.Column("file_reference", sa.Text(), nullable=True), sa.Column("retrieval_method", sa.String(120), nullable=False), sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=True), sa.Column("checksum", sa.String(128), nullable=True), sa.Column("is_official", sa.Boolean(), nullable=False, server_default=sa.text("false")), sa.Column("status", sa.String(80), nullable=False), sa.Column("staff_notes", sa.Text(), nullable=True), sa.Column("metadata", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")), *_timestamps(), schema="civiccode")
    idempotent_create_table("code_titles", _id_column(), sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("title_number", sa.String(80), nullable=False), sa.Column("title_name", sa.String(500), nullable=False), sa.Column("sort_order", sa.Integer(), nullable=False, server_default=sa.text("0")), *_timestamps(), sa.ForeignKeyConstraint(["source_id"], ["civiccode.code_sources.id"]), schema="civiccode")
    idempotent_create_table("code_chapters", _id_column(), sa.Column("title_id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("chapter_number", sa.String(80), nullable=False), sa.Column("chapter_name", sa.String(500), nullable=False), sa.Column("sort_order", sa.Integer(), nullable=False, server_default=sa.text("0")), *_timestamps(), sa.ForeignKeyConstraint(["title_id"], ["civiccode.code_titles.id"]), schema="civiccode")
    idempotent_create_table("code_sections", _id_column(), sa.Column("chapter_id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("section_number", sa.String(120), nullable=False), sa.Column("section_heading", sa.String(500), nullable=False), sa.Column("parent_section_id", postgresql.UUID(as_uuid=True), nullable=True), sa.Column("sort_order", sa.Integer(), nullable=False, server_default=sa.text("0")), *_timestamps(), sa.ForeignKeyConstraint(["chapter_id"], ["civiccode.code_chapters.id"]), sa.ForeignKeyConstraint(["parent_section_id"], ["civiccode.code_sections.id"]), schema="civiccode")
    idempotent_create_table("section_versions", _id_column(), sa.Column("section_id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("version_label", sa.String(120), nullable=False), sa.Column("body", sa.Text(), nullable=False), sa.Column("effective_start", sa.Date(), nullable=False), sa.Column("effective_end", sa.Date(), nullable=True), sa.Column("adoption_event_id", postgresql.UUID(as_uuid=True), nullable=True), sa.Column("is_current", sa.Boolean(), nullable=False, server_default=sa.text("false")), *_timestamps(), sa.ForeignKeyConstraint(["section_id"], ["civiccode.code_sections.id"]), sa.ForeignKeyConstraint(["source_id"], ["civiccode.code_sources.id"]), schema="civiccode")
    idempotent_create_table("section_citations", _id_column(), sa.Column("section_version_id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("citation_text", sa.String(500), nullable=False), sa.Column("canonical_url", sa.Text(), nullable=True), sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=True), *_timestamps(), sa.ForeignKeyConstraint(["section_version_id"], ["civiccode.section_versions.id"]), schema="civiccode")
    idempotent_create_table("interpretation_notes", _id_column(), sa.Column("section_id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("note_text", sa.Text(), nullable=False), sa.Column("visibility", sa.String(80), nullable=False), sa.Column("status", sa.String(80), nullable=False), sa.Column("approved_by", sa.String(255), nullable=True), sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True), *_timestamps(), sa.ForeignKeyConstraint(["section_id"], ["civiccode.code_sections.id"]), schema="civiccode")
    idempotent_create_table("plain_language_summaries", _id_column(), sa.Column("section_version_id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("summary_text", sa.Text(), nullable=False), sa.Column("status", sa.String(80), nullable=False), sa.Column("approved_by", sa.String(255), nullable=True), sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True), sa.Column("language_code", sa.String(20), nullable=False, server_default=sa.text("'en'")), *_timestamps(), sa.ForeignKeyConstraint(["section_version_id"], ["civiccode.section_versions.id"]), schema="civiccode")
    idempotent_create_table("code_questions", _id_column(), sa.Column("question_text", sa.Text(), nullable=False), sa.Column("audience", sa.String(80), nullable=False), sa.Column("status", sa.String(80), nullable=False), sa.Column("answer_text", sa.Text(), nullable=True), sa.Column("citation_payload", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")), sa.Column("is_popular", sa.Boolean(), nullable=False, server_default=sa.text("false")), *_timestamps(), schema="civiccode")
    idempotent_create_table("ordinance_events", _id_column(), sa.Column("external_event_id", sa.String(255), nullable=False), sa.Column("civicclerk_meeting_id", sa.String(255), nullable=True), sa.Column("civicclerk_agenda_item_id", sa.String(255), nullable=True), sa.Column("ordinance_number", sa.String(120), nullable=False), sa.Column("title", sa.String(500), nullable=False), sa.Column("adopted_at", sa.DateTime(timezone=True), nullable=True), sa.Column("affected_sections", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")), sa.Column("status", sa.String(80), nullable=False), sa.Column("source_document_url", sa.Text(), nullable=True), sa.Column("source_document_hash", sa.String(128), nullable=True), *_timestamps(), schema="civiccode")


def downgrade() -> None:
    for table_name in ["ordinance_events", "code_questions", "plain_language_summaries", "interpretation_notes", "section_citations", "section_versions", "code_sections", "code_chapters", "code_titles", "code_sources"]:
        op.drop_table(table_name, schema="civiccode")
