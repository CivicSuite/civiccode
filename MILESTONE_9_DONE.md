# Milestone 9 Done - Plain-Language Summaries

## Summary

Milestone 9 adds CivicCode's plain-language summaries foundation. Authorized
staff can draft summaries tied to adopted section versions, approve them for
public display, and keep the authoritative section text visible beside every
approved summary. Public summaries are explicitly labeled as non-authoritative
explanations and are not legal advice.

## Shipped

- Staff-only plain-language summary create endpoint under
  `/api/v1/civiccode/staff/sections/{section_id}/summaries`.
- Staff approval endpoint at `/api/v1/civiccode/staff/summaries/{summary_id}/approve`.
- Public approved-summary endpoint under
  `/api/v1/civiccode/sections/{section_id}/summaries`.
- Adopted-section-version guardrail before summary drafting and approval.
- `non_authoritative_explanation` label and "summaries are not law" warning.
- Authoritative section metadata and code text returned beside public summaries.
- Audit events for summary creation and approval.

## Not Shipped

- No public lookup UI.
- No CivicClerk handoff.
- No live LLM calls.
- No legal determinations or legal advice.
- No public staff-note visibility.

## Verification Snapshot

- `python -m pytest --collect-only -q`: 78 tests collected.
- `python -m pytest -q`: 78 passed.
- `bash scripts/verify-docs.sh`: PASS.
- `python scripts/check-civiccore-placeholder-imports.py`: PASS, 23 source files scanned.
- `python -m ruff check .`: All checks passed.
- API smoke: PASS. Seeded one active official source, title, chapter, section,
  and adopted current version; created a draft summary; public summary count was
  0 before approval; approved the summary; public response returned
  `non_authoritative_explanation` and authoritative section text.
- Browser QA for `docs/index.html`: PASS in the in-app browser at
  `http://127.0.0.1:8127/docs/index.html`; required Milestone 9 current-state
  strings were present and console error count was 0.

## Next Milestone

Milestone 10: CivicClerk handoff intake.
