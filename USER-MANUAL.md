# CivicCode User Manual

CivicCode currently ships a source registry foundation built on the runtime foundation
and canonical schema foundation. This manual explains what a first-time
installer can do today and what is still planned.

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
- no frontend exists yet,
- no LLM answers or code-answer behavior are generated yet.

For a non-technical user, there is not yet a public product workflow. The
honest experience today is an IT smoke test that proves the module can start
and that source records can be registered before import, section/version,
search, citation, and public lookup work begins.

## For IT and technical staff

This repo currently contains the Milestone 3 source registry foundation plus
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

The next runtime design step is Milestone 4: code section and version lifecycle.
