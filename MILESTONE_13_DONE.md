# Milestone 13 Done - Accessibility And Export Hardening

Date: 2026-04-27

## Scope

Milestone 13 adds records-ready export and accessibility hardening before the
v0.1.0 release. It does not add CivicAccess runtime integration, live LLM
calls, live codifier sync, legal determinations, database persistence beyond
the current in-memory stores, or automatic ordinance codification.

## Shipped Behavior

- Public records-ready JSON export endpoint:
  `/api/v1/civiccode/sections/{section_ref}/export`
- Public accessible HTML export endpoint:
  `/civiccode/sections/{section_ref}/export`
- Public section detail pages link to the records-ready export.
- Export payloads include:
  - authoritative adopted section text,
  - section version metadata,
  - deterministic citation,
  - source provenance,
  - retrieval method and checksum metadata,
  - accessibility labels,
  - legal-boundary copy.
- HTML exports include semantic headings, labeled metadata blocks,
  focus-visible styling, and print-friendly output.
- Stale-source exports refuse actionably instead of producing a records package
  with unsafe provenance.
- Docs state that CivicAccess is planned infrastructure, not a shipped runtime
  dependency.

## Test Coverage

- Records-ready export includes source, version, citation, and retrieval
  metadata.
- HTML export includes headings, labels, skip link, focus styling, print output,
  and legal-boundary copy.
- Public section detail links to the export route.
- Stale-source export fails with an actionable API refusal and accessible HTML
  problem page.
- Documentation truth coverage prevents claiming a shipped CivicAccess runtime
  dependency.

## Verification Snapshot

Pre-audit local verification:

```text
python -m pytest --collect-only -q
106 tests collected

python -m pytest tests/test_milestone_13_accessibility_export_hardening.py -q
5 passed

python -m ruff check civiccode tests/test_milestone_13_accessibility_export_hardening.py
All checks passed!
```

Final local verification before PR:

```text
python -m pytest -q
106 passed

bash scripts/verify-docs.sh
PASS

python scripts/check-civiccore-placeholder-imports.py
PLACEHOLDER-IMPORT-CHECK: PASSED (31 source files scanned)

python -m ruff check .
All checks passed!
```

Browser QA covered the export page, public section detail page, and landing
page at desktop and mobile widths. All checked pages rendered a main landmark,
records-ready copy, and zero console errors. Export and landing pages include
skip links and focus-visible styling.

## Next Milestone

Milestone 14: v0.1.0 release.
