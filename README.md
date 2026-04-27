# CivicCode

**Municipal code and ordinance access for the CivicSuite product family.**

CivicCode is the next CivicSuite planning lane. It will help residents,
staff, clerks, planners, and attorneys ask what the municipal code says about
a topic and receive cited, date-aware answers tied to authoritative code
sections.

## Current status

As of 2026-04-27, CivicCode has a **plain-language summaries foundation**
layered on the staff workbench, citation-grounded Q&A, citation contract,
search and permalink, section/version, source registry, runtime foundation, and
canonical schema foundations: an
installable Python package, a FastAPI app shell, `/` and `/health` endpoints,
an exact `civiccore==0.2.0` dependency pin, canonical SQLAlchemy table
metadata, Alembic migrations under the `civiccode` schema, source registry APIs,
section/version APIs, public-safe text search, stable section permalinks,
deterministic citation/refusal objects, deterministic citation-grounded answers,
staff-only interpretation-note APIs with audit events and staff Q&A context,
and staff-approved plain-language summaries labeled as non-authoritative.

This is deliberately not a legal-advice product and not a live-LLM product yet.
There is no database source persistence, import parser, public lookup UI, live
LLM call, CivicClerk handoff, or legal
determination behavior in this repo yet. Staff interpretation notes are
staff-only and must not be published to public endpoints.

The current deliverable is Milestone 9:

- install and import the package,
- expose health/root endpoints for IT smoke checks,
- run CivicCore migrations before CivicCode migrations,
- create the canonical CivicCode schema tables,
- register official and explicitly non-official source records,
- track source provenance, owner, retrieval method, retrieved timestamp, status,
  and staff notes,
- keep staff-only source notes out of public endpoints,
- create titles, chapters, sections, subsections, and immutable section versions,
- look up current or historical adopted text by section number and effective
  date,
- refuse ambiguous overlapping dates and pending ordinance language with an
  actionable fix path,
- search public-visible adopted section text and related public material
  references,
- expose stable section permalinks that survive text revisions,
- build deterministic citation objects for adopted section text,
- return structured refusals for missing, stale, or contradictory source
  situations,
- answer citation-grounded questions only when one adopted section and active
  source can be cited,
- refuse legal-determination, uncited, ambiguous, missing, stale, or
  contradictory situations with a reason and fix path,
- create staff-only interpretation notes for a code section,
- keep staff interpretation notes out of public lookup, public search, and
  public Q&A responses,
- let staff Q&A responses include approved staff note context with a
  `staff_only_do_not_publish` warning,
- append staff workbench audit events when notes are created,
- create draft plain-language summaries tied to adopted section versions,
- require staff approval before summaries become public,
- label public summaries as `non_authoritative_explanation`,
- keep authoritative code text visible beside approved summaries,
- append audit events when summaries are created and approved,
- keep docs and CI gates green before CivicClerk handoff work begins.

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

Install the CivicCore release wheel first, then install CivicCode in editable
mode:

```bash
python -m pip install https://github.com/CivicSuite/civiccore/releases/download/v0.2.0/civiccore-0.2.0-py3-none-any.whl
python -m pip install -e ".[dev]"
python -m uvicorn civiccode.main:app --reload
```

Smoke checks:

```bash
curl http://127.0.0.1:8000/
curl http://127.0.0.1:8000/health
```

Expected truth today: the service reports `plain-language summaries foundation`,
exposes source registry endpoints under `/api/v1/civiccode/sources`, exposes
section/version and search endpoints under `/api/v1/civiccode/sections` and
`/api/v1/civiccode/search`, exposes deterministic citation objects under
`/api/v1/civiccode/citations/build`, exposes citation-grounded answers under
`/api/v1/civiccode/questions/answer`, exposes staff-only workbench endpoints
under `/api/v1/civiccode/staff`, exposes approved public summaries under
`/api/v1/civiccode/sections/{section_id}/summaries`, and marks successful
answers with `code_answer_behavior=citation_grounded`.

Migration smoke:

```bash
set DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/civiccode
python -m alembic -c civiccode/migrations/alembic.ini upgrade head
```

