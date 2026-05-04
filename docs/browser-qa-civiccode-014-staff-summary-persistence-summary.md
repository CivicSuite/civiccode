# Browser QA - CivicCode v0.1.14 Staff Guidance Persistence Docs

Date: 2026-05-04

Surface checked: `docs/index.html`

Evidence:

- Desktop screenshot: `docs/browser-qa-civiccode-014-staff-summary-persistence-desktop.png`
- Mobile screenshot: `docs/browser-qa-civiccode-014-staff-summary-persistence-mobile.png`
- CDP metrics: `docs/browser-qa-civiccode-014-staff-summary-persistence-cdp.json`

Results:

- Desktop viewport `1440x1200`: no horizontal overflow, zero console/log events, skip link focus lands on `Skip to CivicCode content`.
- Mobile viewport `390x1000`: no horizontal overflow, zero console/log events, skip link focus lands on `Skip to CivicCode content`.
- Copy review confirmed `CivicCode v0.1.14`, durable staff-note storage, and durable plain-language summary storage are visible in the rendered page.
- Accessibility spot check confirmed the existing skip link remains keyboard-focusable and visible on focus.
