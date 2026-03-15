#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"

if [[ ! -d "$BACKEND_DIR" ]]; then
  echo "Backend directory not found: $BACKEND_DIR" >&2
  exit 1
fi

# Auto-activate backend virtualenv first (preferred), then workspace-level virtualenv.
if [[ -f "$BACKEND_DIR/.venv/bin/activate" ]]; then
  # shellcheck disable=SC1091
  source "$BACKEND_DIR/.venv/bin/activate"
elif [[ -f "$ROOT_DIR/.venv/bin/activate" ]]; then
  # shellcheck disable=SC1091
  source "$ROOT_DIR/.venv/bin/activate"
fi

cd "$BACKEND_DIR"

HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8000}"

if lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Port $PORT is already in use." >&2
  echo "Run with a different port, for example: PORT=8001 ./run-backend.sh" >&2
  echo "Or stop the existing listener:" >&2
  lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >&2
  exit 1
fi

exec uvicorn main:app --host "$HOST" --port "$PORT" --reload
