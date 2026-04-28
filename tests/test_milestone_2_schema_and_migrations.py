from __future__ import annotations

import ast
import importlib
from pathlib import Path
import subprocess
import time
import uuid

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import ForeignKeyConstraint, create_engine, text


ROOT = Path(__file__).resolve().parents[1]

CANONICAL_TABLES = [
    "code_sources",
    "code_titles",
    "code_chapters",
    "code_sections",
    "section_versions",
    "section_citations",
    "interpretation_notes",
    "plain_language_summaries",
    "code_questions",
    "ordinance_events",
]

REQUIRED_COLUMNS = {
    "code_sources": {
        "id",
        "name",
        "publisher",
        "source_type",
        "source_category",
        "source_url",
        "file_reference",
        "retrieval_method",
        "retrieved_at",
        "checksum",
        "is_official",
        "status",
        "staff_notes",
        "metadata",
        "created_at",
        "updated_at",
    },
    "code_titles": {
        "id",
        "source_id",
        "title_number",
        "title_name",
        "sort_order",
        "created_at",
        "updated_at",
    },
    "code_chapters": {
        "id",
        "title_id",
        "chapter_number",
        "chapter_name",
        "sort_order",
        "created_at",
        "updated_at",
    },
    "code_sections": {
        "id",
        "chapter_id",
        "section_number",
        "section_heading",
        "parent_section_id",
        "sort_order",
        "created_at",
        "updated_at",
    },
    "section_versions": {
        "id",
        "section_id",
        "source_id",
        "version_label",
        "body",
        "effective_start",
        "effective_end",
        "adoption_event_id",
        "is_current",
        "created_at",
        "updated_at",
    },
    "section_citations": {
        "id",
        "section_version_id",
        "citation_text",
        "canonical_url",
        "retrieved_at",
        "created_at",
        "updated_at",
    },
    "interpretation_notes": {
        "id",
        "section_id",
        "note_text",
        "visibility",
        "status",
        "approved_by",
        "approved_at",
        "created_at",
        "updated_at",
    },
    "plain_language_summaries": {
        "id",
        "section_version_id",
        "summary_text",
        "status",
        "approved_by",
        "approved_at",
        "language_code",
        "created_at",
        "updated_at",
    },
    "code_questions": {
        "id",
        "question_text",
        "audience",
        "status",
        "answer_text",
        "citation_payload",
        "is_popular",
        "created_at",
        "updated_at",
    },
    "ordinance_events": {
        "id",
        "external_event_id",
        "civicclerk_meeting_id",
        "civicclerk_agenda_item_id",
        "ordinance_number",
        "title",
        "adopted_at",
        "affected_sections",
        "status",
        "source_document_url",
        "source_document_hash",
        "created_at",
        "updated_at",
    },
}

PLACEHOLDER_TARGET_PREFIXES = {
    "civiccore.auth",
    "civiccore.rbac",
    "civiccore.audit",
    "civiccore.ingestion",
    "civiccore.search",
    "civiccore.notifications",
    "civiccore.connectors",
    "civiccore.exemptions",
    "civiccore.onboarding",
    "civiccore.catalog",
    "civiccore.verification",
}


def model_module():
    try:
        return importlib.import_module("civiccode.models")
    except ModuleNotFoundError as exc:
        pytest.fail(f"civiccode.models must exist for Milestone 2 schema work: {exc}")


def migration_path() -> Path:
    return ROOT / "civiccode" / "migrations" / "versions" / "civiccode_0001_schema.py"


def test_canonical_table_models_exist_and_no_tables_are_missing_or_extra() -> None:
    models = model_module()
    metadata = models.Base.metadata

    assert sorted(metadata.tables) == sorted(f"civiccode.{name}" for name in CANONICAL_TABLES)


def test_models_use_civiccode_schema_and_civiccore_shared_base() -> None:
    models = model_module()
    civiccore_db = importlib.import_module("civiccore.db")

    assert models.Base is civiccore_db.Base
    for table_name in CANONICAL_TABLES:
        table = models.Base.metadata.tables[f"civiccode.{table_name}"]
        assert table.schema == "civiccode"


def test_models_do_not_declare_a_competing_sqlalchemy_base() -> None:
    model_files = list((ROOT / "civiccode").glob("**/*.py"))
    offenders: list[str] = []
    for path in model_files:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    if getattr(base, "id", None) == "DeclarativeBase":
                        offenders.append(str(path.relative_to(ROOT)))
            if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "declarative_base":
                offenders.append(str(path.relative_to(ROOT)))

    assert offenders == []


def test_each_canonical_table_has_required_foundation_columns() -> None:
    models = model_module()

    for table_name, expected_columns in REQUIRED_COLUMNS.items():
        table = models.Base.metadata.tables[f"civiccode.{table_name}"]
        assert expected_columns <= set(table.columns.keys()), table_name


def test_no_foreign_keys_target_civiccore_placeholder_packages_or_unreleased_shared_tables() -> None:
    models = model_module()

    for table in models.Base.metadata.tables.values():
        for constraint in table.constraints:
            if not isinstance(constraint, ForeignKeyConstraint):
                continue
            for element in constraint.elements:
                target = str(element.target_fullname)
                assert not any(target.startswith(prefix) for prefix in PLACEHOLDER_TARGET_PREFIXES)
                assert not target.startswith("civiccore."), (
                    "CivicCode may only FK into CivicCore tables that exist in v0.3.0; "
                    f"unexpected target: {target}"
                )


