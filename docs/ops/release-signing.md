# Release Signing and Provenance

CivicCode releases must not depend on a secret signing key on one maintainer's
workstation. The release identity must be real, published, and associated with
the CivicSuite organization or GitHub's documented web-flow signing identity.
Do not use `scott@localhost` or any other placeholder identity for release
commits, taggers, or signing keys.

## Current v0.1.x Signing Model

The current CivicCode v0.1.x release line uses GitHub web-flow verification for
release commits. The acceptable dev-process release shape is:

1. Merge the release PR through GitHub, not by pushing a local unsigned commit
   directly to `main`.
2. Verify the target commit through the GitHub commit API or release page before
   publishing assets.
3. Create an annotated release tag that points at that GitHub-verified commit.
4. Run `python scripts/verify-release-provenance.py vX.Y.Z` after publication.
5. Stop if the tag is lightweight or the target commit is not verified.

The current gate enforces two properties: the release ref must be an annotated
tag object, and the tag must point at a GitHub-verified target commit. Prior
v0.1.7-v0.1.16 releases used this web-flow-style provenance at the commit layer;
some earlier annotated tag objects were not independently signed. That is
acceptable only for the v0.1.x developer process and must be replaced before the
procurement-grade evidence pack closes.

## GitHub Web-Flow Verification Check

Use this command to verify a published release tag:

```bash
python scripts/verify-release-provenance.py v0.1.17
```

The script reads the remote GitHub tag ref, rejects lightweight tags, resolves
the annotated tag object to its target commit, and checks GitHub's commit
verification API. A passing result means the published tag is not merely a local
unsigned ref and its target commit is GitHub-verified.

## Long-Term Sigstore Requirement

The long-term release path is a GitHub Actions release workflow that signs
release artifacts with Sigstore/cosign using the workflow OIDC identity. That
workflow must sign at least:

- the wheel,
- the source distribution,
- the checksum manifest,
- the release provenance statement.

The release notes must include the exact clean-machine verification command so
an outside auditor can verify provenance without trusting a maintainer laptop or
preloaded local keyring.

This should land as its own hardening slice, either `civiccode v0.1.18:
release provenance hardening` or as a civiccore-level extraction that
CivicClerk and CivicRecords-AI inherit. By Milestone H, every suite release tag
and artifact must be independently verifiable against a documented signing
identity with no local-secret-key dependency.

## v0.1.17 Post-Incident Note

During the first v0.1.17 publication attempt, `gh release create --target
f3e54e89a53857adf7ac1ec4d4a7f44f705e5598` created a release with a lightweight
tag pointing directly at a locally authored, unsigned commit. The release notes
also claimed GitHub web-flow signing, which was false for that artifact.

The bad release and tag were deleted before suite synchronization. The
correction is to land this runbook and the provenance gate through a
GitHub-verified merge commit, verify that target commit, and recreate v0.1.17
with an audit trail in the release notes. The new gate prevents the same
lightweight-tag/unsigned-target failure from being silently accepted during
future release publication.
