#!/usr/bin/env bash
# run_tests.sh - Run test suite with unittest or pytest
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

if [[ -d "${PROJECT_ROOT}/.venv" ]]; then
    # shellcheck source=/dev/null
    source "${PROJECT_ROOT}/.venv/bin/activate"
fi

if command -v pytest >/dev/null 2>&1; then
    echo "Running tests with pytest..."
    exec pytest -v "${PROJECT_ROOT}/tests"
else
    echo "Running tests with standard library unittest..."
    exec python3 -m unittest discover -s "${PROJECT_ROOT}/tests" -p "test_*.py" -v
fi
