#!/usr/bin/env bash
# run_bob.sh - Launch Bob's sovereign AI responder agent
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

if [[ -d "${PROJECT_ROOT}/.venv" ]]; then
    # shellcheck source=/dev/null
    source "${PROJECT_ROOT}/.venv/bin/activate"
fi

export RELAY_HOST="${RELAY_HOST:-127.0.0.1}"
export RELAY_PORT="${RELAY_PORT:-5000}"
export OLLAMA_MODEL="${OLLAMA_MODEL:-llama3}"

echo "Starting Bob Endpoint connected to ${RELAY_HOST}:${RELAY_PORT} (Ollama model: ${OLLAMA_MODEL})..."
exec python3 "${PROJECT_ROOT}/bob_ai.py"
