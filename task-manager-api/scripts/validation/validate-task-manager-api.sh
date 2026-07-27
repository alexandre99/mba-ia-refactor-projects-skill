#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
PORT="${PORT:-5000}"
BASE_URL="http://127.0.0.1:${PORT}"
TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/task-manager-api-validation.XXXXXX")"
WORK_DIR="${TMP_DIR}/project"
LOG_FILE="${TMP_DIR}/application.log"
APP_PID=""

cleanup() {
    local exit_code=$?
    trap - EXIT INT TERM

    if [[ -n "${APP_PID}" ]] && kill -0 "${APP_PID}" 2>/dev/null; then
        kill -- "-${APP_PID}" 2>/dev/null || kill "${APP_PID}" 2>/dev/null || true
    fi
    if [[ -n "${APP_PID}" ]]; then
        wait "${APP_PID}" 2>/dev/null || true
    fi

    if [[ "${exit_code}" -ne 0 && -f "${LOG_FILE}" ]]; then
        cat "${LOG_FILE}" >&2
    fi

    rm -rf "${TMP_DIR}"
    if [[ "${exit_code}" -eq 0 ]]; then
        echo "CLEANUP: temporary project, database, log, and process removed"
    fi
    exit "${exit_code}"
}
trap cleanup EXIT INT TERM

require_command() {
    command -v "$1" >/dev/null 2>&1 || {
        echo "required command not found: $1" >&2
        exit 1
    }
}

require_command "${PYTHON_BIN}"
require_command curl
require_command mktemp
require_command setsid

[[ "${PORT}" == "5000" ]] || {
    echo "this application hardcodes port 5000; use PORT=5000" >&2
    exit 1
}

"${PYTHON_BIN}" -c 'import flask, flask_sqlalchemy, flask_cors, requests'
PYTHONPYCACHEPREFIX="${TMP_DIR}/pycache" "${PYTHON_BIN}" -m compileall -q "${PROJECT_DIR}"
echo "RUNTIME: ${PYTHON_BIN}"
echo "COMPILE: passed"

mkdir -p "${WORK_DIR}"
cp -a "${PROJECT_DIR}/app.py" "${PROJECT_DIR}/database.py" "${PROJECT_DIR}/seed.py" \
    "${PROJECT_DIR}/models" "${PROJECT_DIR}/routes" "${PROJECT_DIR}/services" \
    "${PROJECT_DIR}/utils" "${WORK_DIR}/"

(
    cd "${WORK_DIR}"
    PYTHONPYCACHEPREFIX="${TMP_DIR}/pycache" "${PYTHON_BIN}" seed.py
)
echo "SEED: passed in isolated temporary database"

(
    cd "${WORK_DIR}"
    setsid "${PYTHON_BIN}" app.py >"${LOG_FILE}" 2>&1 &
    echo "$!" >"${TMP_DIR}/app.pid"
)
APP_PID="$(<"${TMP_DIR}/app.pid")"

ready=0
for _ in {1..30}; do
    status="$(curl -sS --max-time 2 -o "${TMP_DIR}/health.json" -w '%{http_code}' "${BASE_URL}/health" || true)"
    if [[ "${status}" == "200" ]]; then
        ready=1
        break
    fi
    sleep 0.5
done
[[ "${ready}" -eq 1 ]] || {
    echo "BOOT: failed to become ready on ${BASE_URL}/health" >&2
    exit 1
}
echo "BOOT: python app.py -> ready on ${BASE_URL}"

"${PYTHON_BIN}" - "${BASE_URL}" <<'PY'
import json
import sys

import requests

base_url = sys.argv[1]
failures = []


def shape(value):
    if isinstance(value, dict):
        return {"type": "object", "keys": sorted(value)}
    if isinstance(value, list):
        item_keys = sorted(value[0]) if value and isinstance(value[0], dict) else []
        return {"type": "array", "length": len(value), "item_keys": item_keys}
    return {"type": type(value).__name__}


def request(label, method, path, expected_status, payload=None):
    response = requests.request(
        method,
        base_url + path,
        json=payload,
        timeout=5,
    )
    try:
        body = response.json()
    except ValueError:
        body = response.text
    print(
        f"ENDPOINT: {method} {path} -> {response.status_code}; "
        f"shape={json.dumps(shape(body), sort_keys=True)}"
    )
    if response.status_code != expected_status:
        failures.append(
            f"{label}: expected {expected_status}, got {response.status_code}"
        )
    return body


request("health", "GET", "/health", 200)
request("index", "GET", "/", 200)
request("list users", "GET", "/users", 200)
request("missing user", "GET", "/users/999", 404)

created_user = request(
    "create user",
    "POST",
    "/users",
    201,
    {
        "name": "Validation User",
        "email": "validation-user@example.com",
        "password": "pass1234",
        "role": "user",
    },
)
user_id = created_user["id"]
request("get user", "GET", f"/users/{user_id}", 200)
request(
    "update user",
    "PUT",
    f"/users/{user_id}",
    200,
    {"name": "Validation User Updated"},
)
request("user tasks", "GET", f"/users/{user_id}/tasks", 200)
request(
    "valid login",
    "POST",
    "/login",
    200,
    {"email": "joao@email.com", "password": "1234"},
)
request(
    "invalid login",
    "POST",
    "/login",
    401,
    {"email": "joao@email.com", "password": "wrong"},
)

created_category = request(
    "create category",
    "POST",
    "/categories",
    201,
    {"name": "Validation Category", "description": "Baseline", "color": "#123456"},
)
category_id = created_category["id"]
request("list categories", "GET", "/categories", 200)
request(
    "update category",
    "PUT",
    f"/categories/{category_id}",
    200,
    {"description": "Baseline updated"},
)

request("list tasks", "GET", "/tasks", 200)
request("missing task", "GET", "/tasks/999", 404)
created_task = request(
    "create task",
    "POST",
    "/tasks",
    201,
    {
        "title": "Validation Task",
        "description": "Task created by baseline",
        "priority": 2,
        "user_id": user_id,
        "category_id": category_id,
        "tags": ["baseline", "smoke"],
    },
)
task_id = created_task["id"]
request("get task", "GET", f"/tasks/{task_id}", 200)
request(
    "update task",
    "PUT",
    f"/tasks/{task_id}",
    200,
    {"status": "done", "priority": 1},
)
request("search tasks", "GET", "/tasks/search?q=Validation", 200)
request("task stats", "GET", "/tasks/stats", 200)
request("summary report", "GET", "/reports/summary", 200)
request("user report", "GET", "/reports/user/1", 200)
request("missing user report", "GET", "/reports/user/999", 404)

request("delete task", "DELETE", f"/tasks/{task_id}", 200)
request("delete category", "DELETE", f"/categories/{category_id}", 200)
request("delete user", "DELETE", f"/users/{user_id}", 200)

if failures:
    raise SystemExit("; ".join(failures))
PY

echo "ENDPOINTS: all baseline probes passed"
