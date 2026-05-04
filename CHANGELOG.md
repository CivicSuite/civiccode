# Changelog

All notable changes to CivicCode are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [0.1.13] - 2026-05-04

### Added

- Durable section/version lifecycle storage for title, chapter, section, and
  section-version records when `CIVICCODE_SOURCE_REGISTRY_DB_URL` is configured.
- Alembic revision `civiccode_0004_section_lifecycle` for the Docker/PostgreSQL
  product path.

### Changed

- CivicCode's Docker/PostgreSQL path now keeps adopted code structure and
  current version flags after process restarts instead of relying only on demo
  reseeding.

## [0.1.12] - 2026-05-04

### Added

- Durable `popular_question_records` storage for staff-approved resident
  discovery aids when `CIVICCODE_SOURCE_REGISTRY_DB_URL` is configured.
- Alembic revision `civiccode_0003_popular_questions` for the Docker/PostgreSQL
  product path, with migration tests that verify the new head revision and
  restored table set.

### Changed

- Popular-question creation and public listing now use the configured database
  repository on the Docker path while preserving the in-memory store for
  lightweight local mode.

## [0.1.11] - 2026-05-03

### Added

- Staff-approved popular-question discovery aids that link only to cited adopted
  code and publish as public navigation aids, not legal determinations.
- Public related-material endpoint and section-page rendering for explicit
  public cross-references without exposing staff-only notes.
- City of Brookfield demo seed popular question and related-material references
  so the Docker demo shows the resident discovery workflow immediately.

### Changed

- Public lookup home and section pages now include actionable empty states for
  popular questions and related materials.

## [0.1.10] - 2026-05-03

### Added

- Docker/PostgreSQL backup-restore rehearsal helper for the Compose product
  path. The helper runs `pg_dump`, restores into a temporary database, verifies
  restored application tables, writes a manifest with checksum, and drops the
  temporary restore database by default.
- Windows PowerShell and Bash launchers for repeatable operator rehearsal:
  `scripts/start_docker_backup_restore_rehearsal.ps1` and
  `scripts/start_docker_backup_restore_rehearsal.sh`.

## [0.1.9] - 2026-05-03

### Added

- Docker Compose product path with PostgreSQL 17 plus pgvector, migration
  startup, health checks, source-registry persistence, and opt-in City of
  Brookfield demo seed data through `CIVICCODE_DEMO_SEED=1`.
- `Dockerfile`, `docker-compose.yml`, `docker.env.example`, and
  `scripts/docker-demo-smoke.sh` for a repeatable local product demo.
- Runtime demo seed middleware that populates public lookup, staff code
  workspace, approved-summary, staff-note, and CivicClerk handoff warning data
  without outbound vendor calls.

### Changed

- Promoted Alembic, SQLAlchemy, and `psycopg2-binary` to runtime dependencies so
  the packaged Docker app can run migrations and PostgreSQL-backed source
  registry persistence outside the dev extra.

## [0.1.8] - 2026-05-03

### Changed

- Aligned CivicCode with the published `civiccore v0.22.0` release wheel.
- Reused CivicCore's shared sync source-list health projection in codifier sync
  source responses while preserving the existing CivicCode `operator_status`
  shape for current staff clients.
- Bumped release verification and current-facing docs to CivicCode v0.1.8.

## [0.1.7] - 2026-05-03

### Added

- Staff-controlled codifier live-sync foundation with readiness configuration,
  schedule validation, SSRF-safe host checks, delta request planning, local
  payload sync runs, and CivicCore circuit-breaker health copy.
- Staff API endpoints under `/api/v1/civiccode/staff/sync/codifier-sources`
  for configuring codifier sources, listing operator health, and running one
  local payload through the existing import path.
- Focused tests for cron/host validation, delta cursors, circuit breaker
  behavior, staff authorization, and the no-automatic-codification boundary.

### Changed

- Bumped release verification and current-facing docs to CivicCode v0.1.7.
- Updated product copy from "live codifier sync not available" to the current
  truth: a sync foundation is available, but bundled vendor credentials,
  automatic ordinance codification, live LLM calls, and legal determinations
  remain out of scope.

## [0.1.6] - 2026-05-03

### Added

- Reusable mock-city codifier contract suite covering Municode, American Legal
  Publishing, Code Publishing Company, and General Code source interfaces.
- `scripts/run_mock_city_environment_suite.py` writes a secret-free JSON report
  and verifies CivicCode codifier imports without outbound vendor calls.
- Mock-city environment report reuses CivicCore municipal IdP and
  backup-retention contracts so future modules can follow the same pattern.

### Changed

- Bumped release verification and current-facing docs to CivicCode v0.1.6.
- Aligned CivicCode with the published `civiccore v0.21.0` wheel so the
  reusable mock-city contracts resolve from a published CivicCore release.

## [0.1.5] - 2026-05-02

### Added

- Staff code lifecycle workspace at `/staff/code` with access-required, empty,
  readiness-snapshot, section-card, draft-summary, and pending-codification states.
- Staff workspace payload now surfaces current adopted version counts, source
  readiness, plain-language summary blockers, staff note counts, and CivicClerk
  handoff warnings in one operator-facing page.

### Changed

- Bumped release verification and current-facing docs to CivicCode v0.1.5.
- Added store read helpers for staff workspace aggregation without exposing
  staff-only data on public endpoints.

## [0.1.4] - 2026-05-02

### Changed

- Corrected the current-release user manual status so the packaged documentation matches the staff source registry workspace release line.

## [0.1.3] - 2026-05-02

### Added

- Staff source registry workspace at `/staff/sources` with empty, access-required,
  source-card, stale-source, and failed-source states for code administrators.

### Changed

- Staff source create, transition, list, and detail APIs now require the trusted
  staff header seam before exposing staff-only source notes or mutating the
  registry.

## [0.1.2] - 2026-05-02

### Added

- Production-depth source registry persistence slice with
  `CIVICCODE_SOURCE_REGISTRY_DB_URL`, durable source metadata/status/staff-note
  records, and Alembic revision `civiccode_0002_sources`.

### Changed

- Align CivicCode's CivicCore dependency, CI install wheel, documentation, health contract, and release gate with the published `civiccore v0.19.0` release wheel so the module can join the current CivicSuite shared-platform line before the next product-depth slice.

## [0.1.1] - 2026-04-28

### Changed

- Align CivicCode's exact CivicCore dependency, CI install wheel, documentation, health contract, and release gate with `civiccore==0.3.0`.

## [0.1.0] - 2026-04-27

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
- Milestone 11 public code lookup surface: resident-facing `/civiccode` "Read code" pages for search, section detail, citations, approved summaries, pending codification warnings, stale-source warnings, actionable empty states, and legal-advice refusal routing.
- Milestone 12 import and connector hardening: staff-only local import jobs for CSV/file-drop bundles and official HTML extract fixtures, idempotent re-import behavior, actionable failed-import records, retry support, provenance report endpoints, imported-tree verification, and no required outbound dependency for local import.
- Milestone 13 accessibility and export hardening: records-ready export API and HTML page for adopted sections, source/version/citation/retrieval metadata in export payloads, semantic headings and labels, print-friendly output, stale-source export refusals, and CivicAccess integration notes without a shipped CivicAccess runtime dependency.

### Not Shipped

- No live LLM calls.
- No legal-determination behavior.
- No bundled vendor credentials, live LLM calls, Redis/Celery worker
  requirement, CivicAccess runtime dependency, legal determinations, or
  automatic ordinance codification yet; staff notes remain staff-only.
