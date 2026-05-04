from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from civiccode.main import app
from civiccode.public_discovery import PopularQuestionRepository
from civiccode.source_registry import SourceRegistryRepository


STAFF_HEADERS = {
    "X-CivicCode-Role": "staff",
    "X-CivicCode-Actor": "clerk@example.gov",
}


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
        created = await client.post(
            "/api/v1/civiccode/sources",
            headers=STAFF_HEADERS,
            json=active_official_source(),
        )
        transitioned = await client.post(
            "/api/v1/civiccode/sources/municode_persistent/transitions",
            headers=STAFF_HEADERS,
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


@pytest.mark.asyncio
async def test_api_popular_questions_use_configured_database(monkeypatch, tmp_path) -> None:
    import civiccode.main as app_module

    db_url = f"sqlite:///{tmp_path / 'api-discovery.db'}"
    monkeypatch.setenv("CIVICCODE_SOURCE_REGISTRY_DB_URL", db_url)
    app_module.SOURCE_STORE.reset()
    app_module.SECTION_STORE.reset()
    app_module.POPULAR_QUESTION_STORE.reset()
    app_module._source_registry_repository = None
    app_module._popular_question_repository = None

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        assert (
            await client.post(
                "/api/v1/civiccode/sources",
                headers=STAFF_HEADERS,
                json=active_official_source("municode_discovery"),
            )
        ).status_code == 201
        assert (
            await client.post(
                "/api/v1/civiccode/titles",
                json={"title_id": "title_6", "title_number": "6", "title_name": "Animals"},
            )
        ).status_code == 201
        assert (
            await client.post(
                "/api/v1/civiccode/chapters",
                json={
                    "chapter_id": "chapter_6_12",
                    "title_id": "title_6",
                    "chapter_number": "6.12",
                    "chapter_name": "Urban Livestock",
                },
            )
        ).status_code == 201
        assert (
            await client.post(
                "/api/v1/civiccode/sections",
                json={
                    "section_id": "sec_chickens",
                    "chapter_id": "chapter_6_12",
                    "section_number": "6.12.040",
                    "section_heading": "Backyard chickens",
                },
            )
        ).status_code == 201
        assert (
            await client.post(
                "/api/v1/civiccode/sections/sec_chickens/versions",
                json={
                    "version_id": "v_chickens_current",
                    "section_id": "sec_chickens",
                    "source_id": "municode_discovery",
                    "version_label": "Current",
                    "body": "Residents may keep up to six backyard chickens with a city permit.",
                    "effective_start": "2026-01-01",
                    "status": "adopted",
                    "is_current": True,
                },
            )
        ).status_code == 201
        created = await client.post(
            "/api/v1/civiccode/staff/popular-questions",
            headers=STAFF_HEADERS,
            json={
                "question_id": "popular_chickens",
                "question_text": "Where do I read the backyard chicken permit rule?",
                "section_number": "6.12.040",
                "answer_excerpt": "Open Section 6.12.040 for adopted chicken-permit code text.",
            },
        )

    app_module._popular_question_repository = None
    persisted = PopularQuestionRepository(db_url=db_url).public_popular_questions()

    assert created.status_code == 201
    assert [question.question_id for question in persisted] == ["popular_chickens"]
    assert persisted[0].approved_by == "clerk@example.gov"
