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
  "AGENTS.md"
  "USER-MANUAL.md"
  "SECURITY.md"
  "SUPPORT.md"
  "CODE_OF_CONDUCT.md"
  "docs/RECONCILIATION.md"
  "docs/MILESTONES.md"
  "docs/IMPLEMENTATION_PLAN.md"
  "docs/github-discussions-seed.md"
  "docs/index.html"
  "MILESTONE_1_DONE.md"
  "pyproject.toml"
  "civiccode/__init__.py"
  "civiccode/main.py"
  "civiccode/models.py"
  "civiccode/migrations/alembic.ini"
  "civiccode/migrations/env.py"
  "civiccode/migrations/guards.py"
  "civiccode/migrations/versions/civiccode_0001_schema.py"
)

echo "==> Required-artifact check"
for file in "${required[@]}"; do
  if [[ ! -f "$file" ]]; then
    echo "FAIL: missing required artifact: $file" >&2
    exit 1
  fi
done

echo "==> Schema-foundation truth check"
current_files=("README.md" "README.txt" "USER-MANUAL.md" "docs/index.html")
bad_markers=(
  "CivicCode is shipping"
  "Shipping v0.1.0"
  "scaffold only"
  "not installable yet"
  "code answers are available"
  "municipal code answers are available"
  "source registry is available"
  "database schema is available"
  "public lookup UI is available"
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
