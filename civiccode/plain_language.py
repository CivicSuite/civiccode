"""Staff-approved non-authoritative summaries for CivicCode."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


SUMMARY_STATUSES = {"draft", "approved", "retired"}


class PlainLanguageSummaryError(ValueError):
    """Validation error with an operator-facing fix path."""

    def __init__(self, message: str, fix: str, status_code: int = 422) -> None:
        super().__init__(message)
        self.message = message
        self.fix = fix
        self.status_code = status_code

    def detail(self) -> dict[str, str]:
        return {"message": self.message, "fix": self.fix}


@dataclass(slots=True)
class PlainLanguageSummary:
    summary_id: str
    section_id: str
    section_version_id: str
    summary_text: str
    status: str
    language_code: str = "en"
    created_by: str = "unknown"
    approved_by: str | None = None
    approved_at: datetime | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def public_visible(self) -> bool:
        return self.status == "approved"


@dataclass(slots=True)
class SummaryAuditEvent:
    event_id: str
    event_type: str
    actor: str
    section_id: str
    target_id: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class PlainLanguageSummaryStore:
    """In-memory summary and audit store for the Milestone 9 API."""

    def __init__(self) -> None:
        self._summaries: dict[str, PlainLanguageSummary] = {}
        self._audit_events: list[SummaryAuditEvent] = []

    def create_summary(
        self,
        section_id: str,
        data: dict[str, Any],
        *,
        actor: str,
    ) -> PlainLanguageSummary:
        status = data.get("status", "draft")
        if status not in SUMMARY_STATUSES:
            raise PlainLanguageSummaryError(
                f"Unknown plain-language summary status '{status}'.",
                f"Use one of: {', '.join(sorted(SUMMARY_STATUSES))}.",
            )
        if status == "approved":
            raise PlainLanguageSummaryError(
                "Plain-language summaries must be approved through the approval endpoint.",
                "Create the summary as draft first, then approve it after staff review.",
            )
        summary = PlainLanguageSummary(
            summary_id=data.get("summary_id") or f"summary_{uuid4().hex}",
            section_id=section_id,
            section_version_id=data["section_version_id"],
            summary_text=data["summary_text"],
            status=status,
            language_code=data.get("language_code", "en"),
            created_by=actor,
        )
        if summary.summary_id in self._summaries:
            raise PlainLanguageSummaryError(
                f"Plain-language summary '{summary.summary_id}' already exists.",
                "Use a unique summary_id or read the existing summary.",
                status_code=409,
            )
        self._summaries[summary.summary_id] = summary
        self._append_event(
            "plain_language_summary_created",
            actor=actor,
            section_id=section_id,
            target_id=summary.summary_id,
        )
        return summary

    def approve_summary(self, summary_id: str, *, actor: str) -> PlainLanguageSummary:
        summary = self.get_summary(summary_id)
        if summary.status == "retired":
            raise PlainLanguageSummaryError(
                f"Plain-language summary '{summary_id}' is retired.",
                "Create a new draft summary for staff review instead of approving a retired one.",
                status_code=409,
            )
        summary.status = "approved"
        summary.approved_by = actor
        summary.approved_at = datetime.now(UTC)
        self._append_event(
            "plain_language_summary_approved",
            actor=actor,
            section_id=summary.section_id,
            target_id=summary.summary_id,
        )
        return summary

    def list_for_section(
        self,
        section_id: str,
        *,
        include_unapproved: bool = False,
    ) -> list[PlainLanguageSummary]:
        summaries = [
            summary
            for summary in self._summaries.values()
            if summary.section_id == section_id
            and (include_unapproved or summary.public_visible)
        ]
        return sorted(summaries, key=lambda summary: summary.created_at)

    def list_all(self, *, include_unapproved: bool = False) -> list[PlainLanguageSummary]:
        summaries = [
            summary
            for summary in self._summaries.values()
            if include_unapproved or summary.public_visible
        ]
        return sorted(summaries, key=lambda summary: summary.created_at)

    def get_summary(self, summary_id: str) -> PlainLanguageSummary:
        try:
            return self._summaries[summary_id]
        except KeyError as exc:
            raise PlainLanguageSummaryError(
                f"Plain-language summary '{summary_id}' was not found.",
                "Create the summary before trying to approve or read it.",
                status_code=404,
            ) from exc

    def audit_events(self) -> list[SummaryAuditEvent]:
        return list(self._audit_events)

    def reset(self) -> None:
        self._summaries.clear()
        self._audit_events.clear()

    def _append_event(
        self,
        event_type: str,
        *,
        actor: str,
        section_id: str,
        target_id: str,
    ) -> None:
        self._audit_events.append(
            SummaryAuditEvent(
                event_id=f"audit_{uuid4().hex}",
                event_type=event_type,
                actor=actor,
                section_id=section_id,
                target_id=target_id,
            )
        )


def summary_to_staff_dict(summary: PlainLanguageSummary) -> dict[str, Any]:
    return {
        "summary_id": summary.summary_id,
        "section_id": summary.section_id,
        "section_version_id": summary.section_version_id,
        "summary_text": summary.summary_text,
        "status": summary.status,
        "language_code": summary.language_code,
        "authority": "non_authoritative_explanation",
        "warning": "Plain-language summaries are not law.",
        "public_visible": summary.public_visible,
        "created_by": summary.created_by,
        "approved_by": summary.approved_by,
        "approved_at": summary.approved_at.isoformat() if summary.approved_at else None,
        "created_at": summary.created_at.isoformat(),
    }


def summary_to_public_dict(
    summary: PlainLanguageSummary,
    *,
    authoritative_section: dict[str, Any],
    authoritative_text: str,
) -> dict[str, Any]:
    return {
        "summary_id": summary.summary_id,
        "section_id": summary.section_id,
        "section_version_id": summary.section_version_id,
        "summary_text": summary.summary_text,
        "language_code": summary.language_code,
        "authority": "non_authoritative_explanation",
        "warning": "Plain-language summaries are not law.",
        "authoritative_section": authoritative_section,
        "authoritative_text": authoritative_text,
    }


def summary_audit_event_to_dict(event: SummaryAuditEvent) -> dict[str, Any]:
    return {
        "event_id": event.event_id,
        "event_type": event.event_type,
        "actor": event.actor,
        "section_id": event.section_id,
        "target_id": event.target_id,
        "created_at": event.created_at.isoformat(),
    }
