# Production Depth - Source Registry Persistence

Date: 2026-04-28
Branch: `feature-depth/source-persistence`

## Scope

This slice closes the CivicCode source-registry persistence gap. The source
registry remains in-memory by default for lightweight local smoke checks, and it
persists official/non-official source records when
`CIVICCODE_SOURCE_REGISTRY_DB_URL` is configured.

## What Shipped

- `SourceRegistryRepository` persists source metadata, source status,
  official/non-official labels, owner/retrieval metadata, and staff notes.
- Source registry API routes use the configured repository when
  `CIVICCODE_SOURCE_REGISTRY_DB_URL` is set.
- Alembic revision `civiccode_0002_sources` adds
  `civiccode.source_registry_records`.
- Regression tests prove durable status/staff-note persistence through both the
  repository and API runtime paths.
- README, README.txt, USER-MANUAL.md, USER-MANUAL.txt, CHANGELOG, and landing
  page copy now describe the shipped persistence path honestly.
- Browser QA evidence confirms the landing page renders the new persistence copy
  on desktop and mobile with zero console errors.

## Verification

```bash
python -m pytest tests/test_production_depth_source_persistence.py tests/test_milestone_2_schema_and_migrations.py tests/test_milestone_3_source_registry.py -q
# 27 passed

python -m ruff check civiccode tests
# All checks passed!
```

## Browser QA Evidence

- `docs/browser-qa-production-depth-source-persistence-desktop.png`
- `docs/browser-qa-production-depth-source-persistence-mobile.png`
- `docs/browser-qa-production-depth-source-persistence-summary.md`

## Out of Scope

- Live codifier sync.
- Redis/Celery import workers.
- Live LLM calls.
- Legal-determination behavior.
- Automatic ordinance codification.
