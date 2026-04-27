# Milestone 14 Done - v0.1.0 Release

Date: 2026-04-27

## Scope

Milestone 14 prepares CivicCode v0.1.0 for release. It synchronizes version
surfaces, promotes the changelog entry from `[Unreleased]` to `[0.1.0]`, adds a
release verification gate, and confirms the first runtime release remains
honest about shipped and planned behavior.

## Shipped Behavior

- CivicCode package version is `0.1.0`.
- `/health` reports CivicCode `0.1.0` and CivicCore `0.2.0`.
- Root endpoint reports the v0.1.0 shipped state and points future work back to
  the CivicSuite roadmap rather than another pre-release milestone.
- Release verification builds wheel and sdist artifacts and writes
  `SHA256SUMS.txt`.
- CI runs the release verification gate.

## Verification Snapshot

Release-prep local verification:

```text
python -m pytest --collect-only -q
106 tests collected

python -m pytest -q
106 passed

bash scripts/verify-docs.sh
PASS

python scripts/check-civiccore-placeholder-imports.py
PLACEHOLDER-IMPORT-CHECK: PASSED (31 source files scanned)

python -m ruff check .
All checks passed!

bash scripts/verify-release.sh
VERIFY-RELEASE: PASSED
```

Browser/runtime QA:

```text
GET /health
{"status":"ok","service":"civiccode","version":"0.1.0","civiccore":"0.2.0"}
```

Landing-page desktop and mobile checks rendered the v0.1.0 release copy with a
main landmark, skip link, focus-visible styling, and zero console errors. The
root JSON endpoint reported the v0.1.0 release state with zero console errors.

## Post-Merge Release Tasks

- Tag `v0.1.0` on the merged release commit.
- Upload `civiccode-0.1.0-py3-none-any.whl`,
  `civiccode-0.1.0.tar.gz`, and `SHA256SUMS.txt` to the GitHub release.
- Update `CivicSuite/civicsuite` compatibility docs after the release exists.
