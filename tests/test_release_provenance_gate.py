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
    assert "FIXTURE PASS: known-good Sigstore attested release (pass)" in result.stdout
    assert "FIXTURE PASS: missing attestation schema is rejected (fail)" in result.stdout
    assert "FIXTURE PASS: wrong workflow identity is rejected (fail)" in result.stdout
    assert "FIXTURE PASS: mismatched artifact hash is rejected (fail)" in result.stdout
    assert "FIXTURE PASS: unexpected OIDC issuer is rejected (fail)" in result.stdout
    assert "FIXTURE PASS: transparency log outage fails closed (fail)" in result.stdout
    assert "FIXTURE PASS: attestation target mismatch is rejected (fail)" in result.stdout
    assert "FIXTURE PASS: workflow rename identity drift is rejected (fail)" in result.stdout
    assert "FIXTURE PASS: trust-root rotation fails closed (fail)" in result.stdout
