#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PROJECT_DIR="$ROOT_DIR/code-smells-project"
PORT="5000"
LOG_FILE="${TMPDIR:-/tmp}/code-smells-project-validation.log"

command -v python >/dev/null || { echo "python runtime not found" >&2; exit 1; }
command -v curl >/dev/null || { echo "curl not found" >&2; exit 1; }
[[ -d "$PROJECT_DIR" ]] || { echo "project not found: $PROJECT_DIR" >&2; exit 1; }

cd "$PROJECT_DIR"
python -m compileall . >/dev/null
python app.py >"$LOG_FILE" 2>&1 &
pid=$!
trap 'kill "$pid" 2>/dev/null || true; wait "$pid" 2>/dev/null || true' EXIT

for _ in {1..30}; do
  if curl -fsS "http://127.0.0.1:$PORT/health" >/dev/null 2>&1; then
    break
  fi
  sleep 0.5
done

curl -fsS "http://127.0.0.1:$PORT/health" >/dev/null || {
  cat "$LOG_FILE" >&2
  echo "application did not become ready on port $PORT" >&2
  exit 1
}

curl -fsS "http://127.0.0.1:$PORT/" >/dev/null
curl -fsS "http://127.0.0.1:$PORT/produtos" >/dev/null

echo "code-smells-project smoke validation passed"
