# Milestone 6 Done - Citation Contract

## Summary

Milestone 6 adds CivicCode's deterministic citation contract. The module can
build structured citation objects from adopted section text and return
structured refusals for missing, stale, contradictory, or ambiguous situations
without generating Q&A, summaries, legal advice, or code answers.

## Shipped

- Citation builder endpoint at `/api/v1/civiccode/citations/build`.
- Citation object with section id, version id, source id, effective date, and
  canonical URL.
- Citation text containing title, chapter, section, version label, and
  effective date.
- `information_not_determination` classification.
- Structured refusal object with reason and fix path.
- Refusals for missing sections, stale sources, and overlapping adopted
  effective dates.
- Guardrail that citation endpoint returns objects, not uncited prose answers.

## Not Shipped

- No Q&A workflow.
- No public lookup UI.
- No staff workbench, CivicClerk handoff, or LLM/code-answer behavior.

## Verification Snapshot

- `python -m pytest --collect-only -q`: 60 tests collected.
- `python -m pytest -q`: 60 passed.
- `bash scripts/verify-docs.sh`: PASS.
- `python scripts/check-civiccore-placeholder-imports.py`: PASS, 17 source files scanned.
- `python -m ruff check .`: All checks passed.
- API smoke: PASS. Seeded one active official source, title, chapter, section,
  and adopted current version; `/api/v1/civiccode/citations/build` returned
  `status=ok`, citation text with title/chapter/section/version/effective date,
  `classification=information_not_determination`,
  `code_answer_behavior=not_available`, and no `answer` field.
- Browser QA for `docs/index.html`: PASS in the in-app browser at
  `http://127.0.0.1:8127/docs/index.html`; required Milestone 6 current-state
  strings were present and console error count was 0.

## Next Milestone

Milestone 7: citation-grounded Q&A harness.
