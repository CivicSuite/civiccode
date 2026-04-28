# Browser QA: CivicCode v0.1.1 Alignment

## Target

- Page: `docs/index.html`
- Change: current release/dependency wording now states CivicCode v0.1.1 and `civiccore==0.3.0`.

## Evidence

- Desktop screenshot: `docs/browser-qa-civiccode-v0.1.1-alignment-desktop.png` (317,504 bytes)
- Mobile screenshot: `docs/browser-qa-civiccode-v0.1.1-alignment-mobile.png` (143,797 bytes)

## Checks

- Desktop and mobile render without obvious clipping or missing content.
- Landing page still separates shipped behavior from planned behavior.
- Current "What ships today" dependency line shows `civiccore==0.3.0`.
- Current next-step copy shows CivicCode v0.1.1 as the dependency-alignment release.
- Console errors: 0 observed during the headless render pass.
