CivicCode
=========

Municipal code and ordinance access for the CivicSuite product family.

Current status
--------------

As of 2026-04-27, CivicCode has a records-ready export and accessibility
hardening foundation built on the local import foundation, public code lookup
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
codification warnings.

This is not a legal-advice product and does not make live LLM calls. There is
no live codifier sync,
CivicAccess runtime dependency, live LLM-backed frontend workflow, live LLM
calls, automatic ordinance codification, or legal determination behavior yet.
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
and live codifier sync are not required in this milestone.

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

1. python -m pip install https://github.com/CivicSuite/civiccore/releases/download/v0.3.0/civiccore-0.3.0-py3-none-any.whl
2. python -m pip install -e ".[dev]"
3. python -m uvicorn civiccode.main:app --reload
4. curl http://127.0.0.1:8000/health
5. curl http://127.0.0.1:8000/api/v1/civiccode/sources/catalog
6. create staff notes with X-CivicCode-Role: staff and X-CivicCode-Actor

Migration smoke
---------------

1. set DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/civiccode
2. python -m alembic -c civiccode/migrations/alembic.ini upgrade head
3. set CIVICCODE_SOURCE_REGISTRY_DB_URL=sqlite:///civiccode-sources.db before source persistence smoke checks

Release
-------

CivicCode v0.1.1 is the current dependency-alignment release.
