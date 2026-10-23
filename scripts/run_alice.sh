#!/usr/bin/env bash
# run_alice.sh - Launch the Streamlit frontend for Alice's client
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

if [[ -d "${PROJECT_ROOT}/.venv" ]]; then
    # shellcheck source=/dev/null
    source "${PROJECT_ROOT}/.venv/bin/activate"
fi

export RELAY_HOST="${RELAY_HOST:-127.0.0.1}"
export RELAY_PORT="${RELAY_PORT:-5000}"
STREAMLIT_PORT="${STREAMLIT_PORT:-8501}"

echo "Launching Project Armadillo Streamlit Frontend (Alice) on http://localhost:${STREAMLIT_PORT}..."
exec streamlit run "${PROJECT_ROOT}/Home.py" --server.port "${STREAMLIT_PORT}" --server.headless false
