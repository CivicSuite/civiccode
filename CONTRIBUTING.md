# Contributing to CivicCode

CivicCode is currently in scaffold and Milestone 0 planning. Contributions
should improve documentation, clarify ADR questions, or strengthen verification
gates. Runtime code starts only after Milestone 0 is reviewed.

## Before opening a PR

Run:

```bash
bash scripts/verify-docs.sh
```

If a future runtime adds tests or release gates, this file must be updated in
the same PR.

## Scope rules

- Do not promote planned CivicCode behavior as shipped.
- Do not add runtime application code before Milestone 1 is opened.
- Do not import from unreleased CivicCore placeholder packages.
- Do not change suite-wide compatibility docs from this repo; open a PR in
  `CivicSuite/civicsuite` instead.
