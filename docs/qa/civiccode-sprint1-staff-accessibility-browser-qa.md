# CivicCode Sprint 1 Staff Accessibility Browser QA

Run date: 2026-05-07
Target: `node scripts/browser-staff-surfaces-qa.cjs`

| Scenario | Viewport | Status | Evidence | Result |
|---|---:|---:|---|---|
| staff-code-access-mobile | 390x900 | 403 | phase=empty; main#content=1; skip=1; first focus="Skip to staff code workspace"; fixReadable=true; overflow=false; unexpected console=0; pageErrors=0 | PASS |
| staff-code-empty-mobile | 390x900 | 200 | phase=empty; main#content=1; skip=1; first focus="Skip to staff code workspace"; fixReadable=true; overflow=false; unexpected console=0; pageErrors=0 | PASS |
| staff-code-workspace-desktop | 1440x1100 | 200 | phase=populated; main#content=1; skip=1; first focus="Skip to staff code workspace"; fixReadable=true; overflow=false; unexpected console=0; pageErrors=0 | PASS |
| staff-code-workspace-mobile | 390x900 | 200 | phase=populated; main#content=1; skip=1; first focus="Skip to staff code workspace"; fixReadable=true; overflow=false; unexpected console=0; pageErrors=0 | PASS |
| staff-sources-access-mobile | 390x900 | 403 | phase=empty; main#content=1; skip=1; first focus="Skip to staff source registry"; fixReadable=true; overflow=false; unexpected console=0; pageErrors=0 | PASS |
| staff-sources-empty-mobile | 390x900 | 200 | phase=empty; main#content=1; skip=1; first focus="Skip to staff source registry"; fixReadable=true; overflow=false; unexpected console=0; pageErrors=0 | PASS |
| staff-sources-workspace-desktop | 1440x1100 | 200 | phase=populated; main#content=1; skip=1; first focus="Skip to staff source registry"; fixReadable=true; overflow=false; unexpected console=0; pageErrors=0 | PASS |
| staff-sources-workspace-mobile | 390x900 | 200 | phase=populated; main#content=1; skip=1; first focus="Skip to staff source registry"; fixReadable=true; overflow=false; unexpected console=0; pageErrors=0 | PASS |

Scoped browser recheck after audit fixes: `node scripts/browser-staff-surfaces-qa.cjs` passed on 2026-05-07 with Chromium across 16 scenarios. This table records the 8 code/source scenarios from the current committed harness; the import/sync scenarios are recorded in `civiccode-sprint1-ops-surfaces-browser-qa.md`.

Result: PASS
