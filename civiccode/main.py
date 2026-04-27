"""FastAPI runtime foundation for CivicCode."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from civiccode import __version__
from civiccode.source_registry import (
    SOURCE_CATEGORIES,
    SOURCE_STATES,
    SOURCE_TRANSITIONS,
    SOURCE_TYPES,
    SourceRegistryError,
    SourceRegistryStore,
    compute_reference_checksum,
    source_to_public_dict,
    source_to_staff_dict,
)
from civiccore import __version__ as CIVICCORE_VERSION

app = FastAPI(
    title="CivicCode",
    version=__version__,
    summary="Runtime foundation for CivicCode municipal code access workflows.",
)

SOURCE_STORE = SourceRegistryStore()


class SourceCreate(BaseModel):
    """Request body for registering an official or explicitly labeled source."""

    model_config = ConfigDict(extra="forbid")

    source_id: str | None = None
    name: str = Field(min_length=1)
    publisher: str = Field(min_length=1)
    source_type: str = Field(min_length=1)
    source_category: str = Field(min_length=1)
    source_url: str | None = None
    file_reference: str | None = None
    retrieved_at: datetime | None = None
    retrieval_method: str | None = None
    checksum: str | None = None
    source_owner: str | None = None
    is_official: bool = True
    official_status_note: str | None = None
    status: str = "draft"
    staff_notes: str | None = None


class SourceTransitionRequest(BaseModel):
    """Request body for source-state changes."""

    model_config = ConfigDict(extra="forbid")

    to_status: str
    actor: str = Field(min_length=1)
    reason: str = Field(min_length=1)


def _raise_source_error(exc: SourceRegistryError) -> None:
    raise HTTPException(status_code=exc.status_code, detail=exc.detail()) from exc


@app.get("/")
async def root() -> dict[str, str]:
    """Describe the current shipped runtime boundary."""
    return {
        "name": "CivicCode",
        "status": "source registry foundation",
        "message": (
            "CivicCode runtime, canonical schema, and official source registry API are online. "
            "Section/version workflows, search, citations, Q&A, summaries, staff workbench, "
            "CivicClerk handoff, and public lookup workflows are not implemented yet."
        ),
        "code_answer_behavior": "not_available",
        "api_base": "/api/v1/civiccode",
        "future_public_path": "/civiccode",
        "next_step": "Milestone 4: code section and version lifecycle",
    }


@app.get("/health")
async def health() -> dict[str, str]:
    """Provide a simple operational health check for IT staff."""
    return {
        "status": "ok",
        "service": "civiccode",
        "version": __version__,
        "civiccore": CIVICCORE_VERSION,
    }


@app.get("/api/v1/civiccode/sources/catalog")
async def source_registry_catalog() -> dict[str, Any]:
    """Expose allowed source registry vocabulary for staff integration clients."""
    return {
        "source_types": sorted(SOURCE_TYPES),
        "source_categories": SOURCE_CATEGORIES,
        "source_states": sorted(SOURCE_STATES),
        "source_transitions": {
            status: sorted(targets) for status, targets in SOURCE_TRANSITIONS.items()
        },
    }


@app.post("/api/v1/civiccode/sources", status_code=201)
async def create_source(request: SourceCreate) -> dict[str, Any]:
    """Register a municipal code source without importing its contents yet."""
    data = request.model_dump()
    if data["checksum"] is None and data.get("file_reference"):
        data["checksum"] = compute_reference_checksum(data["file_reference"])
    try:
        source = SOURCE_STORE.create(data)
    except SourceRegistryError as exc:
        _raise_source_error(exc)
    return source_to_staff_dict(source)


@app.get("/api/v1/civiccode/sources")
async def list_public_sources() -> dict[str, Any]:
    """List public-visible sources without exposing staff-only notes."""
    return {
        "sources": [
            source_to_public_dict(source)
            for source in SOURCE_STORE.list_sources(include_staff_only=False)
        ]
    }


@app.get("/api/v1/civiccode/sources/{source_id}")
async def get_public_source(source_id: str) -> dict[str, Any]:
    """Read a public source record without leaking staff-only notes."""
    try:
        source = SOURCE_STORE.get(source_id)
    except SourceRegistryError as exc:
        _raise_source_error(exc)
    if not source.public_visible:
        raise HTTPException(
            status_code=404,
            detail={
                "message": f"Source '{source_id}' is not public-visible.",
                "fix": "Use the staff source endpoint if you are authorized to view it.",
            },
        )
    return source_to_public_dict(source)


@app.get("/api/v1/civiccode/staff/sources")
async def list_staff_sources() -> dict[str, Any]:
    """List all registered sources for staff workflows."""
    return {
        "sources": [
            source_to_staff_dict(source)
            for source in SOURCE_STORE.list_sources(include_staff_only=True)
        ]
    }


@app.get("/api/v1/civiccode/staff/sources/{source_id}")
async def get_staff_source(source_id: str) -> dict[str, Any]:
    """Read a staff source record including staff-only notes."""
    try:
        source = SOURCE_STORE.get(source_id)
    except SourceRegistryError as exc:
        _raise_source_error(exc)
    return source_to_staff_dict(source)


@app.post("/api/v1/civiccode/sources/{source_id}/transitions")
async def transition_source(
    source_id: str,
    request: SourceTransitionRequest,
) -> dict[str, Any]:
    """Transition a source through the official registry lifecycle."""
    try:
        source = SOURCE_STORE.transition(
            source_id,
            request.to_status,
            actor=request.actor,
            reason=request.reason,
        )
    except SourceRegistryError as exc:
        _raise_source_error(exc)
    return source_to_staff_dict(source)
