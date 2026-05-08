# CivicCode Audit-Full Recovery Packet

Date: 2026-05-07
Repo: `CivicSuite/civiccode`
Branch: `recovery/civiccode-release-truth-gates`
Mode: release-gate recovery cleanup

## 1. Executive Audit

Scope: CivicCode local checkout and live `origin/main` parity at the branch
baseline. The repo is under active cleanup. Local `HEAD` and `origin/main`
matched before edits at `6c4ec918b8efa76a6f491b607de9f21fc36d4364`; the remote
URL is `https://github.com/CivicSuite/civiccode.git` with no embedded token.

Overall verdict: CivicCode had credible implementation depth, but the published
v1 label and supporting docs were too confident for the recovery standard. This
branch freezes fresh product-ready promotion, fixes the WSL verification defect,
isolates release-provenance dependency installation, adds docs-source guardrails,
and records current browser evidence.

Ship posture: do not promote CivicCode as recertified product-ready until this
branch merges and post-merge CI is green.

Severity summary: Critical 2 fixed; Major 2 fixed; Minor 2 fixed; unresolved
Blocker/Critical 0.

Static audit confidence: high for the recovery changes listed here.
Runtime sign-off confidence: medium-high after native WSL release verification
and Playwright docs QA; final confidence depends on post-merge CI.

Top cross-cutting findings:

1. `REL-001`: WSL proof could use Windows Python.
2. `REL-002`: release-provenance install mutated the selected/global Python.
3. `DOC-001`: public docs described v1 as the active release family.
4. `TEST-001`: no regression test locked native Python preference.
5. `SEC-001`: tracked-file secret scan had a false positive.
6. `UX-001`: changed docs copy needed current browser evidence.

CI/workflow posture: CI exists and runs the release script; final status must be
checked after PR push and merge.

## 2. Audit Coverage Ledger

| Lane | Status | Evidence summary | Blocker |
| --- | --- | --- | --- |
| remote parity | Checked | `git fetch origin`; `HEAD` and `origin/main` matched at branch baseline. | None |
| local-vs-live commit truth | Checked | `git rev-list --left-right --count HEAD...origin/main` returned `0 0` before edits. | None |
| CI/workflow presence | Checked | Existing workflow invokes `bash scripts/verify-release.sh`; regression test covers this. | None |
| Windows install path | Partially checked | Focused Windows pytest pass completed. | Full Windows release gate not rerun after WSL pass. |
| Linux or Unix install path | Checked | WSL `.venv-wsl/bin/python3` release gate passed. | None |
| platform parity verdict | Checked | Prior false WSL proof fixed; WSL now selects native Linux Python. | None |
| first boot | Partially checked | FastAPI import and endpoint tests passed. | Browser app flow not rerun in this branch. |
| required post-install steps | Checked | `scripts/verify-release.sh` installs/builds in verification flow. | None |
| migrations | Partially checked | Product suite passed under WSL. | No database migration rehearsal added in this branch. |
| seed/bootstrap requirements | Partially checked | Existing product tests and docs checked. | No new seed path created. |
| runtime dependency and model requirements | Checked | No live LLM; CivicCore v1 wheel dependency verified. | None |
| first-boot dependency truth | Checked | WSL editable install and release gate passed. | None |
| secrets and credential handling | Checked | Tracked-file secret scan returned no matches. | None |
| auth and session handling | Partially checked | Existing staff-role tests passed. | Full auth audit deferred to broader recertification. |
| authorization and role boundaries | Partially checked | Staff note public leak tests passed. | Full app browser role QA not rerun here. |
| response-schema sensitive-data exposure | Checked | Staff note non-leak test passed. | None |
| audit and compliance logging | Partially checked | Existing suite passed. | No new audit-log runtime drill. |
| external and admin surfaces | Partially checked | Public docs and API tests covered. | No live deployment proof required. |
| connector implementation completeness | Partially checked | CivicCore/CivicClerk boundaries not changed. | Full connector recertification remains separate. |
| connector docs truth | Checked | Public docs now provisional and mock-vs-production labeled. | None |
| background jobs and schedulers | Partially checked | Existing product tests passed. | No scheduler stress drill. |
| frontend critical journeys | Partially checked | Docs landing page browser QA passed. | Full app journeys remain for recertification. |
| loading states | Partially checked | Not changed by this branch. | Full UX recertification still needed. |
| empty states | Partially checked | Not changed by this branch. | Full UX recertification still needed. |
| error states | Partially checked | Not changed by this branch. | Full UX recertification still needed. |
| partial states | Partially checked | Not changed by this branch. | Full UX recertification still needed. |
| accessibility cues | Partially checked | Keyboard focus reached a link on docs page. | Full app accessibility pass still needed. |
| docs truthfulness | Checked | Product-ready claim freeze and docs banlist added. | None |
| version consistency | Checked | `scripts/verify-release.sh` version surface check passed. | None |
| release artifact consistency | Checked | Build artifacts and `SHA256SUMS.txt` generated. | None |
| test realism | Checked | Regression tests added for release-script failure mode. | None |
| runtime, build, and test verification | Checked | WSL release gate passed. | None |
| browser verification | Checked | Playwright desktop/mobile screenshots and summary added. | None |
| prior audit or verification challenge | Checked | This pass directly challenged prior release-truth claims. | None |

