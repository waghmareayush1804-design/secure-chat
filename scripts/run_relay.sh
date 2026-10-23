#!/usr/bin/env bash
# run_relay.sh - Start the Project Armadillo Zero-Knowledge TCP Relay Server
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Activate virtualenv if present
if [[ -d "${PROJECT_ROOT}/.venv" ]]; then
    # shellcheck source=/dev/null
    source "${PROJECT_ROOT}/.venv/bin/activate"
fi

export RELAY_HOST="${RELAY_HOST:-127.0.0.1}"
export RELAY_PORT="${RELAY_PORT:-5000}"

echo "Starting Zero-Knowledge Blind Relay on ${RELAY_HOST}:${RELAY_PORT}..."
exec python3 "${PROJECT_ROOT}/server.py"
