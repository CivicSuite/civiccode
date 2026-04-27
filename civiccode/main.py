"""FastAPI runtime foundation for CivicCode."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from civiccode import __version__
from civiccode.citation_contract import build_citation_payload, refusal
from civiccode.qa_harness import QuestionRequestContext, build_grounded_answer
from civiccode.section_lifecycle import (
    SectionLifecycleError,
    SectionLifecycleStore,
    chapter_to_dict,
    section_to_dict,
    title_to_dict,
    version_to_dict,
)
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
SECTION_STORE = SectionLifecycleStore()


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


class TitleCreate(BaseModel):
    """Request body for creating a code title."""

    model_config = ConfigDict(extra="forbid")

    title_id: str | None = None
    title_number: str = Field(min_length=1)
    title_name: str = Field(min_length=1)
    sort_order: int = 0


class ChapterCreate(BaseModel):
    """Request body for creating a code chapter."""

    model_config = ConfigDict(extra="forbid")

    chapter_id: str | None = None
    title_id: str = Field(min_length=1)
    chapter_number: str = Field(min_length=1)
    chapter_name: str = Field(min_length=1)
    sort_order: int = 0


class SectionCreate(BaseModel):
    """Request body for creating a code section or subsection."""

    model_config = ConfigDict(extra="forbid")

    section_id: str | None = None
    chapter_id: str = Field(min_length=1)
    section_number: str = Field(min_length=1)
    section_heading: str = Field(min_length=1)
    parent_section_id: str | None = None
    sort_order: int = 0
    administrative_regulation_refs: list[str] = Field(default_factory=list)
    resolution_refs: list[str] = Field(default_factory=list)
    policy_refs: list[str] = Field(default_factory=list)
    approved_summary_refs: list[str] = Field(default_factory=list)


class SectionVersionCreate(BaseModel):
    """Request body for adding an immutable section version."""

    model_config = ConfigDict(extra="forbid")

    version_id: str | None = None
    section_id: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    version_label: str = Field(min_length=1)
    body: str = Field(min_length=1)
    effective_start: date
    effective_end: date | None = None
    status: str = "draft"
    is_current: bool = False
    adoption_event_id: str | None = None
    amendment_event_id: str | None = None
    amendment_summary: str | None = None
    prior_version_id: str | None = None


class QuestionAnswerRequest(BaseModel):
    """Request body for citation-grounded code Q&A."""

    model_config = ConfigDict(extra="forbid")

    question: str = Field(min_length=1)
    section_number: str | None = None
    as_of: date | None = None


def _raise_source_error(exc: SourceRegistryError) -> None:
    raise HTTPException(status_code=exc.status_code, detail=exc.detail()) from exc


def _raise_section_error(exc: SectionLifecycleError) -> None:
    raise HTTPException(status_code=exc.status_code, detail=exc.detail()) from exc


@app.get("/")
async def root() -> dict[str, str]:
    """Describe the current shipped runtime boundary."""
    return {
        "name": "CivicCode",
        "status": "citation-grounded Q&A foundation",
        "message": (
            "CivicCode runtime, canonical schema, official source registry API, and "
            "section/version lifecycle APIs are online. Search and stable section permalink "
            "APIs are online. Deterministic citations and refusal objects are online. "
            "Citation-grounded Q&A harness is online for adopted sections. Summaries, "
            "staff workbench, CivicClerk handoff, public lookup UI, live LLM calls, and "
            "legal determinations are not implemented yet."
        ),
        "code_answer_behavior": "citation_grounded",
        "api_base": "/api/v1/civiccode",
        "future_public_path": "/civiccode",
        "next_step": "Milestone 8: staff workbench foundation",
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


@app.post("/api/v1/civiccode/titles", status_code=201)
async def create_title(request: TitleCreate) -> dict[str, Any]:
    """Create a municipal code title container."""
    try:
        title = SECTION_STORE.create_title(request.model_dump())
    except SectionLifecycleError as exc:
        _raise_section_error(exc)
    return title_to_dict(title)


@app.post("/api/v1/civiccode/chapters", status_code=201)
async def create_chapter(request: ChapterCreate) -> dict[str, Any]:
    """Create a municipal code chapter under a title."""
    try:
        chapter = SECTION_STORE.create_chapter(request.model_dump())
    except SectionLifecycleError as exc:
        _raise_section_error(exc)
    return chapter_to_dict(chapter)


@app.post("/api/v1/civiccode/sections", status_code=201)
async def create_section(request: SectionCreate) -> dict[str, Any]:
    """Create a code section or subsection without generating answers."""
    try:
        section = SECTION_STORE.create_section(request.model_dump())
    except SectionLifecycleError as exc:
        _raise_section_error(exc)
    return section_to_dict(section)


@app.post("/api/v1/civiccode/sections/{section_id}/versions", status_code=201)
async def create_section_version(
    section_id: str,
    request: SectionVersionCreate,
) -> dict[str, Any]:
    """Create an immutable section version for adopted, pending, or retired text."""
    data = request.model_dump()
    if data["section_id"] != section_id:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Path section_id must match request body section_id.",
                "fix": "Use the same section_id in the URL and JSON body.",
            },
        )
    try:
        source = SOURCE_STORE.get(data["source_id"])
    except SourceRegistryError as exc:
        raise HTTPException(
            status_code=404,
            detail={
                "message": f"Source '{data['source_id']}' was not found for this section version.",
                "fix": "Register the source before adding section text from it.",
            },
        ) from exc
    if source.status in {"failed", "superseded"}:
        raise HTTPException(
            status_code=409,
            detail={
                "message": f"Source '{source.source_id}' is {source.status} and cannot back section text.",
                "fix": "Use an active source or refresh the source registry record first.",
            },
        )
    if data["status"] == "adopted" and (source.status != "active" or not source.public_visible):
        raise HTTPException(
            status_code=409,
            detail={
                "message": "Adopted section versions require an active public-visible source.",
                "fix": "Activate an official source in the registry before marking text as adopted law.",
            },
        )
    try:
        version = SECTION_STORE.create_version(data)
    except SectionLifecycleError as exc:
        _raise_section_error(exc)
    return version_to_dict(version)


@app.get("/api/v1/civiccode/sections/lookup")
async def lookup_section(section_number: str, as_of: date | None = None) -> dict[str, Any]:
    """Lookup adopted section text by current flag or effective date."""
    try:
        return SECTION_STORE.lookup_section(section_number, as_of=as_of)
    except SectionLifecycleError as exc:
        _raise_section_error(exc)


@app.get("/api/v1/civiccode/sections/{section_id}/history")
async def section_history(section_id: str) -> dict[str, Any]:
    """Return immutable amendment/version history for a section."""
    try:
        return SECTION_STORE.section_history(section_id)
    except SectionLifecycleError as exc:
        _raise_section_error(exc)


@app.get("/api/v1/civiccode/sections/{section_id}/permalink")
async def section_permalink(section_id: str) -> dict[str, Any]:
    """Return the stable public-facing permalink for a section."""
    try:
        return SECTION_STORE.permalink(section_id)
    except SectionLifecycleError as exc:
        _raise_section_error(exc)


@app.get("/api/v1/civiccode/search")
async def search_sections(q: str) -> dict[str, Any]:
    """Search public-visible code sections and related public materials."""
    try:
        return SECTION_STORE.search(q)
    except SectionLifecycleError as exc:
        _raise_section_error(exc)


@app.get("/api/v1/civiccode/citations/build")
async def build_citation(section_number: str, as_of: date | None = None) -> dict[str, Any]:
    """Build a deterministic citation object or a structured refusal."""
    return _build_citation_for_section(section_number, as_of)


@app.post("/api/v1/civiccode/questions/answer")
async def answer_question(request: QuestionAnswerRequest) -> dict[str, Any]:
    """Answer code questions only when an adopted section citation grounds them."""
    return build_grounded_answer(
        QuestionRequestContext(
            question=request.question,
            section_number=request.section_number,
            as_of=request.as_of,
        ),
        search=SECTION_STORE.search,
        build_citation=_build_citation_for_section,
    )


def _build_citation_for_section(section_number: str, as_of: date | None = None) -> dict[str, Any]:
    try:
        context = SECTION_STORE.citation_context(section_number, as_of=as_of)
    except SectionLifecycleError as exc:
        return refusal(exc.message, exc.fix, "section_lookup")
    source_id = context["version"]["source_id"]
    try:
        source = SOURCE_STORE.get(source_id)
    except SourceRegistryError:
        return refusal(
            f"Source '{source_id}' was not found for this citation.",
            "Register or restore the source before building a citation.",
            "missing_source",
        )
    if source.status != "active":
        return refusal(
            f"Source '{source.source_id}' is {source.status}, not active.",
            "Refresh or reactivate the source before using it for citations.",
            "stale_source",
        )
    return build_citation_payload(
        section=context["section"],
        version=context["version"],
        title=context["title"],
        chapter=context["chapter"],
        source=source_to_public_dict(source),
        as_of=context["as_of"],
    )
