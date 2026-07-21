#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PROJECT_DIR="$ROOT_DIR/code-smells-project"
PYTHON_BIN="${PYTHON_BIN:-python}"
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-5000}"
BASE_URL="http://${HOST}:${PORT}"
LOG_FILE="${LOG_FILE:-${TMPDIR:-/tmp}/code-smells-project-validation.log}"
TEMP_DATABASE=0
if [[ -z "${DATABASE_PATH:-}" ]]; then
    DATABASE_PATH="$(mktemp "${TMPDIR:-/tmp}/code-smells-project-db.XXXXXX")"
    TEMP_DATABASE=1
fi
SERVER_PID=""

cleanup() {
    if [[ -n "$SERVER_PID" ]]; then
        kill "$SERVER_PID" 2>/dev/null || true
        wait "$SERVER_PID" 2>/dev/null || true
    fi
    if [[ "$TEMP_DATABASE" -eq 1 ]]; then
        rm -f "$DATABASE_PATH"
    fi
}
trap cleanup EXIT

command -v "$PYTHON_BIN" >/dev/null || { echo "python runtime not found: $PYTHON_BIN" >&2; exit 1; }
command -v curl >/dev/null || { echo "curl not found" >&2; exit 1; }
[[ -d "$PROJECT_DIR" ]] || { echo "project not found: $PROJECT_DIR" >&2; exit 1; }

cd "$PROJECT_DIR"
"$PYTHON_BIN" -m compileall -q .

env DATABASE_PATH="$DATABASE_PATH" HOST="$HOST" PORT="$PORT" FLASK_DEBUG=0 \
    "$PYTHON_BIN" app.py >"$LOG_FILE" 2>&1 &
SERVER_PID=$!

ready=0
for _ in {1..30}; do
    if curl -fsS "$BASE_URL/health" >/dev/null 2>&1; then
        ready=1
        break
    fi
    sleep 0.2
done

if [[ "$ready" -ne 1 ]]; then
    cat "$LOG_FILE" >&2
    echo "application did not become ready on $BASE_URL" >&2
    exit 1
fi

curl -fsS "$BASE_URL/health" >/dev/null
curl -fsS "$BASE_URL/" >/dev/null
curl -fsS "$BASE_URL/produtos" >/dev/null
curl -fsS -X POST "$BASE_URL/admin/query" \
    -H 'Content-Type: application/json' \
    --data '{"sql":"SELECT COUNT(*) AS total FROM produtos"}' >/dev/null

echo "code-smells-project smoke validation passed"
