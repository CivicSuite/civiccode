# CivicCode Release Recovery Status

Date: 2026-05-09
Repo: `CivicSuite/civiccode`

## Current Verdict

`v1.0.0` exists as a published package/release label, but it remains
provisional until the current recovery branch is reviewed, merged, and CI is
green after merge. Local runtime, browser, Docker, documentation, and release
verification gates have been rerun in the recovery workspace.

## Recovery Gates

| Gate | Current status | Evidence |
| --- | --- | --- |
| Public product-ready claim freeze | Passing in branch | README, text README, user manual, docs landing page, AGENTS, changelog, and docs checks now describe `v1.0.0` as provisional. |
| Runtime install proof | Passing in branch | `scripts/verify-release.sh` builds artifacts and runs CivicCore release-provenance reinstall checks in an isolated temporary virtualenv. |
| Native WSL/Linux proof | Passing in branch | WSL run selected `.venv-wsl/bin/python3`, reported platform `linux`, and completed `VERIFY-RELEASE: PASSED`. |
| Security scan | Passing in branch | Tracked-file secret scan returned no matches after the staff-note test marker rename. |
| Docs-source enforcement | Passing in branch | `scripts/verify-docs.sh` now blocks stale current-product-line claims; regression tests cover the gate. |
| Mock-vs-production labeling | Passing in branch | Existing docs distinguish local mocks, codifier sync foundation, no live LLM, no legal advice, and no automatic codification. |
| Browser/user-flow QA | Passing in branch | Fresh browser QA checked 10 public resident scenarios and 16 staff scenarios with no console errors, page errors, or horizontal overflow; see `docs/qa/civiccode-current-public-staff-browser-qa.md`. |
| Docker demo runtime | Passing in branch | Clean Compose project `civiccode_recovery_verify` built the image, started PostgreSQL, served the seeded app, and passed `scripts/docker-demo-smoke.sh`. |
| Docker/PostgreSQL backup-restore | Passing in branch | Clean Compose project `civiccode_recovery_verify` passed `pg_dump`, temporary restore database creation, `pg_restore`, restored application table verification, and cleanup. |

## Current Evidence

- Product test suite: `192 passed`.
- Full release gate: `VERIFY-RELEASE: PASSED`, including version surfaces,
  product tests, isolated CivicCore release-provenance test, docs gate,
  placeholder import gate, ruff, build artifacts, and SHA256 generation.
- Browser QA: 10 public resident scenarios and 16 staff scenarios passed with
  no console messages, no page errors, no horizontal overflow, and keyboard
  focus reaching skip links.
- Docker proof: clean Compose smoke and backup/restore rehearsal passed for
  `civiccode_recovery_verify`.

## Sign-Off Boundary

This recovery status does not erase the existing `1.0.0` package version. It
changes the public posture: existing v1 labels are provisional until this
recovery branch is reviewed, merged, and CI evidence confirms the same gates on
the shared branch.
