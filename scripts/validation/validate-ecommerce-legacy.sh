#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PROJECT_DIR="$ROOT_DIR/ecommerce-api-legacy"
PORT="3000"
BASE_URL="http://127.0.0.1:$PORT"
TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/ecommerce-api-legacy-validation.XXXXXX")"
LOG_FILE="$TMP_DIR/application.log"
APP_PID=""

cleanup() {
    local exit_code=$?

    trap - EXIT INT TERM
    if [[ -n "$APP_PID" ]] && kill -0 "$APP_PID" 2>/dev/null; then
        kill "$APP_PID" 2>/dev/null || true
    fi
    if [[ -n "$APP_PID" ]]; then
        wait "$APP_PID" 2>/dev/null || true
    fi

    if [[ "$exit_code" -ne 0 && -f "$LOG_FILE" ]]; then
        cat "$LOG_FILE" >&2
    fi
    rmdir "$TMP_DIR" 2>/dev/null || true
    exit "$exit_code"
}
trap cleanup EXIT INT TERM

fail() {
    echo "FAIL: $*" >&2
    exit 1
}

require_command() {
    command -v "$1" >/dev/null 2>&1 || fail "required command not found: $1"
}

assert_status() {
    local label="$1"
    local actual="$2"
    local expected="$3"
    [[ "$actual" == "$expected" ]] || fail "$label: expected HTTP $expected, got $actual"
}

assert_body() {
    local label="$1"
    local body_file="$2"
    local expected="$3"
    local actual
    actual="$(<"$body_file")"
    [[ "$actual" == "$expected" ]] || fail "$label: expected body '$expected', got '$actual'"
}

assert_json_object_contract() {
    local body_file="$1"
    node -e '
        const fs = require("fs");
        const body = JSON.parse(fs.readFileSync(process.argv[1], "utf8"));
        if (body.msg !== "Sucesso" || !Number.isInteger(body.enrollment_id)) process.exit(1);
    ' "$body_file" || fail "approved checkout: expected JSON with msg=Sucesso and integer enrollment_id"
}

assert_json_array() {
    local label="$1"
    local body_file="$2"
    node -e '
        const fs = require("fs");
        const body = JSON.parse(fs.readFileSync(process.argv[1], "utf8"));
        if (!Array.isArray(body)) process.exit(1);
    ' "$body_file" || fail "$label: expected a JSON array"
}

request() {
    local method="$1"
    local path="$2"
    local body="$3"
    local output_file="$4"
    local http_code

    if ! http_code="$(curl -sS --max-time 5 \
        -X "$method" \
        "$BASE_URL$path" \
        -H 'Content-Type: application/json' \
        --data "$body" \
        -o "$output_file" \
        -w '%{http_code}')"; then
        return 1
    fi
    printf '%s' "$http_code"
}

require_command node
require_command npm
require_command curl
require_command mktemp

[[ -d "$PROJECT_DIR" ]] || fail "project not found: $PROJECT_DIR"
[[ -f "$PROJECT_DIR/package.json" ]] || fail "package.json not found in $PROJECT_DIR"

cd "$PROJECT_DIR"
if [[ -f package-lock.json ]]; then
    npm ci
else
    npm install
fi
npm ls --depth=0
node -e 'require("express"); require("sqlite3");'
echo "Dependency installation and verification passed"

npm start >"$LOG_FILE" 2>&1 &
APP_PID=$!

ready=""
ready_ok=0
for _ in {1..30}; do
    if ready="$(request GET /api/admin/financial-report '' "$TMP_DIR/readiness.body")" \
        && [[ "$ready" == "200" ]] \
        && assert_json_array "readiness" "$TMP_DIR/readiness.body"; then
        ready_ok=1
        break
    fi
    sleep 0.5
done
[[ "$ready_ok" -eq 1 ]] || fail "application did not become ready on GET /api/admin/financial-report"
echo "Readiness passed: GET /api/admin/financial-report -> 200 JSON array"

status="$(request POST /api/checkout '{}' "$TMP_DIR/checkout-missing-payload.body")"
assert_status "checkout with missing payload" "$status" "400"
assert_body "checkout with missing payload" "$TMP_DIR/checkout-missing-payload.body" "Bad Request"
echo "Legacy contract passed: POST /api/checkout with missing payload -> 400"

status="$(request POST /api/checkout \
    '{"usr":"Validation Missing Course","eml":"validation-missing-course@example.com","pwd":"pass","c_id":999,"card":"4111222233334444"}' \
    "$TMP_DIR/checkout-missing-course.body")"
assert_status "checkout with missing course" "$status" "404"
assert_body "checkout with missing course" "$TMP_DIR/checkout-missing-course.body" "Curso não encontrado"
echo "Legacy contract passed: nonexistent course -> 404"

status="$(request POST /api/checkout \
    '{"usr":"Validation Denied","eml":"validation-denied@example.com","pwd":"pass","c_id":1,"card":"5111222233334444"}' \
    "$TMP_DIR/checkout-denied.body")"
assert_status "denied payment" "$status" "400"
assert_body "denied payment" "$TMP_DIR/checkout-denied.body" "Pagamento recusado"
echo "Legacy contract passed: denied payment -> 400"

status="$(request POST /api/checkout \
    '{"usr":"Validation Approved","eml":"validation-approved@example.com","pwd":"pass","c_id":2,"card":"4111222233334444"}' \
    "$TMP_DIR/checkout-approved.body")"
assert_status "approved checkout" "$status" "200"
assert_json_object_contract "$TMP_DIR/checkout-approved.body"
echo "Legacy contract passed: approved checkout -> 200 JSON {msg,enrollment_id}"

status="$(request GET /api/admin/financial-report '' "$TMP_DIR/financial-report.body")"
assert_status "financial report" "$status" "200"
assert_json_array "financial report" "$TMP_DIR/financial-report.body"
echo "Legacy contract passed: financial report -> 200 JSON array"

status="$(request DELETE /api/users/1 '' "$TMP_DIR/delete-user.body")"
assert_status "user deletion" "$status" "200"
assert_body "user deletion" "$TMP_DIR/delete-user.body" "Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco."
echo "Legacy contract passed: DELETE /api/users/1 -> 200 legacy text"

echo "ecommerce-api-legacy validation passed"
