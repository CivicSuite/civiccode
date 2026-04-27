# CivicCode User Manual

CivicCode currently ships a citation-grounded Q&A foundation built on the
citation contract foundation, search and permalink foundation, section/version foundation, source registry
foundation, runtime foundation, and canonical schema foundation. This manual
explains what a first-time installer can do today and what is still planned.

## For municipal decision-makers

CivicCode is planned to make municipal code easier to search, cite, and
explain. It will not replace the city's official codifier and will not provide
legal advice. The goal is to help residents and staff find exact code sections
and understand next steps.

Current truth:

- the Python package can be installed,
- the FastAPI app can be started,
- `/` explains the current product boundary,
- `/health` reports service, CivicCode version, and CivicCore version,
- Alembic can create ten canonical `civiccode.*` tables after CivicCore
  migrations run,
- staff can register source records for official and explicitly non-official
  municipal code materials,
- public source endpoints do not expose staff-only notes,
- staff can create titles, chapters, sections, subsections, and immutable
  section versions,
- current and historical lookup returns adopted law only,
- pending ordinance language and ambiguous overlapping effective dates return
  actionable errors instead of being treated as settled law,
- public-safe search can find adopted section text and related public material
  references,
- stable section permalinks remain the same across text revisions,
- deterministic citation objects can be built from adopted section text,
- citation refusals include reasons and fix paths for missing, stale, or
  contradictory source situations,
- citation-grounded questions can be answered when they resolve to one adopted
  section and one active source,
- legal-determination, uncited, stale, missing, ambiguous, or contradictory
  questions return structured refusals,
- no frontend exists yet,
- no live LLM calls or legal determinations are generated yet.

For a non-technical user, there is not yet a public product workflow. The
honest experience today is an IT smoke test that proves the module can start
and that source, section/version, citation, and citation-grounded Q&A records
can be exercised before import and public lookup work begins.

## For IT and technical staff

This repo currently contains the Milestone 7 citation-grounded Q&A foundation plus
documentation and verification gates. Runtime implementation must follow the
CivicSuite pattern:

- standalone module repo under `CivicSuite/`,
- exact `civiccore==0.2.0` dependency pin,
- local LLM only through `civiccore.llm`,
- no cloud dependency,
- no imports from unreleased CivicCore placeholder packages.

Install and run:

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

Run migrations:

```bash
set DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/civiccode
python -m alembic -c civiccode/migrations/alembic.ini upgrade head
```

The migration chain runs CivicCore first and stores CivicCode's revision in
`alembic_version_civiccode`.

Inspect source-registry vocabulary:

```bash
curl http://127.0.0.1:8000/api/v1/civiccode/sources/catalog
```

Register an official source:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/civiccode/sources \
  -H "Content-Type: application/json" \
  -d '{
    "source_id": "municode_current",
    "name": "Example Municipal Code",
    "publisher": "Municode",
    "source_type": "municode",
    "source_category": "municipal_code",
    "source_url": "https://library.municode.com/example/codes/code_of_ordinances",
    "retrieved_at": "2026-04-27T12:00:00Z",
    "retrieval_method": "official_web_export",
    "source_owner": "City Clerk",
    "is_official": true,
    "status": "active"
  }'
```

The registry accepts `draft`, `active`, `stale`, `superseded`, and `failed`
source states. `active` official sources require source owner and retrieval
metadata. `active` non-official sources require an explicit non-official note.
Stale and failed sources return actionable fix guidance.

Create section structure:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/civiccode/titles \
  -H "Content-Type: application/json" \
  -d '{"title_id":"title_6","title_number":"6","title_name":"Animals"}'

curl -X POST http://127.0.0.1:8000/api/v1/civiccode/chapters \
  -H "Content-Type: application/json" \
  -d '{"chapter_id":"chapter_6_12","title_id":"title_6","chapter_number":"6.12","chapter_name":"Urban Livestock"}'

curl -X POST http://127.0.0.1:8000/api/v1/civiccode/sections \
  -H "Content-Type: application/json" \
  -d '{"section_id":"sec_chickens","chapter_id":"chapter_6_12","section_number":"6.12.040","section_heading":"Backyard chickens"}'
```

Create adopted text:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/civiccode/sections/sec_chickens/versions \
  -H "Content-Type: application/json" \
  -d '{
    "version_id": "v_current",
    "section_id": "sec_chickens",
    "source_id": "municode_current",
    "version_label": "Current",
    "body": "Up to six hens are allowed with a permit.",
    "effective_start": "2026-01-01",
    "status": "adopted",
    "is_current": true
  }'
```

Lookup current adopted text:

```bash
curl "http://127.0.0.1:8000/api/v1/civiccode/sections/lookup?section_number=6.12.040"
```

The lookup response is still not a code answer. It returns structured section
and version data with `code_answer_behavior=not_available`.

Search public-safe section data:

```bash
curl "http://127.0.0.1:8000/api/v1/civiccode/search?q=chickens"
```

Read a stable section permalink:

```bash
curl "http://127.0.0.1:8000/api/v1/civiccode/sections/sec_chickens/permalink"
```

Search results distinguish code sections from related administrative
regulations, resolutions, policies, and approved summaries when those public
references exist. Empty search results include a fix path such as trying an
exact section number or fewer words.

Build a deterministic citation object:

```bash
curl "http://127.0.0.1:8000/api/v1/civiccode/citations/build?section_number=6.12.040"
```

Citation objects include section id, version id, source id, effective date, and
canonical URL. If the source is missing, stale, contradictory, or ambiguous, the
response is a structured refusal with a reason and fix path.

Ask a citation-grounded code question:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/civiccode/questions/answer \
  -H "Content-Type: application/json" \
  -d '{"question":"What does section 6.12.040 say about backyard chickens?","section_number":"6.12.040"}'
```

Code-answer behavior is limited to citation-grounded responses. The Q&A harness returns an answer only when it can attach one deterministic
citation to adopted code text. It refuses legal determinations, uncited
questions, missing sections, stale sources, and contradictory effective-date
windows with a reason and fix path. It sets `llm_provider=not_used` because
Milestone 7 is a deterministic harness, not a live LLM integration.

## Architecture reference

Planned dependency direction:

```text
civicsuite docs/governance
        |
        v
civiccore shared platform
        |
        v
civiccode municipal-code module
        |
        v
future consumers: civiczone, civiclegal, civicaccess, civiccomms
```

The next runtime design step is Milestone 8: staff workbench foundation.
