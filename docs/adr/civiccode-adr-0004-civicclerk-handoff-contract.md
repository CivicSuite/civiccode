# CivicCode ADR-0004: CivicClerk Ordinance Handoff Contract

## Status

Proposed.

## Context

CivicClerk v0.1.0 records ordinance and resolution adoption concepts. CivicCode
needs a receiving contract before it can mark code stale or ingest adopted
ordinance events.

## Decision

Status: Open Question - pending human decision.

## Consequences

CivicCode must not hard-code a CivicClerk event shape before this contract is
accepted.
