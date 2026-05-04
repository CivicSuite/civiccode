"""Verify CivicCode release tag provenance against adversarial fixtures and GitHub.

Release provenance is a pre-publication gate, not post-publication forensics.
The script can run against JSON fixtures first, then against the published
GitHub ref/tag/commit objects for a release tag.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Protocol


WEB_FLOW_KEY_ID = "B5690EEEBB952194"
ALLOWED_WEB_FLOW_COMMITTER = ("GitHub", "noreply@github.com")
ALLOWED_RELEASE_TAGGER_EMAILS = {"noreply@github.com", "web-flow@github.com"}


class ProvenanceError(RuntimeError):
    """Raised when a release provenance check fails with an auditor-facing reason."""


class ProvenanceClient(Protocol):
    def tag_ref(self, repo: str, tag_name: str) -> dict[str, Any]: ...

    def tag_object(self, repo: str, tag_sha: str) -> dict[str, Any]: ...

    def commit(self, repo: str, commit_sha: str) -> dict[str, Any]: ...


class GitHubClient:
    def _gh_api(self, path: str) -> dict[str, Any]:
        result = subprocess.run(
            ["gh", "api", path],
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(result.stdout)

    def tag_ref(self, repo: str, tag_name: str) -> dict[str, Any]:
        return self._gh_api(f"repos/{repo}/git/ref/tags/{tag_name}")

    def tag_object(self, repo: str, tag_sha: str) -> dict[str, Any]:
        return self._gh_api(f"repos/{repo}/git/tags/{tag_sha}")

    def commit(self, repo: str, commit_sha: str) -> dict[str, Any]:
        return self._gh_api(f"repos/{repo}/commits/{commit_sha}")


class FixtureClient:
    def __init__(self, fixture: dict[str, Any]) -> None:
        self.fixture = fixture
        self.responses = fixture["responses"]

    def tag_ref(self, repo: str, tag_name: str) -> dict[str, Any]:
        return self.responses["ref"]

    def tag_object(self, repo: str, tag_sha: str) -> dict[str, Any]:
        return self.responses["tag"]

    def commit(self, repo: str, commit_sha: str) -> dict[str, Any]:
        return self.responses["commit"]


def _verification_reason(payload: dict[str, Any]) -> str:
    return str(payload.get("verification", {}).get("reason") or "missing")


def _require_verified(payload: dict[str, Any], label: str) -> None:
    verification = payload.get("verification") or {}
    if not verification.get("verified"):
        raise ProvenanceError(
            f"{label} is not GitHub-verified (reason: {_verification_reason(payload)})."
        )
    if verification.get("reason") != "valid":
        raise ProvenanceError(
            f"{label} verification reason is {verification.get('reason')!r}, expected 'valid'."
        )


def _require_web_flow_committer(commit: dict[str, Any], tag_name: str) -> None:
    committer = commit.get("commit", {}).get("committer") or {}
    actual = (committer.get("name"), committer.get("email"))
    if actual != ALLOWED_WEB_FLOW_COMMITTER:
        raise ProvenanceError(
            f"{tag_name} target commit committer is {actual[0]} <{actual[1]}>, "
            "expected GitHub <noreply@github.com> for the current web-flow release model."
        )


def _require_release_tagger(tag_object: dict[str, Any], tag_name: str) -> None:
    tagger = tag_object.get("tagger") or {}
    email = tagger.get("email")
    if email not in ALLOWED_RELEASE_TAGGER_EMAILS:
        raise ProvenanceError(
            f"{tag_name} release tagger email is {email!r}; expected a GitHub/org-associated "
            "release identity, not a maintainer-local identity."
        )


def _require_expected_tree(commit: dict[str, Any], expected_tree: str | None, tag_name: str) -> None:
    if not expected_tree:
        return
    tree_sha = commit.get("commit", {}).get("tree", {}).get("sha")
    if tree_sha != expected_tree:
        raise ProvenanceError(
            f"{tag_name} target tree {tree_sha} does not match expected release tree "
            f"{expected_tree}; rebuild from the verified target commit before publishing."
        )


def verify_release_provenance(
    client: ProvenanceClient,
    repo: str,
    tag_name: str,
    *,
    expected_target: str | None = None,
    expected_tree: str | None = None,
) -> tuple[str, str]:
    ref = client.tag_ref(repo, tag_name)
    tag_ref = ref["object"]
    if tag_ref["type"] != "tag":
        raise ProvenanceError(
            f"{tag_name} is a lightweight tag pointing at {tag_ref['type']} "
            f"{tag_ref['sha']}; create a signed annotated release tag instead."
        )

    tag_object = client.tag_object(repo, tag_ref["sha"])
    _require_verified(tag_object, f"{tag_name} tag object {tag_ref['sha']}")
    _require_release_tagger(tag_object, tag_name)

    target = tag_object["object"]
    if target["type"] != "commit":
        raise ProvenanceError(
            f"{tag_name} tag object points at {target['type']} {target['sha']}, not a commit."
        )
    if expected_target and target["sha"] != expected_target:
        raise ProvenanceError(
            f"{tag_name} tag target {target['sha']} does not match expected target "
            f"{expected_target}."
        )

    commit = client.commit(repo, target["sha"])
    _require_verified(commit["commit"], f"{tag_name} target commit {target['sha']}")
    _require_web_flow_committer(commit, tag_name)
    _require_expected_tree(commit, expected_tree, tag_name)

    return tag_ref["sha"], target["sha"]


def _load_fixtures(fixtures_dir: Path) -> list[dict[str, Any]]:
    fixtures = []
    for path in sorted(fixtures_dir.glob("*.json")):
        with path.open(encoding="utf-8") as handle:
            fixture = json.load(handle)
        fixture["_path"] = str(path)
        fixtures.append(fixture)
    if not fixtures:
        raise ProvenanceError(f"No provenance fixtures found in {fixtures_dir}.")
    return fixtures


def run_fixtures(fixtures_dir: Path, repo: str) -> None:
    failures = []
    for fixture in _load_fixtures(fixtures_dir):
        tag_name = fixture.get("tag_name", "vfixture")
        expected = fixture["expected"]
        expected_error = fixture.get("expected_error", "")
        try:
            verify_release_provenance(
                FixtureClient(fixture),
                repo,
                tag_name,
                expected_target=fixture.get("expected_target"),
                expected_tree=fixture.get("expected_tree"),
            )
            actual = "pass"
            error = ""
        except ProvenanceError as exc:
            actual = "fail"
            error = str(exc)

        if actual != expected:
            failures.append(
                f"{fixture['_path']}: expected {expected}, got {actual}. Error: {error}"
            )
            continue
        if expected == "fail" and expected_error not in error:
            failures.append(
                f"{fixture['_path']}: failure did not include expected message "
                f"{expected_error!r}. Actual: {error}"
            )
            continue
        print(f"FIXTURE PASS: {fixture['name']} ({actual})")

    if failures:
        raise ProvenanceError("\n".join(failures))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("tag_name", nargs="?", help="Release tag to verify, for example v0.1.17.")
    parser.add_argument(
        "--repo",
        default="CivicSuite/civiccode",
        help="GitHub repository in OWNER/REPO form.",
    )
    parser.add_argument(
        "--fixtures-dir",
        type=Path,
        help="Run the adversarial fixture suite before checking a live tag.",
    )
    parser.add_argument(
        "--expected-tree",
        help="Expected target commit tree SHA for pre-publication artifact builds.",
    )
    parser.add_argument(
        "--expected-target",
        help="Expected target commit SHA for pre-publication release gating.",
    )
    args = parser.parse_args()

    try:
        if args.fixtures_dir:
            run_fixtures(args.fixtures_dir, args.repo)
        if args.tag_name:
            tag_sha, target_sha = verify_release_provenance(
                GitHubClient(),
                args.repo,
                args.tag_name,
                expected_target=args.expected_target,
                expected_tree=args.expected_tree,
            )
            print(
                "PASS: release provenance verified "
                f"tag={args.tag_name} tag_object={tag_sha} target_commit={target_sha}"
            )
    except ProvenanceError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
