# Milestone 12 Done - Import And Connector Hardening

Date: 2026-04-27

## Scope

Milestone 12 adds the local import/connector hardening foundation for
CivicCode. It does not add live codifier sync, Redis/Celery workers, database
persistence beyond the current in-memory runtime stores, live LLM calls, legal
determinations, or automatic ordinance codification.

## Shipped Behavior

- Staff-only local import endpoint:
  `/api/v1/civiccode/staff/imports/local-bundle`
- Import job listing, detail, retry, imported-tree, and provenance report
  endpoints.
- Supported local fixture shapes:
  - `csv_bundle`
  - `official_html_extract`
- Import jobs create or reuse source, title, chapter, section, and version
  records.
- Re-importing the same bundle is idempotent and reports reused records.
- Failed imports are stored with an actionable `message` and `fix`.
- Failed imports can be retried with a corrected local bundle.
- Provenance reports expose source metadata, fixture checksum, retrieval
  method, and `no_outbound_dependency=true`.
- Local import is synchronous in this milestone; background failure visibility
  is represented by staff import job status endpoints.

## Test Coverage

- Fixture import creates the expected section tree.
- CSV/file-drop bundle import coverage.
- Official HTML extract import coverage.
- Re-import idempotency coverage.
- Failed import visibility and retry coverage.
- Staff-only endpoint protection coverage.
- No-outbound-network local import coverage.
- Provenance report coverage.
- Imported-tree scoping coverage after multiple imports.
- Documentation truth coverage to prevent live codifier sync or Redis/Celery
  worker claims.

## Verification Snapshot

Pre-audit local verification:

```text
python -m pytest --collect-only -q
101 tests collected in 0.63s

python -m pytest tests/test_milestone_12_import_connector_hardening.py -q
9 passed

python -m ruff check civiccode tests/test_milestone_12_import_connector_hardening.py
All checks passed!
```

Full-suite, docs, placeholder-import, and browser QA evidence are captured in
the PR/audit report for this milestone.

## Next Milestone

Milestone 13: accessibility and export hardening.
