# CivicCode Sprint 1 Staff Import, Sync, and Operational Browser QA

Run date: 2026-05-07
Target: http://127.0.0.1:18021

| Scenario | Viewport | Status | Evidence | Result |
|---|---:|---:|---|---|
| staff-imports-access-desktop | 1440x1100 | 403 | main#content=1; skip=1; first focus="Skip to staff import ledger"; fix copy=true; overflow=false; unexpected console=0; pageErrors=0; screenshot=staff-imports-access-desktop.png | PASS |
| staff-imports-empty-mobile | 390x900 | 200 | main#content=1; skip=1; first focus="Skip to staff import ledger"; fix copy=true; overflow=false; unexpected console=0; pageErrors=0; screenshot=staff-imports-empty-mobile.png | PASS |
| staff-sync-access-desktop | 1440x1100 | 403 | main#content=1; skip=1; first focus="Skip to staff sync health"; fix copy=true; overflow=false; unexpected console=0; pageErrors=0; screenshot=staff-sync-access-desktop.png | PASS |
| staff-sync-empty-mobile | 390x900 | 200 | main#content=1; skip=1; first focus="Skip to staff sync health"; fix copy=true; overflow=false; unexpected console=0; pageErrors=0; screenshot=staff-sync-empty-mobile.png | PASS |
| staff-imports-populated-desktop | 1440x1300 | 200 | main#content=1; skip=1; first focus="Skip to staff import ledger"; fix copy=true; overflow=false; unexpected console=0; pageErrors=0; screenshot=staff-imports-populated-desktop.png | PASS |
| staff-imports-populated-mobile | 390x1000 | 200 | main#content=1; skip=1; first focus="Skip to staff import ledger"; fix copy=true; overflow=false; unexpected console=0; pageErrors=0; screenshot=staff-imports-populated-mobile.png | PASS |
| staff-sync-populated-desktop | 1440x1300 | 200 | main#content=1; skip=1; first focus="Skip to staff sync health"; fix copy=true; overflow=false; unexpected console=0; pageErrors=0; screenshot=staff-sync-populated-desktop.png | PASS |
| staff-sync-populated-mobile | 390x1000 | 200 | main#content=1; skip=1; first focus="Skip to staff sync health"; fix copy=true; overflow=false; unexpected console=0; pageErrors=0; screenshot=staff-sync-populated-mobile.png | PASS |

Operational API evidence: status=needs_attention; records=6; network_required=false; external_deployment_required=false; artifact=civiccode-sprint1-operational-state.json

Scoped browser recheck after audit fixes: `node scripts/browser-staff-surfaces-qa.cjs` passed on 2026-05-07 with mock-city seed, Chromium, mobile access pages, desktop staff workspaces, skip-link checks, `main#content` checks, console/page-error checks, horizontal-overflow checks, and `.fix-path` readability checks.

Result: PASS: needs_attention state renders actionable fixes without requiring external deployment.
