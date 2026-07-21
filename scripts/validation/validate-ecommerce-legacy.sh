#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PROJECT_DIR="$ROOT_DIR/ecommerce-api-legacy"
PORT="3000"
LOG_FILE="${TMPDIR:-/tmp}/ecommerce-api-legacy-validation.log"

command -v node >/dev/null || { echo "node runtime not found" >&2; exit 1; }
command -v npm >/dev/null || { echo "npm not found" >&2; exit 1; }
command -v curl >/dev/null || { echo "curl not found" >&2; exit 1; }
[[ -d "$PROJECT_DIR" ]] || { echo "project not found: $PROJECT_DIR" >&2; exit 1; }

cd "$PROJECT_DIR"
if [[ -f package-lock.json ]]; then npm ci; else npm install; fi

npm start >"$LOG_FILE" 2>&1 &
pid=$!
trap 'kill "$pid" 2>/dev/null || true; wait "$pid" 2>/dev/null || true' EXIT

for _ in {1..30}; do
  if curl -fsS "http://127.0.0.1:$PORT/" >/dev/null 2>&1; then break; fi
  sleep 0.5
done

if ! curl -fsS "http://127.0.0.1:$PORT/" >/dev/null 2>&1; then
  cat "$LOG_FILE" >&2
  echo "application did not become ready on port $PORT" >&2
  exit 1
fi

echo "ecommerce-api-legacy boot validation passed; endpoint inventory still pending"
