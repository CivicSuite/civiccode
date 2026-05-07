# CivicCode ADR-0004: CivicClerk Ordinance Handoff Contract

## Status

Proposed.

## Context

CivicClerk v0.1.0 records ordinance and resolution adoption concepts. CivicCode
needs a receiving contract before it can mark code stale or ingest adopted
ordinance events.

## Decision

Status: Proposed.

CivicCode accepts CivicClerk ordinance handoffs keyed by CivicClerk
`external_event_id` and the source payload fields that preserve meeting,
agenda item, ordinance, affected section, source document, status, text, and
failure provenance.

Replaying the same accepted `external_event_id` with the same source payload is
idempotent: CivicCode returns the existing handoff event and does not create a
second audit record, replay record, or pending-codification warning.

Replaying an accepted `external_event_id` with divergent source payload data is
rejected with an operator-actionable 409 conflict. The fix path tells staff to
read the existing handoff and either reconcile the stored handoff with clerk
staff or send a new CivicClerk `external_event_id` for the corrected event.
Duplicate CivicCode internal `event_id` values remain conflicts.

## Consequences

CivicCode can safely accept at-least-once CivicClerk delivery without duplicate
pending-codification warnings, while still blocking silent rewrites of an
already accepted clerk event.
