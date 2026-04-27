# Milestone 7 Done - Citation-Grounded Q&A Harness

## Summary

Milestone 7 adds CivicCode's deterministic citation-grounded Q&A harness. The
module can answer a question only when it resolves to one adopted code section,
one active source, and one citation object. It does not make live LLM calls and
does not provide legal determinations.

## Shipped

- Question-answer endpoint at `/api/v1/civiccode/questions/answer`.
- Exact-section Q&A path for questions that include or provide a section number.
- Single-result search resolution for questions that match one adopted section.
- Citation-grounded answer object with one citation, adopted section text,
  `classification=information_not_determination`, and
  `code_answer_behavior=citation_grounded`.
- `llm_provider=not_used` guardrail.
- Structured refusals for legal determinations, uncited questions, stale
  sources, and upstream citation-contract failures.

## Not Shipped

- No live LLM calls.
- No legal determinations or legal advice.
- No public lookup UI.
- No staff workbench or CivicClerk handoff.

## Verification Snapshot

- `python -m pytest --collect-only -q`: 66 tests collected.
- `python -m pytest -q`: 66 passed.
- `bash scripts/verify-docs.sh`: PASS.
- `python scripts/check-civiccore-placeholder-imports.py`: PASS, 19 source files scanned.
- `python -m ruff check .`: All checks passed.
- API smoke: PASS. Seeded one active official source, title, chapter, section,
  and adopted current version; `/api/v1/civiccode/questions/answer` returned
  `status=ok`, one citation, `code_answer_behavior=citation_grounded`,
  `llm_provider=not_used`, and a legal-determination request returned a
  structured refusal.
- Browser QA for `docs/index.html`: PASS in the in-app browser at
  `http://127.0.0.1:8127/docs/index.html`; required Milestone 7 current-state
  strings were present and console error count was 0.

## Next Milestone

Milestone 8: staff workbench foundation.