## 3. Claim Verification Matrix

| Claim | Source | Verdict | Evidence |
| --- | --- | --- | --- |
| CivicCode v1 is a published label. | `pyproject.toml`, docs | True | Version gate passed at `1.0.0`. |
| CivicCode is freshly product-ready. | Prior docs wording | False as a current claim | Docs now mark this provisional until recovery gates/CI re-earn it. |
| CivicCode depends on CivicCore v1.0.0 wheel. | `pyproject.toml` | True | Product tests and isolated provenance test install the wheel. |
| WSL release verification proves Linux. | Prior script behavior | Previously false, now true in branch | Baseline could select Windows Python; branch selected `.venv-wsl/bin/python3` and platform `linux`. |
| Docs/source gate blocks stale marketing claims. | `scripts/verify-docs.sh` | True in branch | Banlist and regression tests added. |
| Browser docs surface reflects recovery status. | `docs/index.html` | True | Playwright desktop/mobile pass. |

## 4. What The Dev Team Needs To Do Now

### Must fix before ship

- None remaining in this branch-level recovery scope.

### Should fix this sprint

- `CI-001`: Push the branch, open PR, wait for CI, merge only if green.
  Owner: release engineering. Verification: GitHub check URLs and post-merge
  main status.

### Can defer if consciously accepted

- `UX-002`: Full application browser recertification across every public/staff
  state. Owner: UX/QA. Verification: Playwright user-flow suite and screenshots
  for loading, success, empty, error, and partial states.

## 5. Next-Sprint Watchlist

Architecture: keep CivicCode dependency direction one-way through CivicCore.
Security and compliance debt: expand role-boundary browser checks.
UX debt: convert historical screenshot evidence into executable Playwright flows.
Docs debt: continue removing any public wording that implies release status
without current proof.
Install/bootstrap debt: add a first-boot walkthrough that starts the app from a
fresh WSL environment.
Test debt: add regression tests for every release-gate failure class found in
suite recovery.
Operational and release debt: require post-merge CI proof before any status
upgrade.

## 6. Engineering Deep Dive

Verdict: the release-script defect was real and severe; it is fixed in branch.
Strengths: existing test suite is broad, release script centralizes checks, and
version-surface validation already exists.
Findings: `REL-001` and `REL-002` fixed.
Verification gaps: database migration rehearsal was not rerun in this recovery
patch.

### `[CRITICAL] REL-001 Native WSL proof could select Windows Python`

- `Confidence`: High
- `Evidence type`: Mixed
- `Status`: Durable defect fixed

Why it matters:

A Windows interpreter selected from WSL can make a release gate look like Linux
coverage while actually exercising a different platform and dependency set.

Evidence:

- `scripts/verify-release.sh` previously probed `python` before `python3`.
- WSL verification now prints `.venv-wsl/bin/python3` and `linux`.

Blast radius:

- Every release gate using WSL as Linux evidence.

Fix:

- Prefer `python3` before `python`; add regression test coverage.

### `[CRITICAL] REL-002 Release-provenance install mutated the selected Python`

- `Confidence`: High
- `Evidence type`: Mixed
- `Status`: Durable defect fixed

Why it matters:

Installing CivicCore with force reinstall into the selected environment can
pollute a developer machine and hide dependency conflicts.

Evidence:

- Release script now creates `/tmp/civiccode-release-provenance-*` virtualenv
  and removes it afterward.

Blast radius:

- Release verification reliability and local development environments.

Fix:

- Isolated temporary virtualenv for CivicCore provenance test.

## 7. Security And Authorization Deep Dive

Verdict: no secret exposure found in tracked files after cleanup.
Strengths: staff-note public leak tests passed.
Findings: `SEC-001` fixed.
Verification gaps: full authorization browser flow remains for recertification.

### `[MINOR] SEC-001 Secret scanner false positive in staff-note test`

- `Confidence`: High
- `Evidence type`: Static
- `Status`: Durable defect fixed

Why it matters:

False positives train teams to ignore secret scans.

Evidence:

