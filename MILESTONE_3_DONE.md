# Milestone 3 Done - Official Source Registry

## Summary

Milestone 3 adds the CivicCode official source registry foundation. The module
can now register source records for official codifiers, official exports, file
drops, and explicitly labeled non-official materials before any section import,
search, citation, public lookup, or code-answer behavior exists.

## Shipped

- Source registry vocabulary endpoint at `/api/v1/civiccode/sources/catalog`.
- Source create/list/read endpoints for public-safe and staff workflows.
- Source-state transition endpoint with a full state matrix.
- Supported source types for Municode, American Legal, Code Publishing, General
  Code, official XML/DOCX exports, official file drops, and official web
  scrape/export paths.
- Supported categories for municipal code, administrative regulations,
  resolutions, policies, adopted ordinances, historical versions, approved
  summaries, and internal staff notes.
- Official-source provenance enforcement for active sources.
- Explicit non-official labeling for active non-official sources.
- Public/staff visibility split so staff-only notes do not leak through public
  endpoints.
- Actionable responses for missing, stale, failed, invalid URL, invalid file
  reference, and invalid transition cases.

## Not Shipped

- No source persistence beyond the in-memory Milestone 3 registry.
- No section/version import lifecycle.
- No search, citations, Q&A, summaries, staff workbench, CivicClerk handoff, or
  public lookup UI.
- No LLM/code-answer behavior.

## Verification Snapshot

- `python -m pytest --collect-only -q`: 34 tests collected.
- `python -m pytest -q`: 34 passed.
- `bash scripts/verify-docs.sh`: PASS.
- `python scripts/check-civiccore-placeholder-imports.py`: PASSED (12 source files scanned).
- `python -m ruff check .`: All checks passed.
- API smoke: root, catalog, source create, and public sanitized source read passed.
- Browser QA for `docs/index.html`: PASS through in-app browser DOM/console check;
  required shipped/planned strings were visible and console errors were empty.

## Next Milestone

Milestone 4: code section and version lifecycle.
