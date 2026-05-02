# Staff Code Workspace Browser QA

- Target: `/staff/code` generated from the FastAPI app for access-required, empty, and populated/blocker states.
- Viewports: desktop 1440x1000 and mobile 390x1100.
- Accessibility spot-check: focus-visible CSS present in every state; focusable controls/links counted; no keyboard trap detected by static focusable scan.

- access-required desktop: checks=true, focusVisible=true, focusables=1, console events=0, page errors=0, screenshot=browser-qa-staff-code-access-required-desktop.png
- access-required mobile: checks=true, focusVisible=true, focusables=1, console events=0, page errors=0, screenshot=browser-qa-staff-code-access-required-mobile.png
- empty desktop: checks=true, focusVisible=true, focusables=1, console events=0, page errors=0, screenshot=browser-qa-staff-code-empty-desktop.png
- empty mobile: checks=true, focusVisible=true, focusables=1, console events=0, page errors=0, screenshot=browser-qa-staff-code-empty-mobile.png
- populated desktop: checks=true, focusVisible=true, focusables=2, console events=0, page errors=0, screenshot=browser-qa-staff-code-populated-desktop.png
- populated mobile: checks=true, focusVisible=true, focusables=2, console events=0, page errors=0, screenshot=browser-qa-staff-code-populated-mobile.png
