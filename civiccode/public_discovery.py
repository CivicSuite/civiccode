"""Public discovery aids for CivicCode resident lookup surfaces."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


QUESTION_STATUSES = {"draft", "approved", "retired"}
QUESTION_AUDIENCES = {"public", "staff"}
DISCOVERY_CLASSIFICATION = "navigation_aid_not_legal_determination"


class PublicDiscoveryError(ValueError):
    """Validation error with a public/staff-facing fix path."""

    def __init__(self, message: str, fix: str, status_code: int = 422) -> None:
        super().__init__(message)
        self.message = message
        self.fix = fix
        self.status_code = status_code

    def detail(self) -> dict[str, str]:
        return {"message": self.message, "fix": self.fix}


@dataclass(slots=True)
class PopularQuestion:
    question_id: str
    question_text: str
    section_id: str
    section_number: str
    section_heading: str
    answer_excerpt: str
    citation_payload: dict[str, Any]
    audience: str = "public"
    status: str = "draft"
    is_popular: bool = True
    approved_by: str | None = None
    approved_at: datetime | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class PopularQuestionStore:
    """In-memory popular-question store with public-safe filtering."""

    def __init__(self) -> None:
        self._questions: dict[str, PopularQuestion] = {}

    def create(self, data: dict[str, Any], *, actor: str) -> PopularQuestion:
        status = data.get("status", "draft")
        audience = data.get("audience", "public")
        if status not in QUESTION_STATUSES:
            raise PublicDiscoveryError(
                f"Unknown popular-question status '{status}'.",
                f"Use one of: {', '.join(sorted(QUESTION_STATUSES))}.",
            )
        if audience not in QUESTION_AUDIENCES:
            raise PublicDiscoveryError(
                f"Unknown popular-question audience '{audience}'.",
                f"Use one of: {', '.join(sorted(QUESTION_AUDIENCES))}.",
            )
        question = PopularQuestion(
            question_id=data.get("question_id") or f"question_{uuid4().hex}",
            question_text=data["question_text"],
            section_id=data["section_id"],
            section_number=data["section_number"],
            section_heading=data["section_heading"],
            answer_excerpt=data["answer_excerpt"],
            citation_payload=data["citation_payload"],
            audience=audience,
            status=status,
            is_popular=bool(data.get("is_popular", True)),
            approved_by=actor if status == "approved" else None,
            approved_at=datetime.now(UTC) if status == "approved" else None,
        )
        if question.question_id in self._questions:
            raise PublicDiscoveryError(
                f"Popular question '{question.question_id}' already exists.",
                "Use a unique question_id or update the existing question instead.",
                status_code=409,
            )
        self._questions[question.question_id] = question
        return question

    def public_popular_questions(self) -> list[PopularQuestion]:
        return sorted(
            [
                question
                for question in self._questions.values()
                if question.status == "approved"
                and question.audience == "public"
                and question.is_popular
            ],
            key=lambda question: (question.section_number, question.question_text),
        )

    def reset(self) -> None:
        self._questions.clear()


def popular_question_to_public_dict(question: PopularQuestion) -> dict[str, Any]:
    citation = question.citation_payload.get("citation") or {}
    return {
        "question_id": question.question_id,
        "question_text": question.question_text,
        "section_id": question.section_id,
        "section_number": question.section_number,
        "section_heading": question.section_heading,
        "answer_excerpt": question.answer_excerpt,
        "section_url": f"/civiccode/sections/{question.section_number}",
        "citation": citation,
        "classification": DISCOVERY_CLASSIFICATION,
        "legal_determination": "not_provided",
        "code_answer_behavior": "navigation_aid",
        "public_label": "Staff-approved navigation aid, not a legal determination.",
    }


def related_material_to_public_dict(item: dict[str, Any]) -> dict[str, Any]:
    return {
        **item,
        "classification": DISCOVERY_CLASSIFICATION,
        "legal_determination": "not_provided",
        "code_answer_behavior": "navigation_aid",
        "public_label": "Related material is a navigation aid, not a legal determination.",
    }
