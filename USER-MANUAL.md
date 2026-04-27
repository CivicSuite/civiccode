# CivicCode User Manual

CivicCode is not installable yet. This manual explains the planned product and
the current scaffold state.

## For municipal decision-makers

CivicCode is planned to make municipal code easier to search, cite, and
explain. It will not replace the city's official codifier and will not provide
legal advice. The goal is to help residents and staff find exact code sections
and understand next steps.

Current truth:

- no runtime application exists,
- no database schema exists,
- no frontend exists,
- no LLM answers are generated,
- planning and ADR work are next.

## For IT and technical staff

This repo currently contains documentation and verification gates only. Runtime
implementation must follow the CivicSuite pattern:

- standalone module repo under `CivicSuite/`,
- civiccore dependency once runtime begins,
- local LLM only through `civiccore.llm`,
- no cloud dependency,
- no imports from unreleased CivicCore placeholder packages.

## Architecture reference

Planned dependency direction:

```text
civicsuite docs/governance
        |
        v
civiccore shared platform
        |
        v
civiccode municipal-code module
        |
        v
future consumers: civiczone, civiclegal, civicaccess, civiccomms
```

The first runtime design must be reconciled against the upstream unified spec
before code lands.
