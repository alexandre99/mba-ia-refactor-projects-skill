#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PROJECT_DIR="$ROOT_DIR/ecommerce-api-legacy"
PORT="${PORT:-3000}"
BASE_URL="http://127.0.0.1:$PORT"
TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/ecommerce-api-legacy-validation.XXXXXX")"
LOG_FILE="$TMP_DIR/application.log"
VALIDATION_ADMIN_TOKEN="validation-admin-token"
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
    local admin_token="${5:-}"
    local http_code
    local -a auth_header=()

    if [[ -n "$admin_token" ]]; then
        auth_header=(-H "X-Admin-Token: $admin_token")
    fi

    if ! http_code="$(curl -sS --max-time 5 \
        -X "$method" \
        "$BASE_URL$path" \
        -H 'Content-Type: application/json' \
        "${auth_header[@]}" \
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

for configured_database_path in "" ":memory:"; do
    if DATABASE_PATH="$configured_database_path" NODE_ENV=production node -e 'require("./src/config")' >/dev/null 2>&1; then
        fail "production configuration accepted non-durable DATABASE_PATH='$configured_database_path'"
    fi
done
echo "Production storage guard passed"

ADMIN_TOKEN="$VALIDATION_ADMIN_TOKEN" PORT="$PORT" npm start >"$LOG_FILE" 2>&1 &
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

status="$(request DELETE /api/users/1 '' "$TMP_DIR/delete-user-unauthorized.body")"
assert_status "unauthorized user deletion" "$status" "401"
assert_body "unauthorized user deletion" "$TMP_DIR/delete-user-unauthorized.body" "Unauthorized"
echo "Security contract passed: DELETE /api/users/1 without token -> 401"

status="$(request DELETE /api/users/1 '' "$TMP_DIR/delete-user.body" "$VALIDATION_ADMIN_TOKEN")"
assert_status "authorized user deletion" "$status" "200"
assert_body "authorized user deletion" "$TMP_DIR/delete-user.body" "Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco."
echo "Legacy contract passed: authorized DELETE /api/users/1 -> 200 legacy text"

node <<'NODE'
const assert = require('node:assert/strict');
const SqliteDatabase = require('./src/infrastructure/database');
const initializeDatabase = require('./src/infrastructure/initializeDatabase');
const CourseRepository = require('./src/repositories/courseRepository');
const UserRepository = require('./src/repositories/userRepository');
const CheckoutRepository = require('./src/repositories/checkoutRepository');
const CheckoutService = require('./src/services/checkoutService');
const CheckoutController = require('./src/controllers/checkoutController');

async function count(db, table) {
    const row = await db.get(`SELECT COUNT(*) AS count FROM ${table}`);
    return row.count;
}

async function run() {
    const db = new SqliteDatabase(':memory:');
    try {
        const checkoutSource = require('node:fs').readFileSync('./src/services/checkoutService.js', 'utf8');
        assert.equal(checkoutSource.includes("startsWith('4')"), false);
        assert.equal(checkoutSource.includes("'last_checkout_'"), false);
        await initializeDatabase(db);
        const cache = new Map();
        const checkoutRepository = new CheckoutRepository(db);
        const originalAudit = checkoutRepository.recordAudit.bind(checkoutRepository);
        checkoutRepository.recordAudit = async () => {
            throw new Error('injected failure after payment');
        };
        const service = new CheckoutService({
            courseRepository: new CourseRepository(db),
            userRepository: new UserRepository(db),
            checkoutRepository,
            cache,
            transaction: db.transaction.bind(db)
        });

        await assert.rejects(
            service.execute({
                name: 'Rollback User',
                email: 'rollback@example.com',
                password: 'pass',
                courseId: 2,
                card: '4111222233334444'
            }),
            /injected failure after payment/
        );
        assert.equal(await count(db, 'users'), 1);
        assert.equal(await count(db, 'enrollments'), 1);
        assert.equal(await count(db, 'payments'), 1);
        assert.equal(await count(db, 'audit_logs'), 0);
        assert.equal(cache.size, 0);

        checkoutRepository.recordAudit = originalAudit;
        const result = await service.execute({
            name: 'Committed User',
            email: 'committed@example.com',
            password: 'pass',
            courseId: 2,
            card: '4111222233334444'
        });
        assert.equal(result.msg, 'Sucesso');
        assert.equal(await count(db, 'users'), 2);
        assert.equal(await count(db, 'enrollments'), 2);
        assert.equal(await count(db, 'payments'), 2);
        assert.equal(await count(db, 'audit_logs'), 1);
        const committedUser = await db.get('SELECT id FROM users WHERE email = ?', ['committed@example.com']);
        assert.equal(cache.get(`last_checkout_${committedUser.id}`), 'Docker');

        const controller = new CheckoutController({
            execute: async () => { throw new Error('injected SQL detail'); }
        });
        let statusCode;
        let body;
        const response = {
            status(code) { statusCode = code; return this; },
            send(value) { body = value; return this; },
            json(value) { body = value; return this; }
        };
        const originalConsoleError = console.error;
        console.error = () => {};
        try {
            await controller.create({ body: { usr: 'Error', eml: 'error@example.com', pwd: 'pass', c_id: 2, card: '4' } }, response);
        } finally {
            console.error = originalConsoleError;
        }
        assert.equal(statusCode, 500);
        assert.equal(body, 'Erro interno');
    } finally {
        await db.close();
    }
}

run().catch(error => {
    console.error(error);
    process.exit(1);
});
NODE
echo "Finding-specific validation passed: transaction rollback, post-commit cache, and generic error mapping"

echo "ecommerce-api-legacy validation passed"
