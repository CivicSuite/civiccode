# CivicCode Sprint 1 Staff Accessibility Browser QA

Run date: 2026-05-07
Target: http://127.0.0.1:18020

| Scenario | Viewport | Status | Evidence | Result |
|---|---:|---:|---|---|
| staff-code-access-desktop | 1440x1100 | 403 | main#content=1; skip=1; first focus="Skip to staff code workspace"; fix copy=true; overflow=false; expected denied console=1; unexpected console=0; pageErrors=0; screenshot=staff-code-access-desktop.png | PASS |
| staff-code-access-mobile | 390x900 | 403 | main#content=1; skip=1; first focus="Skip to staff code workspace"; fix copy=true; overflow=false; expected denied console=1; unexpected console=0; pageErrors=0; screenshot=staff-code-access-mobile.png | PASS |
| staff-code-workspace-desktop | 1440x1100 | 200 | main#content=1; skip=1; first focus="Skip to staff code workspace"; fix copy=true; overflow=false; expected denied console=0; unexpected console=0; pageErrors=0; screenshot=staff-code-workspace-desktop.png | PASS |
| staff-code-workspace-mobile | 390x900 | 200 | main#content=1; skip=1; first focus="Skip to staff code workspace"; fix copy=true; overflow=false; expected denied console=0; unexpected console=0; pageErrors=0; screenshot=staff-code-workspace-mobile.png | PASS |
| staff-sources-access-desktop | 1440x1100 | 403 | main#content=1; skip=1; first focus="Skip to staff source registry"; fix copy=true; overflow=false; expected denied console=1; unexpected console=0; pageErrors=0; screenshot=staff-sources-access-desktop.png | PASS |
| staff-sources-access-mobile | 390x900 | 403 | main#content=1; skip=1; first focus="Skip to staff source registry"; fix copy=true; overflow=false; expected denied console=1; unexpected console=0; pageErrors=0; screenshot=staff-sources-access-mobile.png | PASS |
| staff-sources-workspace-desktop | 1440x1100 | 200 | main#content=1; skip=1; first focus="Skip to staff source registry"; fix copy=true; overflow=false; expected denied console=0; unexpected console=0; pageErrors=0; screenshot=staff-sources-workspace-desktop.png | PASS |
| staff-sources-workspace-mobile | 390x900 | 200 | main#content=1; skip=1; first focus="Skip to staff source registry"; fix copy=true; overflow=false; expected denied console=0; unexpected console=0; pageErrors=0; screenshot=staff-sources-workspace-mobile.png | PASS |

Scoped browser recheck after audit fixes: `node scripts/browser-staff-surfaces-qa.cjs` passed on 2026-05-07 with mock-city seed, Chromium, mobile access pages, desktop staff workspaces, skip-link checks, `main#content` checks, console/page-error checks, horizontal-overflow checks, and `.fix-path` readability checks.

Result: PASS
