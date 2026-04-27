"""CivicClerk ordinance/adoption handoff intake for CivicCode."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


HANDOFF_STATUSES = {"adopted", "pending", "failed"}
CONFLICT_TERMS = ("amend", "amending", "repeal", "repealing", "supersede", "replace")


class OrdinanceHandoffError(ValueError):
    """Validation error with an operator-facing fix path."""

    def __init__(self, message: str, fix: str, status_code: int = 422) -> None:
        super().__init__(message)
        self.message = message
        self.fix = fix
        self.status_code = status_code

    def detail(self) -> dict[str, str]:
        return {"message": self.message, "fix": self.fix}


@dataclass(slots=True)
class OrdinanceEvent:
    event_id: str
    external_event_id: str
    civicclerk_meeting_id: str
    civicclerk_agenda_item_id: str
    ordinance_number: str
    title: str
    status: str
    affected_sections: list[str]
    source_document_url: str
    source_document_hash: str
    ordinance_text: str = ""
    adopted_at: datetime | None = None
    failure_reason: str | None = None
    created_by: str = "unknown"
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def handoff_state(self) -> str:
        if self.status == "failed":
            return "failed"
        return "pending_codification"


@dataclass(slots=True)
class HandoffAuditEvent:
    event_id: str
    event_type: str
    actor: str
    target_id: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class OrdinanceHandoffStore:
    """In-memory CivicClerk handoff store for Milestone 10 API behavior."""

    def __init__(self) -> None:
        self._events: dict[str, OrdinanceEvent] = {}
        self._audit_events: list[HandoffAuditEvent] = []

    def create_event(self, data: dict[str, Any], *, actor: str) -> OrdinanceEvent:
        status = data.get("status", "pending")
        if status not in HANDOFF_STATUSES:
            raise OrdinanceHandoffError(
                f"Unknown CivicClerk handoff status '{status}'.",
                f"Use one of: {', '.join(sorted(HANDOFF_STATUSES))}.",
            )
        affected_sections = list(data.get("affected_sections", []))
        if not affected_sections:
            raise OrdinanceHandoffError(
                "CivicClerk handoff must identify at least one affected section.",
                "Populate affected_sections with the section numbers touched by the ordinance.",
            )
        for required in [
            "external_event_id",
            "civicclerk_meeting_id",
            "civicclerk_agenda_item_id",
            "ordinance_number",
            "title",
            "source_document_url",
            "source_document_hash",
        ]:
            if not data.get(required):
                raise OrdinanceHandoffError(
                    f"CivicClerk handoff is missing {required}.",
                    f"Include {required} from CivicClerk before sending the handoff.",
                )
        if status == "failed" and not data.get("failure_reason"):
            raise OrdinanceHandoffError(
                "Failed CivicClerk handoffs require a failure_reason.",
                "Explain what failed so staff can repair and resend the handoff.",
            )

        event = OrdinanceEvent(
            event_id=data.get("event_id") or f"ord_{uuid4().hex}",
            external_event_id=data["external_event_id"],
            civicclerk_meeting_id=data["civicclerk_meeting_id"],
            civicclerk_agenda_item_id=data["civicclerk_agenda_item_id"],
            ordinance_number=data["ordinance_number"],
            title=data["title"],
            status=status,
            affected_sections=affected_sections,
            source_document_url=data["source_document_url"],
            source_document_hash=data["source_document_hash"],
            ordinance_text=data.get("ordinance_text", ""),
            adopted_at=data.get("adopted_at"),
            failure_reason=data.get("failure_reason"),
            created_by=actor,
        )
        if event.event_id in self._events:
            raise OrdinanceHandoffError(
                f"CivicClerk ordinance event '{event.event_id}' already exists.",
                "Use a unique event_id or read the existing handoff.",
                status_code=409,
            )
        self._events[event.event_id] = event
        self._append_event("civicclerk_handoff_received", actor=actor, target_id=event.event_id)
        return event

    def warnings_for_section(self, section_number: str) -> list[dict[str, Any]]:
        warnings = []
        for event in self._events.values():
            if section_number not in event.affected_sections:
                continue
            warnings.append(
                {
                    "source": "CivicClerk",
                    "external_event_id": event.external_event_id,
                    "ordinance_number": event.ordinance_number,
                    "handoff_state": event.handoff_state,
                    "message": (
                        f"CivicClerk ordinance {event.ordinance_number} may affect "
                        f"section {section_number}."
                    ),
                    "fix": (
                        f"Review CivicClerk event {event.external_event_id} before treating "
                        "the codified text as fully current."
                    ),
                    "failure_reason": event.failure_reason,
                }
            )
        return warnings

    def audit_events(self) -> list[HandoffAuditEvent]:
        return list(self._audit_events)

    def reset(self) -> None:
        self._events.clear()
        self._audit_events.clear()

    def _append_event(self, event_type: str, *, actor: str, target_id: str) -> None:
        self._audit_events.append(
            HandoffAuditEvent(
                event_id=f"audit_{uuid4().hex}",
                event_type=event_type,
                actor=actor,
                target_id=target_id,
            )
        )


def event_to_dict(event: OrdinanceEvent) -> dict[str, Any]:
    return {
        "event_id": event.event_id,
        "external_event_id": event.external_event_id,
        "ordinance_number": event.ordinance_number,
        "title": event.title,
        "status": event.status,
        "handoff_state": event.handoff_state,
        "affected_sections": event.affected_sections,
        "source_document_url": event.source_document_url,
        "source_document_hash": event.source_document_hash,
        "failure_reason": event.failure_reason,
        "provenance": {
            "civicclerk_meeting_id": event.civicclerk_meeting_id,
            "civicclerk_agenda_item_id": event.civicclerk_agenda_item_id,
        },
        "likely_conflicts": likely_conflicts(event),
        "code_answer_behavior": "not_available",
    }


def likely_conflicts(event: OrdinanceEvent) -> list[dict[str, str]]:
    lowered = f"{event.title} {event.ordinance_text}".lower()
    has_conflict_term = any(term in lowered for term in CONFLICT_TERMS)
    conflicts = []
    for section_number in event.affected_sections:
        if has_conflict_term or section_number.lower() in lowered:
            conflicts.append(
                {
                    "section_number": section_number,
                    "trigger": "ordinance_text_or_title_references_existing_section",
                    "source_event_id": event.external_event_id,
                }
            )
    return conflicts


def handoff_audit_event_to_dict(event: HandoffAuditEvent) -> dict[str, Any]:
    return {
        "event_id": event.event_id,
        "event_type": event.event_type,
        "actor": event.actor,
        "target_id": event.target_id,
        "created_at": event.created_at.isoformat(),
    }
