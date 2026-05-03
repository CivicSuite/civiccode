FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md CHANGELOG.md USER-MANUAL.md LICENSE-CODE LICENSE-DOCS ./
COPY civiccode ./civiccode

RUN python -m pip install --upgrade pip \
    && python -m pip install .

EXPOSE 8000

CMD ["sh", "-c", "python -m alembic -c civiccode/migrations/alembic.ini upgrade head && python -m uvicorn civiccode.main:app --host 0.0.0.0 --port 8000"]
