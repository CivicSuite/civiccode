"""FastAPI runtime foundation for CivicCode."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from starlette.responses import HTMLResponse

from civiccode import __version__
from civiccode.citation_contract import build_citation_payload, refusal
from civiccode.import_connectors import (
    CONNECTOR_TYPES,
    CivicCodeImportError,
    ImportConnectorStore,
    imported_tree_snapshot,
    job_to_dict,
    provenance_report,
)
from civiccode.ordinance_handoff import (
    OrdinanceHandoffError,
    OrdinanceHandoffStore,
    event_to_dict,
    handoff_audit_event_to_dict,
)
from civiccode.plain_language import (
    PlainLanguageSummaryError,
    PlainLanguageSummaryStore,
    summary_audit_event_to_dict,
    summary_to_public_dict,
    summary_to_staff_dict,
)
from civiccode.public_lookup import (
    is_legal_advice_query,
    render_error_page,
    render_home_page,
    render_refusal_page,
    render_search_page,
    render_section_page,
)
from civiccode.public_exports import (
    build_records_ready_export,
    render_records_ready_export_page,
)
from civiccode.qa_harness import QuestionRequestContext, build_grounded_answer
from civiccode.section_lifecycle import (
    SectionLifecycleError,
    SectionLifecycleStore,
    chapter_to_dict,
    section_to_dict,
    title_to_dict,
    version_to_dict,
)
from civiccode.staff_workbench import (
    StaffWorkbenchError,
    StaffWorkbenchStore,
    audit_event_to_dict,
    note_to_staff_dict,
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
STAFF_NOTE_STORE = StaffWorkbenchStore()
SUMMARY_STORE = PlainLanguageSummaryStore()
HANDOFF_STORE = OrdinanceHandoffStore()
IMPORT_STORE = ImportConnectorStore(
    source_store=SOURCE_STORE,
    section_store=SECTION_STORE,
)


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


class InterpretationNoteCreate(BaseModel):
    """Request body for staff-only interpretation notes."""

    model_config = ConfigDict(extra="forbid")

    note_id: str | None = None
    note_text: str = Field(min_length=1)
    status: str = "draft"


class PlainLanguageSummaryCreate(BaseModel):
    """Request body for staff-drafted plain-language summaries."""

    model_config = ConfigDict(extra="forbid")

    summary_id: str | None = None
    section_version_id: str = Field(min_length=1)
    summary_text: str = Field(min_length=1)
    language_code: str = "en"
    status: str = "draft"


class CivicClerkOrdinanceEventCreate(BaseModel):
    """Request body for CivicClerk ordinance/adoption handoff intake."""

    model_config = ConfigDict(extra="forbid")

    event_id: str | None = None
    external_event_id: str = Field(min_length=1)
    civicclerk_meeting_id: str = Field(min_length=1)
    civicclerk_agenda_item_id: str = Field(min_length=1)
    ordinance_number: str = Field(min_length=1)
    title: str = Field(min_length=1)
    status: str = "pending"
    affected_sections: list[str] = Field(default_factory=list)
    source_document_url: str = Field(min_length=1)
    source_document_hash: str = Field(min_length=1)
    ordinance_text: str = ""
    adopted_at: datetime | None = None
    failure_reason: str | None = None


class ImportBundleCreate(BaseModel):
    """Request body for local fixture/file-drop import jobs."""

    model_config = ConfigDict(extra="forbid")

    job_id: str | None = None
    connector_type: str = Field(min_length=1)
    source: SourceCreate
    titles: list[TitleCreate] = Field(default_factory=list)
    chapters: list[ChapterCreate] = Field(default_factory=list)
    sections: list[SectionCreate] = Field(default_factory=list)
    versions: list[SectionVersionCreate] = Field(default_factory=list)
    provenance: dict[str, str] = Field(default_factory=dict)


def _raise_source_error(exc: SourceRegistryError) -> None:
    raise HTTPException(status_code=exc.status_code, detail=exc.detail()) from exc


def _raise_section_error(exc: SectionLifecycleError) -> None:
    raise HTTPException(status_code=exc.status_code, detail=exc.detail()) from exc


def _raise_staff_error(exc: StaffWorkbenchError) -> None:
    raise HTTPException(status_code=exc.status_code, detail=exc.detail()) from exc


def _raise_summary_error(exc: PlainLanguageSummaryError) -> None:
    raise HTTPException(status_code=exc.status_code, detail=exc.detail()) from exc


def _raise_handoff_error(exc: OrdinanceHandoffError) -> None:
    raise HTTPException(status_code=exc.status_code, detail=exc.detail()) from exc


def _raise_import_error(exc: CivicCodeImportError) -> None:
    raise HTTPException(status_code=exc.status_code, detail=exc.detail()) from exc


def _require_staff(
    x_civiccode_role: str | None,
    x_civiccode_actor: str | None,
) -> str:
    if x_civiccode_role != "staff":
        raise HTTPException(
            status_code=403,
            detail={
                "message": "Staff role required for this CivicCode endpoint.",
                "fix": "Send X-CivicCode-Role: staff from the trusted staff shell or service account.",
            },
        )
    actor = (x_civiccode_actor or "").strip()
    if not actor:
        raise HTTPException(
            status_code=403,
            detail={
                "message": "Staff actor required for this CivicCode endpoint.",
                "fix": "Send X-CivicCode-Actor with the staff email or service account.",
            },
        )
    return actor


@app.get("/")
async def root() -> dict[str, str]:
    """Describe the current shipped runtime boundary."""
    return {
        "name": "CivicCode",
        "status": "accessibility export foundation",
        "message": (
            "CivicCode runtime, canonical schema, official source registry API, and "
            "section/version lifecycle APIs are online. Search and stable section permalink "
            "APIs are online. Deterministic citations and refusal objects are online. "
            "Citation-grounded Q&A harness is online for adopted sections. Staff "
            "interpretation-note APIs and staff Q&A context are online. Staff-approved "
            "plain-language summaries are online and labeled non-authoritative. "
            "CivicClerk ordinance handoff intake and affected-section warnings are "
            "online. Resident-facing public lookup pages are online at /civiccode. "
            "Local file-drop and fixture import jobs are online with provenance, "
            "retry, and no required outbound dependency. Records-ready section "
            "exports are online with citation, version, and source metadata. "
            "Live LLM calls, live codifier sync, and legal determinations are "
            "not implemented yet."
        ),
        "code_answer_behavior": "citation_grounded",
        "api_base": "/api/v1/civiccode",
        "future_public_path": "/civiccode",
        "next_step": "CivicCode v0.1.1 dependency-alignment release; next work follows the CivicSuite roadmap.",
    }


@app.get("/civiccode", response_class=HTMLResponse)
async def public_lookup_home() -> str:
    """Render the resident-facing public code lookup home page."""
    return render_home_page()


@app.get("/civiccode/search", response_class=HTMLResponse)
async def public_lookup_search(q: str = "") -> str:
    """Render public search results, empty states, or refusal states."""
    query = q.strip()
    if not query:
        return render_error_page(
            "Search query required",
            "Search query cannot be empty.",
            "Enter a section number like 6.12.040 or a resident phrase like backyard chickens.",
            status_label="Empty search",
        )
    if is_legal_advice_query(query):
        return render_refusal_page(query)
    try:
        results = SECTION_STORE.search(query)["results"]
    except SectionLifecycleError:
        results = []
    return render_search_page(query, results)


@app.get("/civiccode/sections/{section_ref}", response_class=HTMLResponse)
async def public_section_detail(section_ref: str, as_of: date | None = None) -> str:
    """Render a public section detail page with citation and warning context."""
    try:
        try:
            lookup = SECTION_STORE.lookup_section(section_ref, as_of=as_of)
        except SectionLifecycleError:
            section = SECTION_STORE.get_section(section_ref)
            lookup = SECTION_STORE.lookup_section(section.section_number, as_of=as_of)
    except SectionLifecycleError as exc:
        return render_error_page(
            "Section not found",
            exc.message,
            exc.fix,
            status_label="Section lookup problem",
        )
    section_number = lookup["section"]["section_number"]
    citation_payload = _build_citation_for_section(section_number, as_of=as_of)
    summaries = []
    for summary in SUMMARY_STORE.list_for_section(lookup["section"]["section_id"]):
        version = SECTION_STORE.get_version(summary.section_version_id)
        summaries.append(
            summary_to_public_dict(
                summary,
                authoritative_section=lookup["section"],
                authoritative_text=version.body,
            )
        )
    warnings = HANDOFF_STORE.warnings_for_section(section_number)
    return render_section_page(lookup, citation_payload, summaries, warnings)


@app.get("/civiccode/sections/{section_ref}/export", response_class=HTMLResponse)
async def public_section_export(section_ref: str, as_of: date | None = None) -> str:
    """Render an accessible records-ready export page for a section."""
    try:
        export = _build_export_for_section(section_ref, as_of)
    except HTTPException as exc:
        detail = exc.detail if isinstance(exc.detail, dict) else {"message": str(exc.detail), "fix": "Try again."}
        return render_error_page(
            "Export unavailable",
            detail["message"],
            detail["fix"],
            status_label="Export problem",
        )
    return render_records_ready_export_page(export)


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
        "import_connector_types": sorted(CONNECTOR_TYPES),
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
        payload = SECTION_STORE.lookup_section(section_number, as_of=as_of)
    except SectionLifecycleError as exc:
        _raise_section_error(exc)
    payload["handoff_warnings"] = HANDOFF_STORE.warnings_for_section(section_number)
    return payload


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


@app.get("/api/v1/civiccode/sections/{section_ref}/export")
async def export_section(section_ref: str, as_of: date | None = None) -> dict[str, Any]:
    """Return a records-ready section export with citation and source provenance."""
    return _build_export_for_section(section_ref, as_of)


@app.post("/api/v1/civiccode/questions/answer")
async def answer_question(request: QuestionAnswerRequest) -> dict[str, Any]:
    """Answer code questions only when an adopted section citation grounds them."""
    payload = build_grounded_answer(
        QuestionRequestContext(
            question=request.question,
            section_number=request.section_number,
            as_of=request.as_of,
        ),
        search=SECTION_STORE.search,
        build_citation=_build_citation_for_section,
    )
    payload["audience"] = "public"
    return payload


@app.post("/api/v1/civiccode/staff/sections/{section_id}/notes", status_code=201)
async def create_interpretation_note(
    section_id: str,
    request: InterpretationNoteCreate,
    x_civiccode_role: str | None = Header(default=None),
    x_civiccode_actor: str | None = Header(default=None),
) -> dict[str, Any]:
    """Create a staff-only interpretation note without exposing it publicly."""
    actor = _require_staff(x_civiccode_role, x_civiccode_actor)
    try:
        SECTION_STORE.get_section(section_id)
        note = STAFF_NOTE_STORE.create_note(
            section_id,
            request.model_dump(),
            actor=actor,
        )
    except SectionLifecycleError as exc:
        _raise_section_error(exc)
    except StaffWorkbenchError as exc:
        _raise_staff_error(exc)
    return note_to_staff_dict(note)


@app.get("/api/v1/civiccode/staff/sections/{section_id}/notes")
async def list_interpretation_notes(
    section_id: str,
    x_civiccode_role: str | None = Header(default=None),
    x_civiccode_actor: str | None = Header(default=None),
) -> dict[str, Any]:
    """List staff-only interpretation notes for authorized staff clients."""
    _require_staff(x_civiccode_role, x_civiccode_actor)
    try:
        SECTION_STORE.get_section(section_id)
    except SectionLifecycleError as exc:
        _raise_section_error(exc)
    return {"notes": [note_to_staff_dict(note) for note in STAFF_NOTE_STORE.list_notes(section_id)]}


@app.get("/api/v1/civiccode/staff/audit-events")
async def list_staff_audit_events(
    x_civiccode_role: str | None = Header(default=None),
    x_civiccode_actor: str | None = Header(default=None),
) -> dict[str, Any]:
    """List staff workbench audit events for authorized staff clients."""
    _require_staff(x_civiccode_role, x_civiccode_actor)
    events = [
        *[audit_event_to_dict(event) for event in STAFF_NOTE_STORE.audit_events()],
        *[summary_audit_event_to_dict(event) for event in SUMMARY_STORE.audit_events()],
        *[handoff_audit_event_to_dict(event) for event in HANDOFF_STORE.audit_events()],
    ]
    events.sort(key=lambda event: event["created_at"])
    return {"events": events}


@app.post("/api/v1/civiccode/staff/imports/local-bundle", status_code=201)
async def create_local_import_job(
    request: ImportBundleCreate,
    x_civiccode_role: str | None = Header(default=None),
    x_civiccode_actor: str | None = Header(default=None),
) -> dict[str, Any]:
    """Import a local codifier/file-drop fixture without outbound network calls."""
    actor = _require_staff(x_civiccode_role, x_civiccode_actor)
    job = IMPORT_STORE.run_import(request.model_dump(), actor=actor)
    return job_to_dict(job)


@app.get("/api/v1/civiccode/staff/imports")
async def list_import_jobs(
    x_civiccode_role: str | None = Header(default=None),
    x_civiccode_actor: str | None = Header(default=None),
) -> dict[str, Any]:
    """List local import jobs and their visible success/failure states."""
    _require_staff(x_civiccode_role, x_civiccode_actor)
    return {"imports": [job_to_dict(job) for job in IMPORT_STORE.list_jobs()]}


@app.get("/api/v1/civiccode/staff/imports/{job_id}")
async def get_import_job(
    job_id: str,
    x_civiccode_role: str | None = Header(default=None),
    x_civiccode_actor: str | None = Header(default=None),
) -> dict[str, Any]:
    """Read a local import job, including actionable failure details."""
    _require_staff(x_civiccode_role, x_civiccode_actor)
    try:
        job = IMPORT_STORE.get(job_id)
    except CivicCodeImportError as exc:
        _raise_import_error(exc)
    return job_to_dict(job)


@app.post("/api/v1/civiccode/staff/imports/{job_id}/retry", status_code=201)
async def retry_import_job(
    job_id: str,
    request: ImportBundleCreate,
    x_civiccode_role: str | None = Header(default=None),
    x_civiccode_actor: str | None = Header(default=None),
) -> dict[str, Any]:
    """Retry a failed import job with a corrected local bundle."""
    actor = _require_staff(x_civiccode_role, x_civiccode_actor)
    try:
        job = IMPORT_STORE.retry_import(job_id, request.model_dump(), actor=actor)
    except CivicCodeImportError as exc:
        _raise_import_error(exc)
    return job_to_dict(job)


@app.get("/api/v1/civiccode/staff/imports/{job_id}/provenance")
async def get_import_provenance(
    job_id: str,
    x_civiccode_role: str | None = Header(default=None),
    x_civiccode_actor: str | None = Header(default=None),
) -> dict[str, Any]:
    """Return a provenance report for a local import job."""
    _require_staff(x_civiccode_role, x_civiccode_actor)
    try:
        job = IMPORT_STORE.get(job_id)
    except CivicCodeImportError as exc:
        _raise_import_error(exc)
    return provenance_report(job, SOURCE_STORE)


@app.get("/api/v1/civiccode/staff/imports/{job_id}/tree")
async def get_imported_tree(
    job_id: str,
    x_civiccode_role: str | None = Header(default=None),
    x_civiccode_actor: str | None = Header(default=None),
) -> dict[str, Any]:
    """Show imported title/chapter/section/version tree for staff verification."""
    _require_staff(x_civiccode_role, x_civiccode_actor)
    try:
        job = IMPORT_STORE.get(job_id)
        if job.status != "completed" or not job.source_id:
            raise CivicCodeImportError(
                f"Import job '{job_id}' does not have a completed source tree.",
                "Open the job details, fix the failure, and retry before reading its imported tree.",
                status_code=409,
            )
        return imported_tree_snapshot(job.source_id, SOURCE_STORE, SECTION_STORE)
    except CivicCodeImportError as exc:
        _raise_import_error(exc)
    except SourceRegistryError as exc:
        _raise_source_error(exc)


@app.post("/api/v1/civiccode/staff/civicclerk/ordinance-events", status_code=201)
async def create_civicclerk_ordinance_event(
    request: CivicClerkOrdinanceEventCreate,
    x_civiccode_role: str | None = Header(default=None),
    x_civiccode_actor: str | None = Header(default=None),
) -> dict[str, Any]:
    """Receive CivicClerk ordinance/adoption events without codifying them."""
    actor = _require_staff(x_civiccode_role, x_civiccode_actor)
    try:
        for section_number in request.affected_sections:
            SECTION_STORE.lookup_section(section_number)
        event = HANDOFF_STORE.create_event(request.model_dump(), actor=actor)
    except SectionLifecycleError as exc:
        _raise_section_error(exc)
    except OrdinanceHandoffError as exc:
        _raise_handoff_error(exc)
    return event_to_dict(event)


@app.post("/api/v1/civiccode/staff/sections/{section_id}/summaries", status_code=201)
async def create_plain_language_summary(
    section_id: str,
    request: PlainLanguageSummaryCreate,
    x_civiccode_role: str | None = Header(default=None),
    x_civiccode_actor: str | None = Header(default=None),
) -> dict[str, Any]:
    """Create a staff-drafted plain-language summary tied to adopted code text."""
    actor = _require_staff(x_civiccode_role, x_civiccode_actor)
    try:
        SECTION_STORE.get_section(section_id)
        version = SECTION_STORE.get_version(request.section_version_id)
        if version.section_id != section_id:
            raise PlainLanguageSummaryError(
                "Plain-language summary section does not match the cited section version.",
                "Use a section_version_id that belongs to the section in the request URL.",
                status_code=409,
            )
        if version.status != "adopted":
            raise PlainLanguageSummaryError(
                "Plain-language summaries require an adopted section version.",
                "Attach summaries only to adopted law, not draft or pending text.",
            )
        summary = SUMMARY_STORE.create_summary(
            section_id,
            request.model_dump(),
            actor=actor,
        )
    except SectionLifecycleError as exc:
        _raise_section_error(exc)
    except PlainLanguageSummaryError as exc:
        _raise_summary_error(exc)
    return summary_to_staff_dict(summary)


@app.post("/api/v1/civiccode/staff/summaries/{summary_id}/approve")
async def approve_plain_language_summary(
    summary_id: str,
    x_civiccode_role: str | None = Header(default=None),
    x_civiccode_actor: str | None = Header(default=None),
) -> dict[str, Any]:
    """Approve a plain-language summary for public display after staff review."""
    actor = _require_staff(x_civiccode_role, x_civiccode_actor)
    try:
        summary = SUMMARY_STORE.get_summary(summary_id)
        version = SECTION_STORE.get_version(summary.section_version_id)
        if version.status != "adopted":
            raise PlainLanguageSummaryError(
                "Only summaries tied to adopted section text can be approved.",
                "Attach the summary to an adopted section version before approving it.",
                status_code=409,
            )
        summary = SUMMARY_STORE.approve_summary(summary_id, actor=actor)
    except SectionLifecycleError as exc:
        _raise_section_error(exc)
    except PlainLanguageSummaryError as exc:
        _raise_summary_error(exc)
    return summary_to_staff_dict(summary)


@app.get("/api/v1/civiccode/sections/{section_id}/summaries")
async def list_public_plain_language_summaries(section_id: str) -> dict[str, Any]:
    """List public approved summaries while keeping authoritative code visible."""
    try:
        section = SECTION_STORE.get_section(section_id)
        summaries = []
        for summary in SUMMARY_STORE.list_for_section(section_id):
            version = SECTION_STORE.get_version(summary.section_version_id)
            summaries.append(
                summary_to_public_dict(
                    summary,
                    authoritative_section={
                        "section_id": section.section_id,
                        "section_number": section.section_number,
                        "section_heading": section.section_heading,
                    },
                    authoritative_text=version.body,
                )
            )
    except SectionLifecycleError as exc:
        _raise_section_error(exc)
    return {
        "section_id": section_id,
        "summaries": summaries,
        "count": len(summaries),
        "code_answer_behavior": "not_available",
    }


@app.post("/api/v1/civiccode/staff/questions/answer")
async def answer_staff_question(
    request: QuestionAnswerRequest,
    x_civiccode_role: str | None = Header(default=None),
    x_civiccode_actor: str | None = Header(default=None),
) -> dict[str, Any]:
    """Answer staff questions with staff-only notes kept out of public responses."""
    _require_staff(x_civiccode_role, x_civiccode_actor)
    payload = build_grounded_answer(
        QuestionRequestContext(
            question=request.question,
            section_number=request.section_number,
            as_of=request.as_of,
        ),
        search=SECTION_STORE.search,
        build_citation=_build_citation_for_section,
    )
    payload["audience"] = "staff"
    if payload.get("status") == "ok":
        section_id = payload["citations"][0]["section_id"]
        payload["staff_context"] = {
            "warning": "staff_only_do_not_publish",
            "notes": [
                note_to_staff_dict(note)
                for note in STAFF_NOTE_STORE.list_notes(section_id)
                if note.status == "approved"
            ],
        }
    return payload


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


def _build_export_for_section(section_ref: str, as_of: date | None = None) -> dict[str, Any]:
    try:
        try:
            lookup = SECTION_STORE.lookup_section(section_ref, as_of=as_of)
        except SectionLifecycleError:
            section = SECTION_STORE.get_section(section_ref)
            lookup = SECTION_STORE.lookup_section(section.section_number, as_of=as_of)
    except SectionLifecycleError as exc:
        _raise_section_error(exc)

    section_number = lookup["section"]["section_number"]
    citation_payload = _build_citation_for_section(section_number, as_of)
    if citation_payload.get("status") != "ok":
        raise HTTPException(
            status_code=409,
            detail={
                "message": citation_payload.get("reason", "Citation could not be built for this export."),
                "fix": citation_payload.get("fix", "Refresh the source and try exporting again."),
            },
        )
    try:
        source = SOURCE_STORE.get(citation_payload["citation"]["source_id"])
    except SourceRegistryError as exc:
        _raise_source_error(exc)
    return build_records_ready_export(
        lookup=lookup,
        citation_payload=citation_payload,
        source=source_to_public_dict(source),
    )
