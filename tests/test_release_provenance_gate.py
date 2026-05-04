from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PROVENANCE_SCRIPT = REPO_ROOT / "scripts" / "verify-release-provenance.py"
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures" / "release_provenance"


def test_adversarial_release_provenance_fixtures_are_enforced() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(PROVENANCE_SCRIPT),
            "--fixtures-dir",
            str(FIXTURES_DIR),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "FIXTURE PASS: known-good signed web-flow release tag (pass)" in result.stdout
    assert "FIXTURE PASS: lightweight tag is rejected (fail)" in result.stdout
    assert "FIXTURE PASS: annotated unsigned tag object is rejected (fail)" in result.stdout
    assert "FIXTURE PASS: signed tag pointing at unsigned commit is rejected (fail)" in result.stdout
    assert "FIXTURE PASS: signed commit from non-org identity is rejected (fail)" in result.stdout
    assert "FIXTURE PASS: mismatched committer fields are rejected (fail)" in result.stdout
    assert "FIXTURE PASS: target tree mismatch is rejected (fail)" in result.stdout
    assert "FIXTURE PASS: localhost tagger identity is rejected (fail)" in result.stdout
