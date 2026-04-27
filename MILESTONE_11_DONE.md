# Milestone 11 Done - Public Code Lookup Surface

## Summary

Milestone 11 adds CivicCode's resident-facing public code lookup surface under
`/civiccode`. Public users can search by section number or plain-language
phrase, open section detail pages, read authoritative adopted code text, see
deterministic citations, view approved non-authoritative summaries, and see
pending codification warnings when CivicClerk handoffs may affect a section.

## Shipped

- Public lookup home page at `/civiccode`.
- Public search results page at `/civiccode/search`.
- Public section detail page at `/civiccode/sections/{section_number}`.
- Accessible search, empty, legal-advice refusal, stale-source warning, and
  section-detail states.
- Citation display with source, section, and version metadata.
- Approved plain-language summary display beside authoritative code text.
- Pending codification warning display for CivicClerk handoff events.
- Staff-contact routing copy for official interpretation and legal questions.

## Not Shipped

- No live LLM calls.
- No legal determinations or legal advice.
- No automatic ordinance codification.
- Staff notes remain staff-only.
- No import parser or persistent source storage beyond the current in-memory
  foundation.

## Verification Snapshot

- `python -m pytest --collect-only -q`: 92 tests collected.
- `python -m pytest -q`: 92 passed.
- `bash scripts/verify-docs.sh`: PASS.
- `python scripts/check-civiccore-placeholder-imports.py`: PASS, 27 source files scanned.
- `python -m ruff check .`: All checks passed.
- Browser QA for `/civiccode`: page rendered; "Read code with citations,"
  "Ready for a search," "No live LLM," and legal-advice boundary copy visible;
  console errors: 0.
- Browser QA for `/civiccode/search?q=backyard%20chickens`: search result page
  rendered; "Backyard chickens," "Citation-ready," and "authoritative code
  text" visible; console errors: 0.
- Browser QA for `/civiccode/sections/6.12.040`: section detail page rendered;
  authoritative code text, approved summary, pending codification warning,
  citation, and City Clerk contact copy visible; console errors: 0.
- Browser QA for empty/refusal states: no-results and legal-advice refusal pages
  rendered with actionable fix/contact copy; console errors: 0.

## Next Milestone

Milestone 12: import and connector hardening.
