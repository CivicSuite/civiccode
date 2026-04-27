# Milestone 4 Done - Code Section And Version Lifecycle

## Summary

Milestone 4 adds the CivicCode section/version lifecycle foundation. The module
can now create title, chapter, section, subsection, and immutable section
version records; look up current and historical adopted text; and refuse
ambiguous or pending-law situations before any search, citation, Q&A, or
code-answer behavior exists.

## Shipped

- Title creation endpoint at `/api/v1/civiccode/titles`.
- Chapter creation endpoint at `/api/v1/civiccode/chapters`.
- Section/subsection creation endpoint at `/api/v1/civiccode/sections`.
- Section-version creation endpoint at
  `/api/v1/civiccode/sections/{section_id}/versions`.
- Current and historical lookup endpoint at
  `/api/v1/civiccode/sections/lookup`.
- Section history endpoint at `/api/v1/civiccode/sections/{section_id}/history`.
- Related non-code material reference fields for administrative regulations,
  resolutions, and policies.
- Section versions must reference a registered source; adopted versions require
  an active public-visible source.
- Pending ordinance language refusal so proposed or pending text is not treated
  as adopted law.
- Overlapping adopted effective-date refusal with actionable fix guidance.
- Amendment history that preserves prior and current text without silent edits.

## Not Shipped

- No search or section permalink UI.
- No citation engine.
- No Q&A, summaries, staff workbench, CivicClerk handoff, or public lookup UI.
- No LLM/code-answer behavior.

## Verification Snapshot

- `python -m pytest --collect-only -q`: 45 tests collected.
- `python -m pytest -q`: 45 passed.
- `bash scripts/verify-docs.sh`: PASS.
- `python scripts/check-civiccore-placeholder-imports.py`: PASSED (14 source files scanned).
- `python -m ruff check .`: All checks passed.
- API smoke: root, title, chapter, section, version create, and lookup passed.
- Browser QA for `docs/index.html`: PASS through in-app browser DOM/console
  check; required shipped/planned strings were visible and console errors were
  empty.

## Next Milestone

Milestone 5: search and section permalinks.
