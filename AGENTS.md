# CivicCode Operating Contract

This repository implements the future CivicCode module: municipal code and
ordinance access for CivicSuite.

## Priority order

1. User experience.
2. Documentation, QA, and tests.
3. Code.

## Current state

This repo is scaffold only. No runtime application exists yet.

Do not add runtime code until Milestone 0 is complete and reviewed.

## Upstream truth

Read these before any milestone work:

- `CivicSuite/civicsuite/docs/CivicSuiteUnifiedSpec.md`, especially section 11.
- `CivicSuite/civicsuite/docs/roadmap/civiccode-next-module-plan.md`.
- `CivicSuite/civicsuite/specs/01_catalog.md`, CivicCode section.
- Suite ADRs in `CivicSuite/civicsuite/docs/architecture/`.

## CivicCore placeholder warning

Do not import from planned CivicCore placeholder packages unless that package
has shipped in a versioned CivicCore release. Placeholder imports can appear to
work because empty packages exist, but relying on them is a defect.

## CivicCode non-negotiables

These must become tests before runtime behavior ships:

- Exact citations: every code answer cites title/chapter/section/subsection.
- No legal advice: resident-facing answers route legal interpretation to staff.
- Source precedence: official codifier/source text beats summaries and notes.
- Version context: answers know the effective date of the section being cited.
- Ambiguity refusal: missing, stale, or contradictory source text causes a
  helpful refusal, not a guess.
- Plain-language boundary: summaries are labeled non-authoritative.
- Audit trail: imports, summaries, answers, and section changes are recorded.
- Air-gap posture: local runtime only; no required outbound calls.

## Milestones

Milestone 0 is reconciliation only:

1. Read upstream spec and ADRs.
2. Add `docs/RECONCILIATION.md`.
3. Queue ADRs for open questions.
4. Add `docs/MILESTONES.md`.
5. Keep docs verification green.
6. Do not add runtime code.

Runtime milestones start only after Milestone 0 is reviewed.

## Prohibitions

- Do not promote planned behavior as shipped.
- Do not create a second source of truth for the suite spec.
- Do not import from unreleased CivicCore placeholders.
- Do not add frontend code without browser QA evidence.
- Do not say done without verification output.
- Do not edit umbrella compatibility docs from this repo.
