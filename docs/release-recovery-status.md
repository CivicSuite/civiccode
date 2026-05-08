# CivicCode Release Recovery Status

Date: 2026-05-07
Repo: `CivicSuite/civiccode`

## Current Verdict

`v1.0.0` exists as a published package/release label, but it is provisional
during the CivicSuite release-recovery pass. Do not promote it as product-ready
until the recovery gates below are complete and current.

## Recovery Gates

| Gate | Current status | Evidence |
| --- | --- | --- |
| Public product-ready claim freeze | Passing in branch | README, text README, user manual, docs landing page, AGENTS, changelog, and docs checks now describe `v1.0.0` as provisional. |
| Runtime install proof | Passing in branch | `scripts/verify-release.sh` builds artifacts and runs CivicCore release-provenance reinstall checks in an isolated temporary virtualenv. |
| Native WSL/Linux proof | Passing in branch | WSL run selected `.venv-wsl/bin/python3`, reported platform `linux`, and completed `VERIFY-RELEASE: PASSED`. |
| Security scan | Passing in branch | Tracked-file secret scan returned no matches after the staff-note test marker rename. |
| Docs-source enforcement | Passing in branch | `scripts/verify-docs.sh` now blocks stale current-product-line claims; regression tests cover the gate. |
| Mock-vs-production labeling | Passing in branch | Existing docs distinguish local mocks, codifier sync foundation, no live LLM, no legal advice, and no automatic codification. |
| Browser/user-flow QA | Passing in branch | Playwright checked `docs/index.html` at desktop and mobile widths; see `docs/browser-qa-civiccode-release-recovery-summary.md`. |

## Current Evidence

- Focused Windows regression tests: `18 passed`.
- Native WSL release gate: `190 passed, 1 skipped`; isolated
  release-provenance test `1 passed`; docs gate, placeholder import gate, ruff,
  build artifacts, and SHA256 generation passed.
- Browser QA: desktop `1440x1000` and mobile `390x844` passed with no console
  messages, no page errors, no horizontal overflow, and keyboard focus reaching
  a link.

## Sign-Off Boundary

This recovery status does not erase the existing `1.0.0` package version. It
changes the public posture: existing v1 labels are provisional until runtime,
browser, security, documentation, and CI evidence re-earn product-ready status.
