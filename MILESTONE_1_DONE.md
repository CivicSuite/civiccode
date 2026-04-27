# CivicCode Milestone 1 Done

Status: Complete  
Date: 2026-04-27  
Branch: `milestone-1/runtime-foundation`

## Scope

Milestone 1 ships the CivicCode runtime foundation only.

Shipped:

- Installable `civiccode` Python package.
- `pyproject.toml` with exact `civiccore==0.2.0` dependency pin.
- FastAPI app shell in `civiccode.main`.
- `/` endpoint that states the runtime boundary and says code-answer behavior
  is not available.
- `/health` endpoint for IT smoke checks.
- CI updated to install the CivicCore v0.2.0 release wheel, install CivicCode,
  run pytest, verify docs, and run the CivicCore placeholder-import gate.
- README, README.txt, USER-MANUAL.md, docs landing page, CHANGELOG, and
  AGENTS.md updated from scaffold-only truth to runtime-foundation truth.

Not shipped:

- Database schema or Alembic migrations.
- Source registry.
- Search or section permalinks.
- Citation engine.
- LLM calls or code-answer behavior.
- Public lookup UI.

## Verification

- `python -m pytest --collect-only -q`: 10 tests collected.
- `python -m pytest -q`: 10 passed.
- `bash scripts/verify-docs.sh`: PASS.
- `python scripts/check-civiccore-placeholder-imports.py`: PASS.
- `python -m ruff check .`: PASS.
- Browser QA for `docs/index.html`: required runtime-foundation copy visible,
  zero console errors.
- API smoke: `/` returned `code_answer_behavior: not_available`; `/health`
  returned CivicCode `0.1.0.dev0` and CivicCore `0.2.0`.

## Next

Milestone 2: canonical schema and migrations.
