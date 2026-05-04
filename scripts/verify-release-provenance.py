"""Verify CivicCode release tag provenance against GitHub.

This gate is intentionally network-backed: release provenance is a property of
the published GitHub ref, tag object, and target commit, not only the local
checkout.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from typing import Any


WEB_FLOW_KEY_ID = "B5690EEEBB952194"


def _gh_api(path: str) -> dict[str, Any]:
    result = subprocess.run(
        ["gh", "api", path],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def _fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def verify_release_provenance(repo: str, tag_name: str) -> None:
    ref = _gh_api(f"repos/{repo}/git/ref/tags/{tag_name}")
    tag_ref = ref["object"]
    if tag_ref["type"] != "tag":
        _fail(
            f"{tag_name} is a lightweight tag pointing at {tag_ref['type']} "
            f"{tag_ref['sha']}; create an annotated release tag instead."
        )

    tag_object = _gh_api(f"repos/{repo}/git/tags/{tag_ref['sha']}")
    target = tag_object["object"]
    if target["type"] != "commit":
        _fail(f"{tag_name} tag object points at {target['type']} {target['sha']}, not a commit.")

    commit = _gh_api(f"repos/{repo}/commits/{target['sha']}")
    verification = commit["commit"]["verification"]
    if not verification.get("verified"):
        _fail(
            f"{tag_name} target commit {target['sha']} is not GitHub-verified "
            f"(reason: {verification.get('reason')})."
        )

    signature = verification.get("signature") or ""
    if WEB_FLOW_KEY_ID not in signature and verification.get("reason") != "valid":
        _fail(
            f"{tag_name} target commit {target['sha']} does not expose the expected "
            f"GitHub web-flow verification signal."
        )

    print(
        "PASS: release provenance verified "
        f"tag={tag_name} tag_object={tag_ref['sha']} target_commit={target['sha']}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("tag_name", help="Release tag to verify, for example v0.1.17.")
    parser.add_argument(
        "--repo",
        default="CivicSuite/civiccode",
        help="GitHub repository in OWNER/REPO form.",
    )
    args = parser.parse_args()
    verify_release_provenance(args.repo, args.tag_name)


if __name__ == "__main__":
    main()
