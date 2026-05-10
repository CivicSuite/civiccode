# Demotion Browser QA - 2026-05-10

Module: civiccode
Route: /civiccode
Expected visible recovery label: 

Checks completed:

- Desktop viewport 1365x900 rendered and screenshot captured.
- Mobile viewport 390x844 rendered and screenshot captured.
- Browser console/pageerror listeners recorded during both renders.
- Visible page text rendered non-empty; version truth is covered by API/tests because this route does not display a version badge.

Artifacts:

- desktop.png
- desktop-console.txt
- mobile.png
- mobile-console.txt