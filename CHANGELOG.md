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

### Not Shipped

- No source persistence beyond the current in-memory registry.
- No frontend workflow.
- No LLM/code-answer behavior.
- No search, citation engine, Q&A workflow, public lookup UI, or CivicClerk handoff yet.
