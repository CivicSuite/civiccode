# CivicCode

**Municipal code and ordinance access for the CivicSuite product family.**

CivicCode is the next CivicSuite planning lane. It will help residents,
staff, clerks, planners, and attorneys ask what the municipal code says about
a topic and receive cited, date-aware answers tied to authoritative code
sections.

## Current status

As of 2026-04-27, CivicCode has a **source registry foundation** layered on the
runtime foundation and canonical schema foundation: an installable Python
package, a FastAPI app shell, `/` and `/health` endpoints, an exact
`civiccore==0.2.0` dependency pin, canonical SQLAlchemy table metadata, Alembic
migrations under the `civiccode` schema, and staff/public APIs for registering
official municipal-code sources before any code-answer behavior exists.

This is deliberately not the code-answer product yet. There is no database
source persistence, import parser, section/version workflow, search, citation
engine, Q&A workflow, public lookup UI, or LLM/code-answer behavior in this repo
yet.

The current deliverable is Milestone 3:

- install and import the package,
- expose health/root endpoints for IT smoke checks,
- run CivicCore migrations before CivicCode migrations,
- create the canonical CivicCode schema tables,
- register official and explicitly non-official source records,
- track source provenance, owner, retrieval method, retrieved timestamp, status,
  and staff notes,
- keep staff-only source notes out of public endpoints,
- tell users plainly that code answers are not available yet,
- keep docs and CI gates green before section/version lifecycle work begins.

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

Expected truth today: the service reports `source registry foundation`, exposes
source registry endpoints under `/api/v1/civiccode/sources`, and
`code_answer_behavior` remains `not_available`.

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

## License

Code: Apache License 2.0; see `LICENSE-CODE`.

Documentation: CC BY 4.0 unless otherwise stated; see `LICENSE-DOCS`.
