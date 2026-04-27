CivicCode
=========

Municipal code and ordinance access for the CivicSuite product family.

Current status
--------------

As of 2026-04-27, CivicCode has a search and permalink foundation built on the
section/version foundation, source registry foundation, runtime foundation, and
canonical schema foundation. The package can be installed, the FastAPI app can
start, / plus /health are available for IT smoke checks, Alembic can create the
canonical civiccode schema tables after CivicCore migrations run, staff can
register official source records, staff can create titles, chapters, sections,
and adopted or pending section versions, and public-safe search/permalink APIs
are available.

This is not the code-answer product yet. There is no source persistence, import
parser, frontend workflow, LLM workflow, citation engine, or code answers yet.
Source, section/version, search, and permalink behavior exists so authoritative
text can be found before any answer surface is enabled.

CivicCode is the next planning lane because CivicZone needs an authoritative
municipal-code source before zoning runtime work begins.

Source of truth
---------------

1. CivicSuite/civicsuite/docs/CivicSuiteUnifiedSpec.md, section 11.
2. CivicSuite/civicsuite/docs/roadmap/civiccode-next-module-plan.md.
3. CivicSuite/civicsuite/specs/01_catalog.md, CivicCode section.

License
-------

Code: Apache License 2.0; see LICENSE-CODE.
Documentation: CC BY 4.0 unless otherwise stated; see LICENSE-DOCS.

Run locally
-----------

1. python -m pip install https://github.com/CivicSuite/civiccore/releases/download/v0.2.0/civiccore-0.2.0-py3-none-any.whl
2. python -m pip install -e ".[dev]"
3. python -m uvicorn civiccode.main:app --reload
4. curl http://127.0.0.1:8000/health
5. curl http://127.0.0.1:8000/api/v1/civiccode/sources/catalog

Migration smoke
---------------

1. set DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/civiccode
2. python -m alembic -c civiccode/migrations/alembic.ini upgrade head

Next work
---------

Milestone 6: citation contract.
