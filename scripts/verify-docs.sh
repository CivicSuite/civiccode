#!/usr/bin/env bash
set -euo pipefail

required=(
  "README.md"
  "README.txt"
  "CHANGELOG.md"
  "CONTRIBUTING.md"
  "LICENSE"
  "LICENSE-CODE"
  "LICENSE-DOCS"
  ".gitignore"
  ".dockerignore"
  "AGENTS.md"
  "USER-MANUAL.md"
  "SECURITY.md"
  "SUPPORT.md"
  "CODE_OF_CONDUCT.md"
  "docs/RECONCILIATION.md"
  "docs/MILESTONES.md"
  "docs/IMPLEMENTATION_PLAN.md"
  "docs/github-discussions-seed.md"
  "scripts/verify-release.sh"
  "Dockerfile"
  "docker-compose.yml"
  "docker.env.example"
  "scripts/docker-demo-smoke.sh"
  "docs/index.html"
  "MILESTONE_1_DONE.md"
  "MILESTONE_3_DONE.md"
  "MILESTONE_4_DONE.md"
  "MILESTONE_5_DONE.md"
  "MILESTONE_6_DONE.md"
  "MILESTONE_7_DONE.md"
  "MILESTONE_8_DONE.md"
  "MILESTONE_9_DONE.md"
  "MILESTONE_10_DONE.md"
  "MILESTONE_11_DONE.md"
  "MILESTONE_12_DONE.md"
  "MILESTONE_13_DONE.md"
  "MILESTONE_14_DONE.md"
  "pyproject.toml"
  "civiccode/__init__.py"
  "civiccode/main.py"
  "civiccode/citation_contract.py"
  "civiccode/qa_harness.py"
  "civiccode/plain_language.py"
  "civiccode/ordinance_handoff.py"
  "civiccode/import_connectors.py"
  "civiccode/public_exports.py"
  "civiccode/public_lookup.py"
  "civiccode/staff_workbench.py"
  "civiccode/source_registry.py"
  "civiccode/section_lifecycle.py"
  "civiccode/models.py"
  "civiccode/migrations/alembic.ini"
  "civiccode/migrations/env.py"
  "civiccode/migrations/guards.py"
  "civiccode/migrations/versions/civiccode_0001_schema.py"
  "tests/fixtures/milestone_12/csv_bundle.json"
  "tests/fixtures/milestone_12/official_html_extract.json"
  "tests/fixtures/milestone_12/broken_missing_section.json"
)

echo "==> Required-artifact check"
for file in "${required[@]}"; do
  if [[ ! -f "$file" ]]; then
    echo "FAIL: missing required artifact: $file" >&2
    exit 1
  fi
done

echo "==> Current-facing shipped/planned truth check"
current_files=("README.md" "README.txt" "USER-MANUAL.md" "docs/index.html")
bad_markers=(
  "CivicCode is shipping"
  "Shipping v0.1.0"
  "scaffold only"
  "not installable yet"
  "code answers are available"
  "municipal code answers are available"
  "uncited answers are available"
  "legal advice is available"
  "live LLM calls are enabled"
  "public lookup UI is available"
  "staff notes are public"
  "public staff-note visibility"
  "plain-language summaries are law"
  "summaries provide legal advice"
  "pending ordinance language is adopted law"
  "automatic ordinance codification is available"
)

for file in "${current_files[@]}"; do
  for marker in "${bad_markers[@]}"; do
    if grep -Fqi "$marker" "$file"; then
      echo "FAIL: stale/planned-as-shipped marker '$marker' found in $file" >&2
      exit 1
    fi
  done
done

echo "PASS"
