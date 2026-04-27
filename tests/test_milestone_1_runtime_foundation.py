from __future__ import annotations

import importlib
import importlib.util
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient


ROOT = Path(__file__).resolve().parents[1]


def load_pyproject() -> dict:
    pyproject = ROOT / "pyproject.toml"
    assert pyproject.exists(), "pyproject.toml must exist for CivicCode runtime foundation."
    return tomllib.loads(pyproject.read_text(encoding="utf-8"))


def load_app_module():
    try:
        spec = importlib.util.find_spec("civiccode.main")
    except ModuleNotFoundError:
        spec = None
    assert spec is not None, "civiccode.main must be importable."
    return importlib.import_module("civiccode.main")


def test_pyproject_declares_runtime_package_and_dev_version() -> None:
    data = load_pyproject()

    assert data["project"]["name"] == "civiccode"
    assert data["project"]["version"] == "0.1.0.dev0"
    assert "CivicCode" in data["project"]["description"]


def test_pyproject_pins_civiccore_exactly_to_released_v020() -> None:
    data = load_pyproject()
    dependencies = data["project"]["dependencies"]

    assert "civiccore==0.2.0" in dependencies
    assert not any("civiccore>=" in dep or "civiccore~=" in dep for dep in dependencies)


def test_pyproject_declares_foundation_runtime_and_test_dependencies() -> None:
    data = load_pyproject()
    dependencies = "\n".join(data["project"]["dependencies"])
    dev_dependencies = "\n".join(data["project"]["optional-dependencies"]["dev"])

    assert "fastapi" in dependencies
    assert "uvicorn" in dependencies
    assert "pytest" in dev_dependencies
    assert "httpx" in dev_dependencies
    assert "ruff" in dev_dependencies


def test_runtime_package_layout_exists() -> None:
    expected_paths = [
        ROOT / "civiccode" / "__init__.py",
        ROOT / "civiccode" / "main.py",
    ]

    for path in expected_paths:
        assert path.exists(), f"Missing runtime foundation file: {path.relative_to(ROOT)}"


def test_public_fastapi_app_import_path_exists() -> None:
    module = load_app_module()
    assert isinstance(module.app, FastAPI)
    assert module.app.title == "CivicCode"


@pytest.mark.asyncio
async def test_root_endpoint_explains_current_user_experience() -> None:
    module = load_app_module()
    async with AsyncClient(
        transport=ASGITransport(app=module.app),
        base_url="http://testserver",
    ) as client:
        response = await client.get("/")

    assert response.status_code == 200
    payload = response.json()
    assert payload["name"] == "CivicCode"
    assert payload["status"] == "staff workbench foundation"
    assert payload["code_answer_behavior"] == "citation_grounded"
    assert payload["api_base"] == "/api/v1/civiccode"
    assert payload["future_public_path"] == "/civiccode"
    assert payload["next_step"] == "Milestone 9: plain-language summaries"
    assert "not implemented yet" in payload["message"].lower()
    assert "source registry" in payload["message"]
    assert "citations" in payload["message"]
    assert "Q&A" in payload["message"]
    assert "Staff" in payload["message"]
    assert "live LLM" in payload["message"]
    assert "public lookup" in payload["message"]


@pytest.mark.asyncio
async def test_health_endpoint_is_actionable_for_it_staff() -> None:
    module = load_app_module()
    async with AsyncClient(
        transport=ASGITransport(app=module.app),
        base_url="http://testserver",
    ) as client:
        response = await client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload == {
        "status": "ok",
        "service": "civiccode",
        "version": "0.1.0.dev0",
        "civiccore": "0.2.0",
    }


def test_ci_runs_pytest_docs_and_placeholder_gates() -> None:
    workflow = ROOT / ".github" / "workflows" / "verify.yml"
    text = workflow.read_text(encoding="utf-8")

    assert "python -m pytest" in text
    assert "bash scripts/verify-docs.sh" in text
    assert "python scripts/check-civiccore-placeholder-imports.py" in text


def test_placeholder_import_gate_passes_for_runtime_source() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check-civiccore-placeholder-imports.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "PLACEHOLDER-IMPORT-CHECK: PASSED" in result.stdout


def test_current_facing_docs_describe_runtime_foundation_honestly() -> None:
    docs = {
        "README.md": (ROOT / "README.md").read_text(encoding="utf-8"),
        "README.txt": (ROOT / "README.txt").read_text(encoding="utf-8"),
        "USER-MANUAL.md": (ROOT / "USER-MANUAL.md").read_text(encoding="utf-8"),
        "docs/index.html": (ROOT / "docs" / "index.html").read_text(encoding="utf-8"),
    }

    for path, text in docs.items():
        lowered = text.lower()
        assert "runtime foundation" in lowered, f"{path} must mention runtime foundation."
        assert "scaffold only" not in lowered, f"{path} must not retain scaffold-only wording."
        assert "not installable yet" not in lowered, f"{path} must not retain pre-runtime wording."
        assert "code-answer behavior" in lowered or "code answers" in lowered

    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "runtime foundation" in changelog.lower()
