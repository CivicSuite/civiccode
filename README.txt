CivicCode
=========

Municipal code and ordinance access for the CivicSuite product family.

Current status
--------------

As of 2026-04-27, CivicCode has a public code lookup surface built on the
CivicClerk handoff foundation,
plain-language summaries foundation, staff workbench foundation,
citation-grounded Q&A foundation, citation contract foundation, search and permalink foundation, section/version
foundation, source registry foundation, runtime foundation, and canonical
schema foundation. The package can
be installed, the FastAPI app can start, / plus /health are available for IT
smoke checks, Alembic can create the canonical civiccode schema tables after
CivicCore migrations run, staff can register official source records, staff can
create titles, chapters, sections, and adopted or pending section versions,
public-safe search/permalink APIs are available, deterministic citation or
refusal objects can be built, and citation-grounded questions can be answered
when one adopted section and active source can be cited. Staff-only
interpretation notes, staff Q&A context, and staff workbench audit events are
available behind the trusted staff header seam.
Staff-approved plain-language summaries are available after review, are labeled
non-authoritative, and keep authoritative code text visible.
CivicClerk ordinance/adoption handoff events are accepted as pending
codification warnings without replacing adopted code text. Residents can open
/civiccode, search by section number or plain-language phrase, read adopted
code text, see citations, view approved summaries, and see pending
codification warnings.

This is not a legal-advice product and does not make live LLM calls. There is
no source persistence, import parser, live LLM-backed frontend workflow,
live LLM calls, automatic ordinance codification, or legal determination
behavior yet. Staff notes are not public. Summaries are not law. Pending
ordinance language is not adopted law. Source,
section/version, search, permalink, citation-contract, citation-grounded Q&A,
and staff workbench behavior exists so authoritative text can be found, cited,
and annotated internally without uncited public answers. Code answers are
limited to citation_grounded responses.

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
6. create staff notes with X-CivicCode-Role: staff and X-CivicCode-Actor

Migration smoke
---------------

1. set DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/civiccode
2. python -m alembic -c civiccode/migrations/alembic.ini upgrade head

Next work
---------

Milestone 12: import and connector hardening.
