# CivicCode Sprint 1 Staff Import, Sync, and Operational Browser QA

Run date: 2026-05-07
Target: `node scripts/browser-staff-surfaces-qa.cjs`

| Scenario | Viewport | Status | Evidence | Result |
|---|---:|---:|---|---|
| staff-imports-access-mobile | 390x900 | 403 | phase=empty; main#content=1; skip=1; first focus="Skip to staff import ledger"; fixReadable=true; overflow=false; unexpected console=0; pageErrors=0 | PASS |
| staff-imports-empty-mobile | 390x900 | 200 | phase=empty; main#content=1; skip=1; first focus="Skip to staff import ledger"; fixReadable=true; overflow=false; unexpected console=0; pageErrors=0 | PASS |
| staff-sync-access-mobile | 390x900 | 403 | phase=empty; main#content=1; skip=1; first focus="Skip to staff sync health"; fixReadable=true; overflow=false; unexpected console=0; pageErrors=0 | PASS |
| staff-sync-empty-mobile | 390x900 | 200 | phase=empty; main#content=1; skip=1; first focus="Skip to staff sync health"; fixReadable=true; overflow=false; unexpected console=0; pageErrors=0 | PASS |
| staff-imports-populated-desktop | 1440x1100 | 200 | phase=populated; main#content=1; skip=1; first focus="Skip to staff import ledger"; fixReadable=true; overflow=false; unexpected console=0; pageErrors=0 | PASS |
| staff-imports-populated-mobile | 390x1000 | 200 | phase=populated; main#content=1; skip=1; first focus="Skip to staff import ledger"; fixReadable=true; overflow=false; unexpected console=0; pageErrors=0 | PASS |
| staff-sync-populated-desktop | 1440x1100 | 200 | phase=populated; main#content=1; skip=1; first focus="Skip to staff sync health"; fixReadable=true; overflow=false; unexpected console=0; pageErrors=0 | PASS |
| staff-sync-populated-mobile | 390x1000 | 200 | phase=populated; main#content=1; skip=1; first focus="Skip to staff sync health"; fixReadable=true; overflow=false; unexpected console=0; pageErrors=0 | PASS |

Operational API evidence: status=needs_attention; records=6; network_required=false; external_deployment_required=false; artifact=civiccode-sprint1-operational-state.json

Scoped browser recheck after audit fixes: `node scripts/browser-staff-surfaces-qa.cjs` passed on 2026-05-07 with Chromium across 16 scenarios. This table records the 8 import/sync scenarios from the current committed harness; the code/source scenarios are recorded in `civiccode-sprint1-staff-accessibility-browser-qa.md`.

Result: PASS: needs_attention state renders actionable fixes without requiring external deployment.
