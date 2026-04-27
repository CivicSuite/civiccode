# Milestone 5 Done - Search And Section Permalinks

## Summary

Milestone 5 adds CivicCode's first public-safe search and stable section
permalink foundation. The module can search adopted section text and related
public material references without generating citations, summaries, Q&A, or code
answers.

## Shipped

- Public-safe search endpoint at `/api/v1/civiccode/search`.
- Exact section-number search.
- Phrase search over current adopted section text.
- Related public material results for administrative regulations, resolutions,
  and policies.
- Actionable empty search state.
- Stable section permalink endpoint at
  `/api/v1/civiccode/sections/{section_id}/permalink`.
- Search result leakage guardrails so staff/internal fields are not returned.

## Not Shipped

- No citation engine.
- No Q&A, summaries, staff workbench, CivicClerk handoff, or public lookup UI.
- No LLM/code-answer behavior.

## Verification Snapshot

- `python -m pytest --collect-only -q`: 54 tests collected.
- `python -m pytest -q`: 54 passed.
- `bash scripts/verify-docs.sh`: PASS.
- `python scripts/check-civiccore-placeholder-imports.py`: PASSED (15 source files scanned).
- `python -m ruff check .`: All checks passed.
- API smoke: root, search, and permalink passed.
- Browser QA for `docs/index.html`: PASS through in-app browser DOM/console
  check; required shipped/planned strings were visible and console errors were
  empty.

## Next Milestone

Milestone 6: citation contract.
