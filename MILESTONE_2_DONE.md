# CivicCode Milestone 2 Done

Status: Complete  
Date: 2026-04-27  
Branch: `milestone-2/schema-and-migrations`

## Scope

Milestone 2 ships the CivicCode canonical schema and Alembic migration
foundation.

Shipped:

- `civiccode.models` using `civiccore.db.Base`.
- Ten canonical `civiccode.*` foundation tables:
  `code_sources`, `code_titles`, `code_chapters`, `code_sections`,
  `section_versions`, `section_citations`, `interpretation_notes`,
  `plain_language_summaries`, `code_questions`, and `ordinance_events`.
- Alembic config and env under `civiccode/migrations`.
- CivicCore-first migration execution through an isolated subprocess to avoid
  nested Alembic context proxy breakage.
- Separate CivicCode version table: `alembic_version_civiccode`.
- Schema-aware local migration guard.
- Real pgvector-backed migration integration test that runs upgrade twice.
- Docs and root endpoint updated from runtime-foundation truth to
  schema-foundation truth.

Not shipped:

- Official source registry API.
- Import workflows.
- Search or section permalinks.
- Citation engine.
- LLM calls or code-answer behavior.
- Public lookup UI.

## Verification

- `python -m pytest --collect-only -q`: 22 tests collected.
- `python -m pytest -q`: 22 passed.
- `bash scripts/verify-docs.sh`: PASS.
- `python scripts/check-civiccore-placeholder-imports.py`: PASS.
- `python -m ruff check .`: PASS.
- Real pgvector migration integration test: PASS; ran Alembic upgrade twice,
  verified CivicCore revision `civiccore_0002_llm`, CivicCode revision
  `civiccode_0001_schema`, and all ten `civiccode.*` tables.

## Next

Milestone 3: official source registry.
