"""Local source-import and connector hardening for CivicCode Milestone 12."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from hashlib import sha256
import json
from typing import Any
from uuid import uuid4

from civiccode.section_lifecycle import (
    SectionLifecycleError,
    SectionLifecycleStore,
    chapter_to_dict,
    section_to_dict,
    title_to_dict,
    version_to_dict,
)
from civiccode.source_registry import (
    SourceRegistryError,
    SourceRegistryStore,
    compute_reference_checksum,
    source_to_staff_dict,
)


CONNECTOR_TYPES = {"csv_bundle", "official_html_extract"}


class CivicCodeImportError(ValueError):
    """Import validation error with an operator-facing recovery path."""

    def __init__(self, message: str, fix: str, status_code: int = 422) -> None:
        super().__init__(message)
        self.message = message
        self.fix = fix
        self.status_code = status_code

    def detail(self) -> dict[str, str]:
        return {"message": self.message, "fix": self.fix}


@dataclass(slots=True)
class ImportJob:
    """Auditable local import job record."""

    job_id: str
    connector_type: str
    actor: str
    status: str = "pending"
    retry_of: str | None = None
    counts: dict[str, int] = field(default_factory=dict)
    provenance: dict[str, Any] = field(default_factory=dict)
    failure: dict[str, str] | None = None
    source_id: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None


class ImportConnectorStore:
    """In-memory import coordinator for local fixture/file-drop source bundles."""

    def __init__(
        self,
        *,
        source_store: SourceRegistryStore,
        section_store: SectionLifecycleStore,
    ) -> None:
        self._jobs: dict[str, ImportJob] = {}
        self._source_store = source_store
        self._section_store = section_store

    def run_import(
        self,
        payload: dict[str, Any],
        *,
        actor: str,
        retry_of: str | None = None,
    ) -> ImportJob:
        connector_type = payload.get("connector_type", "")
        job = ImportJob(
            job_id=payload.get("job_id") or f"import_{uuid4().hex}",
            connector_type=connector_type,
            actor=actor,
            retry_of=retry_of,
            provenance=_base_provenance(payload),
            source_id=payload.get("source", {}).get("source_id"),
        )
        self._jobs[job.job_id] = job
        try:
            self._validate_payload(payload)
            job.counts = self._apply_payload(payload)
            job.status = "completed"
            job.completed_at = datetime.now(UTC)
        except (CivicCodeImportError, SourceRegistryError, SectionLifecycleError) as exc:
            job.status = "failed"
            job.failure = _failure_detail(exc)
            job.counts = _empty_counts()
            job.completed_at = datetime.now(UTC)
        return job

    def retry_import(self, job_id: str, payload: dict[str, Any], *, actor: str) -> ImportJob:
        original = self.get(job_id)
        if original.status != "failed":
            raise CivicCodeImportError(
                f"Import job '{job_id}' is not failed.",
                "Retry only failed import jobs. Re-import completed jobs by posting the bundle again.",
                status_code=409,
            )
        return self.run_import(payload, actor=actor, retry_of=job_id)

    def get(self, job_id: str) -> ImportJob:
        try:
            return self._jobs[job_id]
        except KeyError as exc:
            raise CivicCodeImportError(
                f"Import job '{job_id}' was not found.",
                "Check the import job id or submit a new local import bundle.",
                status_code=404,
            ) from exc

    def list_jobs(self) -> list[ImportJob]:
        return sorted(self._jobs.values(), key=lambda job: job.created_at)

    def reset(self) -> None:
        self._jobs.clear()

    def _validate_payload(self, payload: dict[str, Any]) -> None:
        connector_type = payload.get("connector_type")
        if connector_type not in CONNECTOR_TYPES:
            raise CivicCodeImportError(
                f"Unknown connector_type '{connector_type}'.",
                f"Use one of: {', '.join(sorted(CONNECTOR_TYPES))}.",
            )
        source = payload.get("source") or {}
        if not source.get("source_id"):
            raise CivicCodeImportError(
                "Import bundle source requires source_id.",
                "Add source.source_id so imported sections can cite their official source.",
            )
        title_ids = {item["title_id"] for item in payload.get("titles", [])}
        chapter_ids = {item["chapter_id"] for item in payload.get("chapters", [])}
        section_ids = {item["section_id"] for item in payload.get("sections", [])}

        for chapter in payload.get("chapters", []):
            title_id = chapter["title_id"]
            if title_id not in title_ids and not _exists(lambda: self._section_store.get_title(title_id)):
                raise CivicCodeImportError(
                    f"Chapter '{chapter['chapter_id']}' references missing title '{title_id}'.",
                    "Include the title in the same bundle or import it before this chapter.",
                )
        for section in payload.get("sections", []):
            chapter_id = section["chapter_id"]
            if chapter_id not in chapter_ids and not _exists(lambda: self._section_store.get_chapter(chapter_id)):
                raise CivicCodeImportError(
                    f"Section '{section['section_id']}' references missing chapter '{chapter_id}'.",
                    "Include the chapter in the same bundle or import it before this section.",
                )
        for version in payload.get("versions", []):
            section_id = version["section_id"]
            if section_id not in section_ids and not _exists(lambda: self._section_store.get_section(section_id)):
                raise CivicCodeImportError(
                    f"Version '{version['version_id']}' references missing section '{section_id}'.",
                    "Include the section in the same bundle or import it before this version.",
                )
            if version["source_id"] != source["source_id"] and not _exists(
                lambda: self._source_store.get(version["source_id"])
            ):
                raise CivicCodeImportError(
                    f"Version '{version['version_id']}' references missing source '{version['source_id']}'.",
                    "Use the bundle source_id or register the referenced source before import.",
                )

    def _apply_payload(self, payload: dict[str, Any]) -> dict[str, int]:
        counts = _empty_counts()
        source = dict(payload["source"])
        if source.get("checksum") is None and source.get("file_reference"):
            source["checksum"] = compute_reference_checksum(source["file_reference"])
        _create_or_reuse(
            lambda: self._source_store.create(source),
            lambda: self._source_store.get(source["source_id"]),
            counts,
            "sources",
        )
        for title in payload.get("titles", []):
            _create_or_reuse(
                lambda item=title: self._section_store.create_title(item),
                lambda item=title: self._section_store.get_title(item["title_id"]),
                counts,
                "titles",
            )
        for chapter in payload.get("chapters", []):
            _create_or_reuse(
                lambda item=chapter: self._section_store.create_chapter(item),
                lambda item=chapter: self._section_store.get_chapter(item["chapter_id"]),
                counts,
                "chapters",
            )
        for section in payload.get("sections", []):
            _create_or_reuse(
                lambda item=section: self._section_store.create_section(item),
                lambda item=section: self._section_store.get_section(item["section_id"]),
                counts,
                "sections",
            )
        for version in payload.get("versions", []):
            _create_or_reuse(
                lambda item=version: self._section_store.create_version(item),
                lambda item=version: self._section_store.get_version(item["version_id"]),
                counts,
                "versions",
            )
        return counts


def job_to_dict(job: ImportJob) -> dict[str, Any]:
    return {
        "job_id": job.job_id,
        "connector_type": job.connector_type,
        "status": job.status,
        "source_id": job.source_id,
        "actor": job.actor,
        "retry_of": job.retry_of,
        "counts": job.counts,
        "provenance": job.provenance,
        "failure": job.failure,
        "background": {
            "mode": "synchronous_local",
            "worker": "not_required_for_milestone_12",
            "failure_visibility": "GET /api/v1/civiccode/staff/imports/{job_id}",
        },
        "created_at": job.created_at.isoformat(),
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        "code_answer_behavior": "not_available",
    }


def provenance_report(job: ImportJob, source_store: SourceRegistryStore) -> dict[str, Any]:
    source_payload = None
    if job.source_id:
        try:
            source_payload = source_to_staff_dict(source_store.get(job.source_id))
        except SourceRegistryError:
            source_payload = None
    return {
        "job": job_to_dict(job),
        "source": source_payload,
        "report": {
            "summary": "Local import provenance report.",
            "fixture_checksum": job.provenance.get("fixture_checksum"),
            "retrieval_method": job.provenance.get("retrieval_method"),
            "no_outbound_dependency": True,
            "legal_boundary": "Imported text is source material, not legal advice.",
        },
    }


def imported_tree_snapshot(
    source_id: str,
    source_store: SourceRegistryStore,
    section_store: SectionLifecycleStore,
) -> dict[str, Any]:
    source = source_store.get(source_id)
    versions = [
        version
        for version in section_store._versions.values()  # noqa: SLF001
        if version.source_id == source_id
    ]
    section_ids = {version.section_id for version in versions}
    sections = [
        section
        for section_id in section_ids
        if (section := section_store.get_section(section_id))
    ]
    chapter_ids = {section.chapter_id for section in sections}
    chapters = [
        chapter
        for chapter_id in chapter_ids
        if (chapter := section_store.get_chapter(chapter_id))
    ]
    title_ids = {chapter.title_id for chapter in chapters}
    titles = [
        title
        for title_id in title_ids
        if (title := section_store.get_title(title_id))
    ]
    return {
        "source": source_to_staff_dict(source),
        "titles": sorted([title_to_dict(title) for title in titles], key=lambda item: item["title_id"]),
        "chapters": sorted([chapter_to_dict(chapter) for chapter in chapters], key=lambda item: item["chapter_id"]),
        "sections": sorted([section_to_dict(section) for section in sections], key=lambda item: item["section_id"]),
        "versions": sorted([version_to_dict(version) for version in versions], key=lambda item: item["version_id"]),
        "code_answer_behavior": "not_available",
    }


def _create_or_reuse(create, get_existing, counts: dict[str, int], key: str) -> None:
    try:
        create()
        counts[f"{key}_created"] += 1
    except (SourceRegistryError, SectionLifecycleError) as exc:
        if exc.status_code != 409:
            raise
        get_existing()
        counts[f"{key}_reused"] += 1


def _base_provenance(payload: dict[str, Any]) -> dict[str, Any]:
    source = payload.get("source", {})
    serialized = json.dumps(payload, sort_keys=True, default=str)
    return {
        "connector_type": payload.get("connector_type"),
        "source_id": source.get("source_id"),
        "source_name": source.get("name"),
        "source_url": source.get("source_url"),
        "file_reference": source.get("file_reference"),
        "retrieval_method": source.get("retrieval_method") or payload.get("provenance", {}).get("retrieval_method"),
        "fixture_name": payload.get("provenance", {}).get("fixture_name"),
        "fixture_checksum": sha256(serialized.encode("utf-8")).hexdigest(),
        "no_outbound_dependency": True,
    }


def _failure_detail(exc: Exception) -> dict[str, str]:
    if isinstance(exc, (CivicCodeImportError, SourceRegistryError, SectionLifecycleError)):
        return exc.detail()
    return {
        "message": str(exc),
        "fix": "Review the import bundle and retry with corrected source, section, or version data.",
    }


def _empty_counts() -> dict[str, int]:
    return {
        "sources_created": 0,
        "sources_reused": 0,
        "titles_created": 0,
        "titles_reused": 0,
        "chapters_created": 0,
        "chapters_reused": 0,
        "sections_created": 0,
        "sections_reused": 0,
        "versions_created": 0,
        "versions_reused": 0,
    }


def _exists(callback) -> bool:
    try:
        callback()
    except (SourceRegistryError, SectionLifecycleError):
        return False
    return True