- Test variable renamed from `secret` to `private_note_marker`.
- Tracked-file scan returned no matches.

Blast radius:

- Security scan signal quality.

Fix:

- Rename the fixture variable and keep the non-leak assertion.

## 8. UI/UX Deep Dive

Verdict: changed docs surface now reflects the recovery posture without console
errors or overflow. Strengths: clear release-status section and no stale product
line phrase in rendered copy. Findings: `UX-001` fixed. Verification gaps: full
app user-flow QA is still a recertification task.

### `[MAJOR] UX-001 Recovery copy lacked current browser evidence`

- `Confidence`: High
- `Evidence type`: Runtime
- `Status`: Durable defect fixed

Why it matters:

Release-truth copy is user-facing; it needs the same browser evidence standard
as other UX surfaces.

Evidence:

- Desktop and mobile Playwright screenshots:
  `docs/browser-qa-civiccode-release-recovery-desktop.png` and
  `docs/browser-qa-civiccode-release-recovery-mobile.png`.

Blast radius:

- Public trust in the release-status page.

Fix:

- Added Playwright screenshots and summary.

## 9. Product/PM Deep Dive

Verdict: the branch aligns product posture with evidence. Strengths: explicit
provisional status avoids overclaiming. Findings: no remaining branch blocker.
Verification gaps: public announcement remains blocked until suite recovery
recertification, PR merge, and CI proof.

## 10. Documentation Deep Dive

Verdict: stale active-release-family wording was real and fixed. Strengths:
README, manuals, docs landing page, AGENTS, changelog, and recovery status now
point at provisional release review. Findings: `DOC-001` fixed. Verification
gaps: future docs must keep source-of-truth gates current.

### `[MAJOR] DOC-001 Public docs overclaimed v1 status`

- `Confidence`: High
- `Evidence type`: Static
- `Status`: Durable defect fixed

Why it matters:

Users and auditors rely on public docs to decide whether a city can trust a
module.

Evidence:

- Current-facing docs now describe v1 as under suite-wide release-recovery
  review.

Blast radius:

- README, user manual, docs landing page, changelog, and agent instructions.

Fix:

- Replace current-product-line wording with provisional recovery wording and
  add a docs banlist.

## 11. Install / Bootstrap / Seeding Deep Dive

Verdict: Linux install/release proof is now meaningful. Strengths: WSL venv
install and full release gate passed. Findings: covered by `REL-001` and
`REL-002`. Verification gaps: no fresh Docker/database rehearsal was added in
this branch.

## 12. Version And Release Consistency Deep Dive

Verdict: version surfaces still intentionally say `1.0.0`, while release-status
copy says the label is provisional. Strengths: release script version check
passed. Findings: no unresolved mismatch in this branch. Verification gaps:
post-merge tag/release status must be checked before any public claim changes.

## 13. Test Engineering Deep Dive

Verdict: regression coverage now exists for the exact release-script failure
mode. Strengths: focused Windows tests passed and full WSL release gate passed.
Findings: `TEST-001` fixed. Verification gaps: no full app Playwright test suite
was created in this branch.

### `[MAJOR] TEST-001 Release gate lacked regression tests for WSL interpreter order`

- `Confidence`: High
- `Evidence type`: Static
- `Status`: Durable defect fixed

Why it matters:

Without a test, the same false Linux proof could return in a future cleanup.

Evidence:

- `tests/test_milestone_1_runtime_foundation.py` now asserts `python3` is
  probed before `python`, provenance install uses a temp venv, and force
  reinstall is absent.

Blast radius:

- Every future CivicCode release verification run.

Fix:

- Add regression tests.

## 14. Runtime QA Deep Dive

Verdict: `[AUDITOR-RUN]` WSL verification and browser QA passed. Strengths:
native Linux interpreter proof is explicit. `[DEV-REPORTED]` prior v1 QA remains
treated as historical evidence only.

Verification gaps: post-merge CI is still required.

## 15. Cross-Cutting Synthesis

The root cause was evidence inflation: a release label, docs posture, and WSL
command looked stronger than the proof underneath. The fix is not another
paragraph of caveats; it is a gate that forces native Linux verification,
isolates dependency mutation, bans stale product-line copy, and records browser
evidence when user-facing claims change.

## 16. Verification Gaps And Sign-Off Limits

- Post-merge CI: not available until branch is pushed and PR runs.
- Full application Playwright recertification: outside this branch-level docs
  recovery patch; required before any new public product-ready announcement.
- Fresh deployment proof: intentionally not required by user directive; local
  adversarial mocks and runtime proofs are the standard.
- Docker/database rehearsal: not rerun in this patch because the change did not
  touch DB runtime behavior.
