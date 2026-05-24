#!/usr/bin/env bash
set -euo pipefail

NO_BLOCK=false
if [[ "${1:-}" == "--noblock" ]]; then
    NO_BLOCK=true
    shift
fi

PREFECT_HOST="${PREFECT_API_HOST:-0.0.0.0}"
PREFECT_PORT="${PREFECT_SERVER_API_PORT:-4200}"
API_HOST="${API_HOST:-0.0.0.0}"
API_PORT="${API_PORT:-8002}"
PREFECT_API_URL="${PREFECT_API_URL:-http://127.0.0.1:4200/api}"

cleanup_enabled=true

cleanup() {
    if [[ "$cleanup_enabled" != "true" ]]; then
        return
    fi
    if [[ -n "${api_pid:-}" ]] && kill -0 "$api_pid" 2>/dev/null; then
        kill "$api_pid" 2>/dev/null || true
    fi
    if [[ -n "${prefect_pid:-}" ]] && kill -0 "$prefect_pid" 2>/dev/null; then
        kill "$prefect_pid" 2>/dev/null || true
    fi
    wait || true
}

trap cleanup SIGINT SIGTERM EXIT

echo "Starting Prefect server on ${PREFECT_HOST}:${PREFECT_PORT}"
if [[ "$NO_BLOCK" == "true" ]]; then
    nohup prefect server start --host "$PREFECT_HOST" --port "$PREFECT_PORT" >/tmp/prefect.log 2>&1 &
else
    prefect server start --host "$PREFECT_HOST" --port "$PREFECT_PORT" &
fi
prefect_pid=$!

for i in $(seq 1 60); do
    if curl -fsS "${PREFECT_API_URL%/}/health" >/dev/null 2>&1; then
        break
    fi
    if ! kill -0 "$prefect_pid" 2>/dev/null; then
        echo "Prefect server terminated before becoming healthy"
        exit 1
    fi
    sleep 1
    if [[ "$i" -eq 60 ]]; then
        echo "Prefect server did not become healthy within timeout"
        exit 1
    fi
done

echo "Starting API server on ${API_HOST}:${API_PORT}"
if [[ "$NO_BLOCK" == "true" ]]; then
    nohup uvicorn api:app --host "$API_HOST" --port "$API_PORT" >/tmp/api.log 2>&1 &
else
    uvicorn api:app --host "$API_HOST" --port "$API_PORT" &
fi
api_pid=$!

if [[ "$NO_BLOCK" == "true" ]]; then
    cleanup_enabled=false
    trap - EXIT
    echo "Services started in non-blocking mode"
    echo "Prefect PID: ${prefect_pid}, API PID: ${api_pid}"
    echo "Logs: /tmp/prefect.log and /tmp/api.log"
    exit 0
fi

set +e
wait -n "$prefect_pid" "$api_pid"
exit_code=$?
set -e

echo "A service exited (code ${exit_code}), stopping container"
exit "$exit_code"
