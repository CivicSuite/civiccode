CivicCode
=========

Municipal code and ordinance access for the CivicSuite product family.

Current status
--------------

As of 2026-05-03, CivicCode has a Docker-demo codifier runtime layered on the
mock-city codifier contract suite, staff code lifecycle workspace,
records-ready export and accessibility
hardening foundation, local import foundation, public code lookup
surface, CivicClerk handoff foundation,
plain-language summaries foundation, staff workbench foundation,
citation-grounded Q&A foundation, citation contract foundation, search and permalink foundation, section/version
foundation, database-backed source registry foundation, runtime foundation, and canonical
schema foundation. The package can
be installed, the FastAPI app can start, / plus /health are available for IT
smoke checks, Alembic can create the canonical civiccode schema tables after
CivicCore migrations run, staff can register official source records, persist
source records with CIVICCODE_SOURCE_REGISTRY_DB_URL when configured, staff can
create titles, chapters, sections, and adopted or pending section versions,
public-safe search/permalink APIs are available, deterministic citation or
refusal objects can be built, and citation-grounded questions can be answered
when one adopted section and active source can be cited. Staff-only
interpretation notes, staff Q&A context, and staff workbench audit events are
available behind the trusted staff header seam.
Staff-approved plain-language summaries are available after review, are labeled
non-authoritative, and keep authoritative code text visible.
Local CSV/file-drop bundle and official HTML extract imports are available
through staff-only endpoints, with job status, retry, and provenance report
behavior. CivicClerk ordinance/adoption handoff events are accepted as pending
codification warnings without replacing adopted code text. Residents can open
/civiccode, search by section number or plain-language phrase, read adopted
code text, see citations, view approved summaries, and see pending
codification warnings. Docker Compose can start PostgreSQL 17 with pgvector,
run migrations, serve the FastAPI app, persist source registry records, and
seed a City of Brookfield demo with CIVICCODE_DEMO_SEED=1.

This is not a legal-advice product and does not make live LLM calls. The
staff-controlled codifier sync foundation can validate schedules and source
hosts, plan delta requests, run already-fetched local payloads through the
import path, and show CivicCore circuit-breaker health. There is no
CivicAccess runtime dependency, live LLM-backed frontend workflow, live LLM
calls, bundled vendor credentials, automatic ordinance codification, or legal
determination behavior yet.
Staff notes are not public. Summaries are not law. Pending ordinance language is not adopted law. Source,
section/version, search, permalink, citation-contract, citation-grounded Q&A,
staff workbench, and local import behavior exists so authoritative text can be
found, cited, imported from local fixtures, and annotated internally without
uncited public answers. Code answers are limited to citation_grounded responses.

Local import truth today
------------------------

Staff can submit local CSV/file-drop bundles and official HTML extract fixtures
to /api/v1/civiccode/staff/imports/local-bundle. Completed imports populate the
in-memory source/title/chapter/section/version tree. Failed imports remain
visible through staff endpoints with an actionable fix path. Re-importing the
same bundle is idempotent. Provenance report endpoints expose source metadata,
fixture checksums, and a no-outbound-dependency marker. Redis/Celery workers
and vendor credentials are not required for local import.

Codifier sync foundation truth today
------------------------------------

Staff can configure active official codifier sources at
/api/v1/civiccode/staff/sync/codifier-sources, validate cron schedules and
SSRF-safe source hosts, view next-run and circuit-breaker health, plan delta
requests, and run already-fetched local payloads through the import path.
CivicCode does not ship vendor credentials, make outbound calls from the
foundation smoke, or automatically codify ordinances.

Mock-city codifier contract truth today
---------------------------------------

Run:

python scripts/run_mock_city_environment_suite.py --output .tmp-civiccode-mock-city-report.json

The suite validates secret-free Municode, American Legal Publishing, Code
Publishing Company, and General Code source contracts through the local import
path without outbound vendor calls. It renders planned delta URLs for future
codifier sync foundation and reuses CivicCore municipal IdP and backup-retention
mock-city contracts so later modules can reuse the same environment pattern.

Records-ready export truth today
--------------------------------

Public adopted sections can be exported through
/api/v1/civiccode/sections/{section}/export and
/civiccode/sections/{section}/export. The export includes authoritative text,
version metadata, deterministic citation, source provenance, retrieval
metadata, accessibility labels, semantic headings, and legal-boundary copy.
CivicAccess is planned infrastructure, not a shipped runtime dependency.

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

1. python -m pip install https://github.com/CivicSuite/civiccore/releases/download/v0.22.0/civiccore-0.22.0-py3-none-any.whl
2. python -m pip install -e ".[dev]"
3. python -m uvicorn civiccode.main:app --reload
4. curl http://127.0.0.1:8000/health
5. curl http://127.0.0.1:8000/api/v1/civiccode/sources/catalog
6. create staff notes with X-CivicCode-Role: staff and X-CivicCode-Actor

Docker demo
-----------

1. cp docker.env.example .env
2. docker compose up --build
3. open http://127.0.0.1:8000/civiccode
4. search for 6.12.040 to see the seeded City of Brookfield code section
5. bash scripts/docker-demo-smoke.sh

The default Docker password is local-demo only. Change .env before any shared
environment.

Migration smoke
---------------

1. set DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/civiccode
2. python -m alembic -c civiccode/migrations/alembic.ini upgrade head
3. set CIVICCODE_SOURCE_REGISTRY_DB_URL=sqlite:///civiccode-sources.db before source persistence smoke checks

Release
-------

CivicCode v0.1.9 is the current Docker demo runtime release. It reuses the
shared CivicCore source-list health projection for codifier sync source lists
while retaining CivicCode-specific legal-boundary copy.
