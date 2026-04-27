# CivicCode User Manual

CivicCode currently ships a runtime foundation. This manual explains what a
first-time installer can do today and what is still planned.

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
- no database schema exists yet,
- no frontend exists yet,
- no LLM answers or code-answer behavior are generated yet.

For a non-technical user, there is not yet a public product workflow. The
honest experience today is an IT smoke test that proves the module can start
before schema, import, search, citation, and public lookup work begins.

## For IT and technical staff

This repo currently contains the Milestone 1 runtime foundation plus
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

The next runtime design step is Milestone 2: canonical schema and migrations.
