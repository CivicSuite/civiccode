# CivicCode Release-Recovery Browser QA

Date: 2026-05-07
Scope: `docs/index.html` release-status copy after the suite-wide release
recovery claim freeze.

## Playwright Walkthrough

| Viewport | Evidence | Result |
| --- | --- | --- |
| Desktop 1440x1000 | `docs/browser-qa-civiccode-release-recovery-desktop.png` | Passed |
| Mobile 390x844 | `docs/browser-qa-civiccode-release-recovery-mobile.png` | Passed |

## Checks

- Page title rendered as `CivicCode - CivicSuite municipal code module`.
- Primary heading rendered as `CivicCode`.
- Release-recovery wording was visible in both viewports.
- Stale active-product wording was absent from the rendered page.
- Browser console messages: none.
- Page errors: none.
- Horizontal overflow: none.
- Keyboard focus check: first `Tab` reached a link.

## Boundary

This QA pass verifies the changed public documentation surface. It does not
recertify CivicCode as a product-ready release; that status depends on the full
suite recovery gates and post-merge CI.
