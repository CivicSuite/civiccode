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

### Not Shipped

- No database schema.
- No frontend workflow.
- No LLM/code-answer behavior.
