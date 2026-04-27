# CivicCode

**Municipal code and ordinance access for the CivicSuite product family.**

CivicCode is the next CivicSuite planning lane. It will help residents,
staff, clerks, planners, and attorneys ask what the municipal code says about
a topic and receive cited, date-aware answers tied to authoritative code
sections.

## Current status

As of 2026-04-27, this repository is a **scaffold only**. No runtime
application code has shipped. There is no FastAPI app, no database schema, no
frontend, and no LLM workflow in this repo yet.

The current deliverable is Milestone 0 planning:

- reconcile this repo against the upstream CivicSuite unified spec,
- queue ADRs before runtime choices harden,
- define the test-first milestone plan,
- install docs and CI gates.

## Why CivicCode before CivicZone

CivicZone remains the first major Tier 2 land-use product, but it needs an
authoritative municipal-code source before it can safely answer zoning
questions. CivicCode is that Tier 1 dependency: it owns code sections,
versions, citations, plain-language summaries, and ordinance-adoption context.

## Product promise

CivicCode will:

- ingest municipal code sources from a city's official publisher,
- preserve title/chapter/section/subsection structure,
- track section versions and effective dates,
- answer natural-language code questions with exact citations,
- label plain-language explanations as non-authoritative,
- route legal-interpretation questions to staff,
- receive ordinance/adoption events from CivicClerk when that contract is
  defined.

## Non-goals

CivicCode is not:

- a codifier,
- legal advice,
- automatic ordinance codification,
- automatic legal interpretation,
- CivicZone runtime work,
- a resident portal shell.

## Source of truth

Read these upstream documents first:

1. `CivicSuite/civicsuite/docs/CivicSuiteUnifiedSpec.md`, section 11.
2. `CivicSuite/civicsuite/docs/roadmap/civiccode-next-module-plan.md`.
3. `CivicSuite/civicsuite/specs/01_catalog.md`, "CivicCode - Municipal Code & Ordinance Access."

## Development status

There is nothing to run yet. The first implementation milestone must start
with tests, docs, and ADRs before runtime code.

## License

Code: Apache License 2.0; see `LICENSE-CODE`.

Documentation: CC BY 4.0 unless otherwise stated; see `LICENSE-DOCS`.