Expected migration truth today: CivicCore migrations run first, CivicCode uses
`alembic_version_civiccode`, and ten canonical `civiccode.*` tables are created.

Source registry smoke:

```bash
curl http://127.0.0.1:8000/api/v1/civiccode/sources/catalog
```

Expected source-registry truth today: source types include Municode, American
Legal, Code Publishing, General Code, official XML/DOCX exports, official file
drops, and official web scrape/export paths. Source states are `draft`,
`active`, `stale`, `superseded`, and `failed`.

Section/version smoke:

```bash
curl "http://127.0.0.1:8000/api/v1/civiccode/sections/lookup?section_number=6.12.040"
```

Expected section/version truth today: adopted versions can be looked up by
current flag or effective date, pending ordinance language is not treated as
adopted law, and overlapping effective dates return actionable 409 responses.

Search smoke:

```bash
curl "http://127.0.0.1:8000/api/v1/civiccode/search?q=6.12.040"
curl "http://127.0.0.1:8000/api/v1/civiccode/sections/sec_chickens/permalink"
```

Expected search truth today: search returns public-safe structured results and
stable section permalinks. It does not generate answers by itself.

Citation contract smoke:

```bash
curl "http://127.0.0.1:8000/api/v1/civiccode/citations/build?section_number=6.12.040"
```

Expected citation truth today: citation responses are deterministic objects with
section id, version id, source id, effective date, and canonical URL. Refusals
include a reason and fix path.

Citation-grounded Q&A smoke:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/civiccode/questions/answer \
  -H "Content-Type: application/json" \
  -d '{"question":"What does section 6.12.040 say about backyard chickens?","section_number":"6.12.040"}'
```

Expected Q&A truth today: successful answers quote adopted section text, include
one citation object, set `classification=information_not_determination`, set
`llm_provider=not_used`, and state that the answer is not a legal
determination. Code-answer behavior is limited to `citation_grounded` responses.
Legal-advice, uncited, stale, missing, ambiguous, or
contradictory requests return structured refusals.

Staff workbench smoke:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/civiccode/staff/sections/sec_chickens/notes \
  -H "Content-Type: application/json" \
  -H "X-CivicCode-Role: staff" \
  -H "X-CivicCode-Actor: planner@example.gov" \
  -d '{"note_text":"Planning staff treats coop setbacks as measured from the property line.","status":"approved"}'

curl -X POST http://127.0.0.1:8000/api/v1/civiccode/staff/questions/answer \
  -H "Content-Type: application/json" \
  -H "X-CivicCode-Role: staff" \
  -H "X-CivicCode-Actor: planner@example.gov" \
  -d '{"question":"What does section 6.12.040 say about backyard chickens?","section_number":"6.12.040"}'
```

Expected staff-workbench truth today: staff endpoints require
`X-CivicCode-Role: staff` and `X-CivicCode-Actor`, staff interpretation notes
are returned only to staff endpoints, staff Q&A adds `staff_context` with
`staff_only_do_not_publish`, and public lookup, search, and Q&A never expose
staff notes or staff note counts.

Plain-language summary smoke:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/civiccode/staff/sections/sec_chickens/summaries \
  -H "Content-Type: application/json" \
  -H "X-CivicCode-Role: staff" \
  -H "X-CivicCode-Actor: clerk@example.gov" \
  -d '{"summary_id":"summary_chickens","section_version_id":"v_current","summary_text":"In plain language: residents may keep up to six chickens if they get a city permit."}'

curl -X POST http://127.0.0.1:8000/api/v1/civiccode/staff/summaries/summary_chickens/approve \
  -H "X-CivicCode-Role: staff" \
  -H "X-CivicCode-Actor: clerk@example.gov"

curl http://127.0.0.1:8000/api/v1/civiccode/sections/sec_chickens/summaries
```

Expected plain-language truth today: public summaries appear only after staff
approval, are labeled `non_authoritative_explanation`, warn that
plain-language summaries are not law, and include authoritative section text so
the official code remains visible.

## License

Code: Apache License 2.0; see `LICENSE-CODE`.

Documentation: CC BY 4.0 unless otherwise stated; see `LICENSE-DOCS`.
