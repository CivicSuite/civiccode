from __future__ import annotations

import importlib
import socket

import pytest
from httpx import ASGITransport, AsyncClient

from civiccode.mock_city_environment import mock_city_codifier_contracts, mock_city_import_payload


STAFF_HEADERS = {
    "X-CivicCode-Role": "staff",
    "X-CivicCode-Actor": "operator@example.gov",
}


@pytest.fixture()
def app_module(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("CIVICCODE_SOURCE_REGISTRY_DB_URL", raising=False)
    monkeypatch.delenv("CIVICCODE_DEMO_SEED", raising=False)
    module = importlib.import_module("civiccode.main")
    module.SOURCE_STORE.reset()
    module.SECTION_STORE.reset()
    module.STAFF_NOTE_STORE.reset()
    module.SUMMARY_STORE.reset()
    module.HANDOFF_STORE.reset()
    module.IMPORT_STORE.reset()
    module.CODIFIER_SYNC_STORE.reset()
    module._source_registry_repository = None
    module._section_lifecycle_repository = None
    module._import_store = None
    module._codifier_sync_store = None
    module._demo_seed_key = None
    return module


@pytest.fixture()
async def client(app_module):
    async with AsyncClient(
        transport=ASGITransport(app=app_module.app),
        base_url="http://testserver",
    ) as async_client:
        yield async_client


@pytest.mark.asyncio
async def test_staff_operational_state_empty_state_is_actionable(client: AsyncClient) -> None:
    response = await client.get("/api/v1/civiccode/staff/operational-state", headers=STAFF_HEADERS)

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "missing_state"
    assert payload["counts"] == {
        "records": 0,
        "retry_queue": 0,
        "replay_record": 0,
        "delta_cursor": 0,
        "lanes_with_state": 0,
    }
    assert payload["data_source"]["external_deployment_required"] is False
    assert payload["data_source"]["network_required"] is False
    assert payload["fixes"] == [
        "Run at least one local import, codifier sync, or CivicClerk handoff operation so staff can inspect operational readiness."
    ]
    assert payload["lanes"]["import"]["fixes"][0].startswith("Run a local import bundle")
    assert payload["lanes"]["sync"]["fixes"][0].startswith("Configure a codifier sync source")
    assert payload["lanes"]["handoff"]["fixes"][0].startswith("Create a CivicClerk handoff event")


@pytest.mark.asyncio
async def test_staff_operational_state_returns_populated_mock_city_state(
    client: AsyncClient,
    app_module,
) -> None:
    payload = mock_city_import_payload(mock_city_codifier_contracts()[0])
    app_module.SOURCE_STORE.create(payload["source"])

    configured = await client.post(
        "/api/v1/civiccode/staff/sync/codifier-sources",
        headers=STAFF_HEADERS,
        json={"source_id": payload["source"]["source_id"], "sync_schedule": "*/15 * * * *"},
    )
    assert configured.status_code == 201

    run = await client.post(
        f"/api/v1/civiccode/staff/sync/codifier-sources/{payload['source']['source_id']}/run",
        headers=STAFF_HEADERS,
        json={"payload": payload, "changed_since": "2026-05-01T12:00:00Z"},
    )
    assert run.status_code == 201

    handoff = await client.post(
        "/api/v1/civiccode/staff/civicclerk/ordinance-events",
        headers=STAFF_HEADERS,
        json={
            "event_id": "ord_operational_ready",
            "external_event_id": "cc_event_operational_ready",
            "civicclerk_meeting_id": "meeting_2026_05_06",
            "civicclerk_agenda_item_id": "agenda_8",
            "ordinance_number": "2026-108",
            "title": "Operational readiness handoff proof",
            "status": "adopted",
            "affected_sections": ["6.12.040"],
            "source_document_url": "https://brookfield.example.gov/ordinances/2026-108.pdf",
            "source_document_hash": "sha256:operational-ready",
            "ordinance_text": "An ordinance proving operational readiness state.",
        },
    )
    assert handoff.status_code == 201

    response = await client.get("/api/v1/civiccode/staff/operational-state", headers=STAFF_HEADERS)

    assert response.status_code == 200
    readiness = response.json()
    assert readiness["status"] == "ready"
    assert readiness["counts"]["lanes_with_state"] == 3
    assert readiness["counts"]["replay_record"] >= 3
    assert readiness["counts"]["delta_cursor"] == 1
    assert readiness["fixes"] == []
    assert readiness["lanes"]["handoff"]["status"] == "ready"
    assert readiness["lanes"]["import"]["status"] == "ready"
    assert readiness["lanes"]["sync"]["status"] == "ready"
    assert any(record["lane"] == "sync" for record in readiness["records"])
    assert any(record["subject_id"] == payload["source"]["source_id"] for record in readiness["records"])


@pytest.mark.asyncio
async def test_staff_operational_state_does_not_require_external_deployment(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_network(*args, **kwargs):  # noqa: ANN002, ANN003
        raise AssertionError("operational-state endpoint attempted outbound network")

    monkeypatch.setattr(socket, "create_connection", fail_network)

    response = await client.get("/api/v1/civiccode/staff/operational-state", headers=STAFF_HEADERS)

    assert response.status_code == 200
    payload = response.json()
    assert payload["data_source"]["external_deployment_required"] is False
    assert payload["data_source"]["network_required"] is False


@pytest.mark.asyncio
async def test_staff_operational_state_requires_staff_headers(client: AsyncClient) -> None:
    response = await client.get("/api/v1/civiccode/staff/operational-state")

    assert response.status_code == 403
    assert response.json()["detail"]["fix"].startswith("Send X-CivicCode-Role: staff")
