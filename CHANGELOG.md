# Changelog

All notable changes to CivicCode are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- Initial scaffold for the future `CivicSuite/civiccode` module.
- Professional documentation baseline, landing page, contribution/support/security docs, issue templates, PR template, and docs verification gate.
- Milestone 0 operating contract in `AGENTS.md`.
- Milestone 0 reconciliation report, ADR queue, milestone plan, and CivicCore placeholder-import CI gate.
- CivicCode implementation plan broken into PR-sized runtime chunks from foundation through v0.1.0 release.
- CivicCode implementation plan cross-checked against the original Module Catalog v1 extract, preserving codifier imports, resident/staff Q&A, administrative materials, popular questions, conflict detection, and CivicClerk handoff requirements under the current Apache 2.0 suite decision.
- Milestone 1 runtime foundation: installable package, FastAPI app shell, `/` and `/health` endpoints, exact `civiccore==0.2.0` dependency pin, pytest CI gate, and documentation updated to state that code-answer behavior is not available yet.
- Milestone 2 canonical schema foundation: CivicCore-first Alembic migration chain, separate `alembic_version_civiccode` table, schema-aware migration guard, canonical SQLAlchemy metadata, and ten `civiccode.*` foundation tables.
- Milestone 3 official source registry foundation: source vocabulary endpoint, source create/list/read/transition APIs, official-source provenance enforcement, public/staff source visibility split, source-state matrix, and actionable stale/failed-source messages.
- Milestone 4 section/version foundation: title/chapter/section creation APIs, immutable section-version records, current and historical section lookup, related non-code material references, pending-law refusal, overlapping-date ambiguity checks, and amendment history.
- Milestone 5 search and permalink foundation: public-safe search endpoint, exact section-number lookup through search, phrase search over adopted text, related public material result types, actionable empty search state, stable section permalink endpoint, and leakage guardrails.
- Milestone 6 citation contract foundation: deterministic citation object, section/version/source/effective-date fields, canonical URL, information-not-determination classification, and structured refusals for missing, stale, or contradictory source situations.
- Milestone 7 citation-grounded Q&A foundation: deterministic question-answer endpoint, exact citation requirement, single-result search resolution, legal-determination refusal, uncited-question refusal, stale-source refusal, and `llm_provider=not_used` guardrail.
- Milestone 8 staff workbench foundation: staff-only interpretation-note endpoints, trusted staff header seam, staff Q&A context with `staff_only_do_not_publish`, staff workbench audit events, and public-surface leakage tests for lookup, search, and Q&A.
- Milestone 9 plain-language summaries foundation: staff draft/approval workflow, approved-only public summary endpoint, non-authoritative `non_authoritative_explanation` labeling, authoritative code text kept visible beside summaries, adopted-version guardrails, and summary audit events.
- Milestone 10 CivicClerk handoff foundation: ordinance/adoption event intake, meeting/agenda provenance preservation, pending codification warnings on affected lookups, likely conflict detection, failed-handoff visibility, and guardrails proving pending ordinance language is not adopted law.

### Not Shipped

- No source persistence beyond the current in-memory registry.
- No frontend workflow.
- No live LLM calls.
- No legal-determination behavior.
- No public lookup UI, automatic ordinance codification, or public staff-note visibility yet.
