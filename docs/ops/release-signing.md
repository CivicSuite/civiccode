# Release Signing and Provenance

CivicCode releases must not depend on a secret signing key on one maintainer's
workstation. The release identity must be real, published, and associated with
the CivicSuite organization or GitHub's documented web-flow signing identity.
Do not use `scott@localhost` or any other placeholder identity for release
commits, taggers, or signing keys.

Release provenance is a pre-flight gate, not post-publication forensics. A
failing gate produces no release assets. There is no dev-process exemption, no
localhost identity exception, and no "fix it in the next release" path.

## Current v0.1.x Signing Model

The current CivicCode v0.1.x release line uses GitHub web-flow verification for
release commits and release tag objects. The acceptable dev-process release
shape is:

1. Merge the release PR through GitHub, not by pushing a local unsigned commit
   directly to `main`.
2. Verify the target commit through the GitHub commit API before creating any
   public release artifact.
3. Create a GitHub-verified annotated release tag object that points at that
   GitHub-verified commit.
4. Run the adversarial fixture suite before checking the real tag:

   ```bash
   python scripts/verify-release-provenance.py --fixtures-dir tests/fixtures/release_provenance
   ```

5. Run the live provenance gate before publishing release assets:

   ```bash
   python scripts/verify-release-provenance.py vX.Y.Z \
     --expected-target <verified-target-commit-sha> \
     --expected-tree <verified-release-tree-sha>
   ```

6. Publish the GitHub Release and assets only after the pre-flight gate passes.
7. Run the post-publication provenance workflow as a secondary check.

The gate enforces that the release ref is not lightweight, the annotated tag
object is GitHub-verified, the tagger is a GitHub/org-associated release
identity, the tag target is the expected commit, the target commit is
GitHub-verified, the target committer is the GitHub web-flow identity, and the
target tree matches the verified release build.

## Adversarial Fixture Suite

The canonical fixture suite lives in
`tests/fixtures/release_provenance/`. The gate must reject every failure fixture
with a specific auditor-facing error and accept the known-good fixture.

Current fixtures:

- `00_known_good_web_flow_signed.json`: known-good signed web-flow release tag.
- `10_lightweight_tag.json`: rejects lightweight tags.
- `20_annotated_unsigned_tag.json`: rejects annotated-but-unsigned tag objects.
- `30_signed_tag_unsigned_commit.json`: rejects signed tags pointing at unsigned commits.
- `40_unassociated_commit_identity.json`: rejects commits signed by a non-org release identity.
- `50_mismatched_committer_fields.json`: rejects mismatched commit committer fields.
- `60_tree_mismatch_local_state.json`: rejects a release tree that differs from the verified build tree.
- `70_localhost_tagger_identity.json`: rejects localhost/local maintainer tagger identities.

New production defect classes must be added here before any destructive
correction is requested.

## Known Failure Modes

### Lightweight Tag to Unsigned Commit

Discovered: `v0.1.17` first-publication attempt, 2026-05-04.

Prior gate miss: the release was created before provenance verification, and
`gh release create --target <sha>` created a lightweight tag pointing directly
at a locally authored unsigned commit.

Fixture: `10_lightweight_tag.json`.

Expected error: `is a lightweight tag`.

### Annotated but Unsigned Tag Object

Discovered: `v0.1.18` first-publication attempt, 2026-05-04.

Prior gate miss: the v0.1.17 correction gate checked that the ref was an
annotated tag and that the target commit was GitHub-verified, but it did not
require the annotated tag object itself to be GitHub-verified. The same blind
spot allowed v0.1.17 and v0.1.18 to appear acceptable even though both tag
objects were unsigned.

Fixture: `20_annotated_unsigned_tag.json`.

Expected error: `tag object <sha> is not GitHub-verified`.

## Live Defect Statement: v0.1.18

Current public artifact: `v0.1.18`

Defect an outside auditor can verify:

- GitHub tag ref `refs/tags/v0.1.18` points at annotated tag object
  `d82660282fa48193fd437f033c28bec687fb380c`.
- That tag object targets commit
  `e061d262e1fc78875e72c28a809dd07a00f7b798`.
- The target commit is GitHub-verified.
- The tag object itself is not GitHub-verified:
  `verification.verified=false`, `verification.reason=unsigned`.
- Therefore v0.1.18 fails the corrected release provenance bar.

Reproducer:

```bash
python scripts/verify-release-provenance.py v0.1.18
```

Expected output:

```text
FAIL: v0.1.18 tag object d82660282fa48193fd437f033c28bec687fb380c is not GitHub-verified (reason: unsigned).
```

Corrected-artifact proof before destructive action:

```bash
python scripts/verify-release-provenance.py --fixtures-dir tests/fixtures/release_provenance
```

The known-good fixture passes and the annotated-unsigned fixture fails with the
same defect class as the live v0.1.18 artifact.

Defect-discovery latency: v0.1.18 was published at `2026-05-04T17:11:13Z`.
The swarm detected the unsigned tag-object defect in the same release session,
before requesting any destructive correction. Treat this as a class defect, not
a one-off.

## Two-Release Correction Window: v0.1.17

Current public artifact: `v0.1.17`

The corrected gate also fails v0.1.17:

```bash
python scripts/verify-release-provenance.py v0.1.17
```

Expected output:

```text
FAIL: v0.1.17 tag object 31d9d18ed4931cf462732b6fd91f2937cc80d792 is not GitHub-verified (reason: unsigned).
```

Because v0.1.17 and v0.1.18 fail the same corrected gate, any future
destructive correction must handle both releases in one coordinated correction
window after explicit chat authorization.

## v0.1.17 Post-Incident Note

During the first v0.1.17 publication attempt, `gh release create --target
f3e54e89a53857adf7ac1ec4d4a7f44f705e5598` created a release with a lightweight
tag pointing directly at a locally authored, unsigned commit. The release notes
also claimed GitHub web-flow signing, which was false for that artifact.

The bad release and tag were deleted before suite synchronization. The
correction landed an initial runbook and provenance gate through a
GitHub-verified merge commit, verified the target commit, and recreated
v0.1.17 with an audit trail in the release notes.

Follow-up finding: that correction prevented the lightweight-tag/unsigned-target
failure but did not require a verified tag object, which caused the second
incident class documented above.

## v0.1.18 Post-Incident Note

During the first v0.1.18 publication attempt, the release was created against an
existing annotated tag object. The target commit was GitHub-verified, but the
tag object was locally created and unsigned. The post-publication workflow
queued only after the public release existed, so the defect was detected after
publication rather than prevented before publication.

No destructive correction has been performed. The current release and tag are
held in place until the corrected gate, fixture suite, pre-publication workflow,
and backfill verification are landed and reviewed.

Defect-discovery latency: same release session, under five minutes from
publication to self-detection.

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

By Milestone H, every suite release tag and artifact must be independently
verifiable against a documented signing identity with no local-secret-key
dependency.
