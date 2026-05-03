"""Codifier live-sync readiness and local-run foundation for CivicCode."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from civiccore import (
    SyncCircuitState,
    SyncRunResult,
    apply_sync_run_result,
    build_sync_operator_status,
    build_sync_source_status,
    compute_next_sync_at,
    validate_cron_expression,
    validate_url_host,
)

from civiccode.import_connectors import ImportConnectorStore, job_to_dict
from civiccode.source_registry import CodeSource, SourceRegistryStore


CODIFIER_DELTA_QUERY_PARAMS = {
    "municode": "updatedSince",
    "american_legal": "modifiedAfter",
    "code_publishing": "changed_since",
    "general_code": "lastModified",
}


class CodifierSyncError(ValueError):
    """Actionable sync configuration or runtime error."""

    def __init__(self, message: str, fix: str, status_code: int = 422) -> None:
        super().__init__(message)
        self.message = message
        self.fix = fix
        self.status_code = status_code

    def detail(self) -> dict[str, str]:
        return {"message": self.message, "fix": self.fix}


@dataclass(frozen=True, slots=True)
class CodifierDeltaPlan:
    """Operator-visible planned codifier request."""

    connector: str
    request_url: str
    delta_enabled: bool
    cursor_param: str | None
    cursor_value: str | None
    message: str
    fix: str

    def public_dict(self) -> dict[str, str | bool | None]:
        return {
            "connector": self.connector,
            "request_url": self.request_url,
            "delta_enabled": self.delta_enabled,
            "cursor_param": self.cursor_param,
            "cursor_value": self.cursor_value,
            "message": self.message,
            "fix": self.fix,
        }


@dataclass(slots=True)
class CodifierSyncSource:
    """Configured codifier sync source backed by a registered CivicCode source."""

    source_id: str
    connector: str
    source_name: str
    source_url: str
    sync_schedule: str
    allowlisted_hosts: tuple[str, ...] = ()
    last_successful_sync_at: datetime | None = None
    last_attempted_sync_at: datetime | None = None
    last_import_job_id: str | None = None
    state: SyncCircuitState = field(default_factory=lambda: SyncCircuitState(connector="codifier"))

    @property
    def next_sync_at(self) -> datetime | None:
        return compute_next_sync_at(self.sync_schedule, self.last_successful_sync_at)


@dataclass(frozen=True, slots=True)
class CodifierSyncRun:
    """Result of one local codifier sync run."""

    source: CodifierSyncSource
    job_payload: dict[str, Any]
    delta_plan: CodifierDeltaPlan

    def public_dict(self) -> dict[str, Any]:
        return {
            "source": sync_source_to_dict(self.source),
            "import_job": self.job_payload,
            "delta_plan": self.delta_plan.public_dict(),
            "legal_boundary": (
                "Codifier sync imports source material for staff review. It does not provide legal "
                "advice and does not automatically codify ordinances."
            ),
        }


class CodifierSyncStore:
    """In-memory codifier sync coordinator for staff-controlled source pulls."""

    def __init__(
        self,
        *,
        source_store: SourceRegistryStore,
        import_store: ImportConnectorStore,
    ) -> None:
        self._source_store = source_store
        self._import_store = import_store
        self._sources: dict[str, CodifierSyncSource] = {}

    def configure_source(
        self,
        *,
        source_id: str,
        sync_schedule: str,
        allowlisted_hosts: tuple[str, ...] = (),
    ) -> CodifierSyncSource:
        source = self._source_store.get(source_id)
        _validate_source_for_sync(source)
        _validate_sync_schedule(sync_schedule)
        assert source.source_url is not None
        try:
            validate_url_host(source.source_url, allowlisted_hosts)
        except ValueError as exc:
            raise CodifierSyncError(
                "Codifier sync source URL failed host validation.",
                (
                    "Use an HTTPS public vendor endpoint or add the intended on-prem host to the "
                    "source-specific allowlist before enabling sync."
                ),
            ) from exc
        configured = CodifierSyncSource(
            source_id=source.source_id,
            connector=source.source_type,
            source_name=source.name,
            source_url=source.source_url,
            sync_schedule=sync_schedule,
            allowlisted_hosts=tuple(allowlisted_hosts),
            state=SyncCircuitState(connector=source.source_type, source_name=source.name),
        )
        self._sources[source_id] = configured
        return configured

    def get_source(self, source_id: str) -> CodifierSyncSource:
        try:
            return self._sources[source_id]
        except KeyError as exc:
            raise CodifierSyncError(
                f"Codifier sync source '{source_id}' is not configured.",
                "Run the sync readiness configuration step before starting a sync run.",
                status_code=404,
            ) from exc

    def list_sources(self) -> tuple[CodifierSyncSource, ...]:
        return tuple(sorted(self._sources.values(), key=lambda source: source.source_id))

    def run_local_payload(
        self,
        *,
        source_id: str,
        payload: dict[str, Any],
        actor: str,
        changed_since: datetime | None = None,
        now: datetime | None = None,
    ) -> CodifierSyncRun:
        configured = self.get_source(source_id)
        if configured.state.sync_paused:
            raise CodifierSyncError(
                f"Codifier sync for '{configured.source_name}' is paused by the circuit breaker.",
                "Review the last failure, fix the source or payload, then reconfigure the source to close the circuit.",
                status_code=409,
            )
        delta_plan = plan_codifier_delta_request(
            connector=configured.connector,
            source_url=configured.source_url,
            changed_since=changed_since or configured.last_successful_sync_at,
        )
        job = self._import_store.run_import(payload, actor=actor)
        attempted_at = now or datetime.now(UTC)
        if job.status == "completed":
            result = SyncRunResult(
                records_discovered=sum(job.counts.values()),
                records_succeeded=1,
                records_failed=0,
            )
            configured.last_successful_sync_at = attempted_at
        else:
            result = SyncRunResult(
                records_discovered=1,
                records_succeeded=0,
                records_failed=1,
                error_summary=(job.failure or {}).get("message"),
            )
        configured.last_attempted_sync_at = attempted_at
        configured.last_import_job_id = job.job_id
        configured.state = apply_sync_run_result(configured.state, result, now=attempted_at)
        return CodifierSyncRun(
            source=configured,
            job_payload=job_to_dict(job),
            delta_plan=delta_plan,
        )

    def reset(self) -> None:
        self._sources.clear()


def plan_codifier_delta_request(
    *,
    connector: str,
    source_url: str,
    changed_since: datetime | None,
) -> CodifierDeltaPlan:
    """Build a codifier request plan without making a vendor call."""

    normalized_connector = connector.strip().lower()
    cursor_param = CODIFIER_DELTA_QUERY_PARAMS.get(normalized_connector)
    if changed_since is None or cursor_param is None:
        return CodifierDeltaPlan(
            connector=normalized_connector,
            request_url=source_url,
            delta_enabled=False,
            cursor_param=cursor_param,
            cursor_value=None,
            message="Codifier sync will run a full source request.",
            fix="After one successful import, subsequent runs can use the recorded cursor for delta pulls.",
        )
    cursor_value = _format_cursor(changed_since)
    return CodifierDeltaPlan(
        connector=normalized_connector,
        request_url=_with_query_param(source_url, cursor_param, cursor_value),
        delta_enabled=True,
        cursor_param=cursor_param,
        cursor_value=cursor_value,
        message=f"{normalized_connector} codifier sync will request changes since {cursor_value}.",
        fix="If staff sees missed sections, reset the cursor and run one full reconciliation import.",
    )


def sync_source_to_dict(source: CodifierSyncSource) -> dict[str, Any]:
    """Return staff-safe codifier sync source state."""

    source_status = build_sync_source_status(
        source.state,
        sync_schedule=source.sync_schedule,
        last_sync_at=source.last_successful_sync_at,
    ).public_dict()
    next_sync_at = source_status["next_sync_at"]
    return {
        "source_id": source.source_id,
        "connector": source.connector,
        "source_name": source.source_name,
        "source_url": source.source_url,
        "sync_schedule": source.sync_schedule,
        "next_sync_at": next_sync_at.isoformat() if isinstance(next_sync_at, datetime) else None,
        "last_successful_sync_at": source.last_successful_sync_at.isoformat()
        if source.last_successful_sync_at
        else None,
        "last_attempted_sync_at": source.last_attempted_sync_at.isoformat()
        if source.last_attempted_sync_at
        else None,
        "last_import_job_id": source.last_import_job_id,
        "source_status": source_status,
        "operator_status": build_sync_operator_status(source.state).public_dict(),
    }


def _validate_source_for_sync(source: CodeSource) -> None:
    if source.source_type not in CODIFIER_DELTA_QUERY_PARAMS:
        raise CodifierSyncError(
            f"Source type '{source.source_type}' is not supported for codifier sync.",
            "Use one of: american_legal, code_publishing, general_code, municode.",
        )
    if not source.is_official or source.status != "active":
        raise CodifierSyncError(
            "Codifier sync requires an active official source.",
            "Mark the source official, complete provenance, and transition it to active before enabling sync.",
        )
    if not source.source_url:
        raise CodifierSyncError(
            "Codifier sync requires a source_url.",
            "Register the official vendor URL before enabling sync.",
        )


def _validate_sync_schedule(sync_schedule: str) -> None:
    try:
        validate_cron_expression(sync_schedule, minimum_interval_minutes=15)
    except ValueError as exc:
        raise CodifierSyncError(
            "Codifier sync schedule is invalid or too frequent.",
            "Use a standard five-field cron expression that runs no more often than every 15 minutes.",
        ) from exc


def _format_cursor(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _with_query_param(source_url: str, key: str, value: str) -> str:
    parsed = urlparse(source_url)
    query_items = [(existing_key, existing_value) for existing_key, existing_value in parse_qsl(parsed.query)]
    query_items = [(existing_key, existing_value) for existing_key, existing_value in query_items if existing_key != key]
    query_items.append((key, value))
    return urlunparse(parsed._replace(query=urlencode(query_items)))


__all__ = [
    "CODIFIER_DELTA_QUERY_PARAMS",
    "CodifierDeltaPlan",
    "CodifierSyncError",
    "CodifierSyncRun",
    "CodifierSyncSource",
    "CodifierSyncStore",
    "plan_codifier_delta_request",
    "sync_source_to_dict",
]
