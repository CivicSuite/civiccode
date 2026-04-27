# Milestone 10 Done - CivicClerk Handoff Foundation

## Summary

Milestone 10 adds CivicCode's CivicClerk handoff foundation. Authorized staff
can receive CivicClerk ordinance/adoption events, preserve meeting and agenda
item provenance, mark affected sections with pending codification warnings, and
see likely conflict signals when ordinance text references existing sections.
The handoff does not replace adopted code text and does not perform automatic
ordinance codification.

## Shipped

- Staff-only CivicClerk ordinance/adoption event intake endpoint at
  `/api/v1/civiccode/staff/civicclerk/ordinance-events`.
- Required CivicClerk provenance fields for meeting id and agenda item id.
- Pending codification warnings attached to affected section lookups.
- Likely conflict signals for affected sections referenced by ordinance text or
  amendment/repeal language.
- Failed-handoff visibility with failure reason.
- Audit event for received CivicClerk handoffs.

## Not Shipped

- No public lookup UI.
- No automatic ordinance codification.
- No live LLM calls.
- No legal determinations or legal advice.
- No public staff-note visibility.

## Verification Snapshot

- `python -m pytest --collect-only -q`: 85 tests collected.
- `python -m pytest -q`: 85 passed.
- `bash scripts/verify-docs.sh`: PASS.
- `python scripts/check-civiccore-placeholder-imports.py`: PASS, 25 source files scanned.
- `python -m ruff check .`: All checks passed.
- API smoke: root reports `CivicClerk handoff foundation`; handoff intake returns
  `201`; affected lookup reports `pending_codification`; adopted body remains
  unchanged; unknown affected section returns actionable `404`.
- Browser QA for `docs/index.html`: in-app browser rendered the landing page at
  `http://127.0.0.1:8127/docs/index.html`; M10 status, pending codification,
  likely-conflict copy, Milestone 11 next-step copy, `citation_grounded`, and
  `not_available` were visible; browser console reported zero errors.

## Next Milestone

Milestone 11: public code lookup surface.
