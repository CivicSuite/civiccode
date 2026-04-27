# CivicCode Milestone 0 Reconciliation

Date: 2026-04-27  
Repo: `CivicSuite/civiccode`  
Scope: scaffold and Milestone 0 planning only

## Inputs Read

- `CivicSuite/civicsuite/docs/CivicSuiteUnifiedSpec.md`, sections 11, 18, 19, 20, 21.
- `CivicSuite/civicsuite/docs/roadmap/civiccode-next-module-plan.md`.
- `CivicSuite/civicsuite/specs/01_catalog.md`, "CivicCode - Municipal Code & Ordinance Access."
- Suite ADRs ADR-0001, ADR-0002, ADR-0003.

## Disagreements And Drift

| File path | Current text (verbatim) | Required correction (verbatim) | Driver |
|---|---|---|---|
| `CivicSuite/civicsuite/docs/roadmap/civiccode-next-module-plan.md` | `` `CivicSuite/civiccode` does not exist yet.`` | `` `CivicSuite/civiccode` exists as a scaffold-only repository; no runtime code has shipped.`` | Current repo truth |
| `CivicSuite/civicsuite/docs/roadmap/civiccode-next-module-plan.md` | `1. Create `CivicSuite/civiccode` under the organization.` | `1. Maintain the `CivicSuite/civiccode` scaffold and run Milestone 0 reconciliation before runtime work.` | Current repo truth |
| `CivicSuite/civicsuite/docs/CivicSuiteUnifiedSpec.md` | `CivicCode, CivicAccess, CivicZone, and the rest of the catalog are planned, not implemented.` | `CivicCode exists as a scaffold-only repository; CivicAccess, CivicZone, and the rest of the catalog are planned, not implemented.` | Current repo truth |
| `README.md` | `No runtime application code has shipped.` | Keep. This is correct and must not be softened until runtime exists. | Shipped/planned truth |
| `docs/index.html` | `Scaffold only - no runtime code shipped yet` | Keep. This is correct and must remain current-facing until runtime exists. | Shipped/planned truth |
| `AGENTS.md` | `Do not add runtime code until Milestone 0 is complete and reviewed.` | Keep. Milestone 0 is documentation, ADR, CI, and reconciliation only. | Milestone discipline |
| `AGENTS.md` | `Do not import from unreleased CivicCore placeholders.` | Add a CI gate that enforces this when source files appear. | CivicCore placeholder rule |
| `scripts/verify-docs.sh` | Required artifacts do not include `docs/RECONCILIATION.md`, `docs/MILESTONES.md`, or ADR queue. | Require Milestone 0 artifacts after this milestone lands. | Milestone 0 done definition |
| `docs/CivicSuiteUnifiedSpec.md` | `Whether CivicCode must ship before CivicZone runtime begins.` | Queue as an ADR question; do not decide in code. | Unified spec section 20 |
| `docs/roadmap/civiccode-next-module-plan.md` | `Official source precedence and what happens when sources disagree.` | Queue as ADR-0001. | Roadmap ADR queue |
| `docs/roadmap/civiccode-next-module-plan.md` | `Codifier import strategy: file upload, URL scrape, API, or all three.` | Queue as ADR-0002. | Roadmap ADR queue |
| `docs/roadmap/civiccode-next-module-plan.md` | `Section versioning model and historical effective-date semantics.` | Queue as ADR-0003. | Roadmap ADR queue |
| `docs/roadmap/civiccode-next-module-plan.md` | `CivicClerk ordinance/adoption-event handoff contract.` | Queue as ADR-0004. | Roadmap ADR queue |
| `docs/roadmap/civiccode-next-module-plan.md` | `Legal-disclaimer wording and resident-facing refusal policy.` | Queue as ADR-0005. | Roadmap ADR queue |
| `docs/roadmap/civiccode-next-module-plan.md` | `Staff-only interpretation-note visibility and retention policy.` | Queue as ADR-0006. | Roadmap ADR queue |
| `CivicSuite/civicsuite/docs/architecture/ADR-0002-base-declarative-class-ownership.md` | `Every module that adds tables (records, clerk, code, zone, etc.) imports the same Base from civiccore.` | Runtime milestones must import the shared CivicCore Base; do not declare a local SQLAlchemy Base. | ADR-0002 |
| `CivicSuite/civicsuite/docs/architecture/ADR-0003-civiccore-alembic-baseline-strategy.md` | `Its upgrade() declares the union of shared-table schema as-of records HEAD 019_encrypt_connection_config.` | CivicCode migrations must run after CivicCore migrations and must not duplicate CivicCore-owned tables. | ADR-0003 |

## Excluded Open Questions

The CivicClerk-specific open questions from unified spec section 20 are not queued here:

- Exact CivicClerk MVP table list if reduced from the canonical table set.
- Whether CivicClerk v0.1 includes public comments.
- Whether transcription is v0.1 or v0.2.

They do not affect CivicCode v0.1.0 scope directly.
