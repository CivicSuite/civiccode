CivicCode
=========

Municipal code and ordinance access for the CivicSuite product family.

Current status
--------------

As of 2026-04-27, CivicCode has a schema foundation built on the runtime foundation
from Milestone 1. The package can be installed, the FastAPI app can
start, / plus /health are available for IT smoke checks, and Alembic can create
the canonical civiccode schema tables after CivicCore migrations run.

This is not the code-answer product yet. There is no database schema, no
source registry API, no frontend workflow, no LLM workflow, and no code answers
yet. The schema exists; source registry behavior starts in Milestone 3.

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

Migration smoke
---------------

1. set DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/civiccode
2. python -m alembic -c civiccode/migrations/alembic.ini upgrade head

Next work
---------

Milestone 3: official source registry.
