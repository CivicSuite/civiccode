# CivicCode User Manual

CivicCode currently ships a section/version foundation built on the source registry
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
- no frontend exists yet,
- no LLM answers or code-answer behavior are generated yet.

For a non-technical user, there is not yet a public product workflow. The
honest experience today is an IT smoke test that proves the module can start
and that source and section/version records can be registered before import,
search, citation, and public lookup work begins.

## For IT and technical staff

This repo currently contains the Milestone 4 section/version foundation plus
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

The next runtime design step is Milestone 5: search and section permalinks.
