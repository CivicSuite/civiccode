# Milestone 8 Done - Staff Workbench Foundation

## Summary

Milestone 8 adds CivicCode's staff workbench foundation. Authorized staff can
create and read staff-only interpretation notes for adopted code sections, use
approved staff notes as staff Q&A context, and inspect staff workbench audit
events. Public lookup, public search, and public Q&A responses do not expose
staff note text or note counts.

## Shipped

- Staff-only interpretation-note create/read endpoints under
  `/api/v1/civiccode/staff/sections/{section_id}/notes`.
- Trusted header seam using `X-CivicCode-Role: staff` and `X-CivicCode-Actor`.
- Staff Q&A endpoint at `/api/v1/civiccode/staff/questions/answer`.
- Approved staff note context marked with `staff_only_do_not_publish`.
- Staff workbench audit events for interpretation-note creation.
- Public leakage tests proving public lookup, search, and Q&A omit staff note
  text and staff note counts.

## Not Shipped

- No public lookup UI.
- No plain-language summary workflow.
- No CivicClerk handoff.
- No live LLM calls.
- No legal determinations or legal advice.
- No public staff-note visibility.

## Verification Snapshot

- `python -m pytest --collect-only -q`: 72 tests collected.
- `python -m pytest -q`: 72 passed.
- `bash scripts/verify-docs.sh`: PASS.
- `python scripts/check-civiccore-placeholder-imports.py`: PASS, 21 source files scanned.
- `python -m ruff check .`: All checks passed.
- API smoke: PASS. Seeded one active official source, title, chapter, section,
  and adopted current version; created one approved staff-only interpretation
  note; staff Q&A returned `staff_only_do_not_publish`; public Q&A returned
  `audience=public` and did not include the staff-only marker.
- Browser QA for `docs/index.html`: PASS in the in-app browser at
  `http://127.0.0.1:8127/docs/index.html`; required Milestone 8 current-state
  strings were present and console error count was 0.

## Next Milestone

Milestone 9: plain-language summaries.