def test_alembic_scaffold_exists_for_civiccode_schema_chain() -> None:
    expected = [
        ROOT / "civiccode" / "migrations" / "alembic.ini",
        ROOT / "civiccode" / "migrations" / "env.py",
        migration_path(),
    ]

    for path in expected:
        assert path.exists(), f"Missing migration scaffold file: {path.relative_to(ROOT)}"


def test_alembic_env_runs_civiccore_baseline_first_and_uses_separate_version_table() -> None:
    env_py = ROOT / "civiccode" / "migrations" / "env.py"
    assert env_py.exists(), "civiccode migrations env.py must exist."
    text = env_py.read_text(encoding="utf-8")

    assert "civiccore.migrations.runner" in text
    assert "upgrade_to_head" in text
    assert "_database_url()" in text
    assert "_run_civiccore_migrations(section[\"sqlalchemy.url\"])" in text
    assert "subprocess.run" in text
    assert "version_table=\"alembic_version_civiccode\"" in text
    assert "target_metadata = Base.metadata" in text


def test_schema_aware_guard_checks_table_inside_target_schema() -> None:
    guard_py = ROOT / "civiccode" / "migrations" / "guards.py"
    text = guard_py.read_text(encoding="utf-8")

    assert "schema = kwargs.get(\"schema\")" in text
    assert "has_table(name, schema=schema)" in text


def test_alembic_command_upgrades_real_pgvector_database(monkeypatch: pytest.MonkeyPatch) -> None:
    """Run the actual operator migration path against disposable Postgres."""
    name = f"civiccode-m2-{uuid.uuid4().hex[:12]}"
    subprocess.run(
        [
            "docker",
            "run",
            "--name",
            name,
            "-e",
            "POSTGRES_PASSWORD=postgres",
            "-e",
            "POSTGRES_USER=postgres",
            "-e",
            "POSTGRES_DB=civiccode_test",
            "-p",
            "5432",
            "-d",
            "pgvector/pgvector:pg17",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    try:
        mapped = subprocess.run(
            ["docker", "port", name, "5432/tcp"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        port = mapped.rsplit(":", maxsplit=1)[-1]
        db_url = f"postgresql+psycopg2://postgres:postgres@localhost:{port}/civiccode_test"
        engine = create_engine(db_url)

        deadline = time.monotonic() + 30
        while True:
            try:
                with engine.connect() as connection:
                    connection.execute(text("select 1"))
                break
            except Exception:
                if time.monotonic() > deadline:
                    raise
                time.sleep(1)

        monkeypatch.setenv("DATABASE_URL", db_url)
        cfg = Config(str(ROOT / "civiccode" / "migrations" / "alembic.ini"))

        command.upgrade(cfg, "head")
        command.upgrade(cfg, "head")

        with engine.connect() as connection:
            civiccore_revision = connection.execute(
                text("select version_num from alembic_version_civiccore")
            ).scalar_one()
            civiccode_revision = connection.execute(
                text("select version_num from alembic_version_civiccode")
            ).scalar_one()
            civiccode_tables = set(
                connection.execute(
                    text(
                        """
                        select table_name
                        from information_schema.tables
                        where table_schema = 'civiccode'
                        """
                    )
                ).scalars()
            )

        assert civiccore_revision == "civiccore_0002_llm"
        assert civiccode_revision == "civiccode_0001_schema"
        assert civiccode_tables == set(CANONICAL_TABLES)
    finally:
        subprocess.run(["docker", "rm", "-f", name], check=False, capture_output=True, text=True)


def test_first_migration_declares_revision_and_creates_all_canonical_tables_idempotently() -> None:
    assert migration_path().exists(), "civiccode_0001_schema migration must exist."
    text = migration_path().read_text(encoding="utf-8")

    assert 'revision = "civiccode_0001_schema"' in text
    assert "down_revision = None" in text
    assert "idempotent_create_table" in text
    assert 'op.execute("CREATE SCHEMA IF NOT EXISTS civiccode")' in text

    for table_name in CANONICAL_TABLES:
        assert f'"{table_name}"' in text or f"'{table_name}'" in text
        assert 'schema="civiccode"' in text or "schema='civiccode'" in text


def test_migration_table_list_matches_model_metadata() -> None:
    models = model_module()
    text = migration_path().read_text(encoding="utf-8")

    model_tables = {table.name for table in models.Base.metadata.tables.values()}
    for table_name in model_tables:
        assert f'"{table_name}"' in text or f"'{table_name}'" in text


def test_docs_and_changelog_record_schema_milestone_without_claiming_code_answers() -> None:
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8").lower()
    manual = (ROOT / "USER-MANUAL.md").read_text(encoding="utf-8").lower()
    landing = (ROOT / "docs" / "index.html").read_text(encoding="utf-8").lower()

    for document_text in [changelog, manual, landing]:
        assert "canonical schema" in document_text
        assert "alembic" in document_text
        assert "code answers are available" not in document_text
