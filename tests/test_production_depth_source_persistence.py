from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from civiccode.main import app
from civiccode.source_registry import SourceRegistryRepository


def active_official_source(source_id: str = "municode_persistent") -> dict[str, object]:
    return {
        "source_id": source_id,
        "name": "Example Municipal Code",
        "publisher": "Municode",
        "source_type": "municode",
        "source_category": "municipal_code",
        "source_url": "https://library.municode.com/example/codes/code_of_ordinances",
        "retrieved_at": "2026-04-27T12:00:00Z",
        "retrieval_method": "official_web_export",
        "source_owner": "City Clerk",
        "is_official": True,
        "status": "active",
        "staff_notes": "Internal source review note.",
    }


def test_source_registry_records_persist_status_and_staff_notes(tmp_path) -> None:
    db_url = f"sqlite:///{tmp_path / 'sources.db'}"
    first = SourceRegistryRepository(db_url=db_url)
    created = first.create(active_official_source())
    transitioned = first.transition(
        created.source_id,
        "stale",
        actor="clerk@example.gov",
        reason="Publisher posted a newer official export.",
    )

    second = SourceRegistryRepository(db_url=db_url)
    persisted = second.get(created.source_id)

    assert transitioned.status == "stale"
    assert persisted.status == "stale"
    assert persisted.staff_notes == "Internal source review note."
    assert persisted.source_owner == "City Clerk"


@pytest.mark.asyncio
async def test_api_sources_use_configured_database(monkeypatch, tmp_path) -> None:
    db_url = f"sqlite:///{tmp_path / 'api-sources.db'}"
    monkeypatch.setenv("CIVICCODE_SOURCE_REGISTRY_DB_URL", db_url)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        created = await client.post("/api/v1/civiccode/sources", json=active_official_source())
        transitioned = await client.post(
            "/api/v1/civiccode/sources/municode_persistent/transitions",
            json={
                "to_status": "stale",
                "actor": "clerk@example.gov",
                "reason": "Publisher posted a newer official export.",
            },
        )
        public = await client.get("/api/v1/civiccode/sources/municode_persistent")

    second = SourceRegistryRepository(db_url=db_url)
    persisted = second.get("municode_persistent")

    assert created.status_code == 201
    assert transitioned.status_code == 200
    assert transitioned.json()["status"] == "stale"
    assert public.status_code == 200
    assert "staff_notes" not in public.json()
    assert persisted.status == "stale"
    assert persisted.staff_notes == "Internal source review note."
