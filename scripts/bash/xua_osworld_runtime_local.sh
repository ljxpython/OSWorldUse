#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OSWORLD_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

XUAEVAL_HOME="${XUAEVAL_HOME:-/Users/bytedance/PycharmProjects/work/xua-eval}"
RUNTIME_PROJECT="${XUAEVAL_HOME}/runtimes/osworld"
XUA_LOCAL_E2E_DIR="${XUA_LOCAL_E2E_DIR:-/tmp/xua-osworld-e2e-local}"
PID_DIR="${XUA_LOCAL_E2E_DIR}/pids"
LOG_DIR="${XUA_LOCAL_E2E_DIR}/logs"
PID_FILE="${OSWORLD_RUNTIME_PID_FILE:-${PID_DIR}/osworld-runtime.pid}"
LOG_FILE="${OSWORLD_RUNTIME_LOG_FILE:-${LOG_DIR}/osworld-runtime.log}"
PORT="${OSWORLD_RUNTIME_PORT:-7001}"
HOST="${OSWORLD_RUNTIME_HOST:-127.0.0.1}"
RUNTIME_STATE_DB="${OSWORLD_RUNTIME_STATE_DB:-${XUA_LOCAL_E2E_DIR}/runtime.sqlite}"
RUNTIME_RESULT_ROOT="${OSWORLD_RUNTIME_RESULT_ROOT:-${XUA_LOCAL_E2E_DIR}/runtime-results}"
RUNTIME_BOOTSTRAP_ROOT="${OSWORLD_RUNTIME_BOOTSTRAP_ROOT:-${XUA_LOCAL_E2E_DIR}/bootstrap}"

usage() {
  cat <<'EOF'
Usage:
  bash scripts/bash/xua_osworld_runtime_local.sh start
  bash scripts/bash/xua_osworld_runtime_local.sh stop
  bash scripts/bash/xua_osworld_runtime_local.sh restart
  bash scripts/bash/xua_osworld_runtime_local.sh reset
  bash scripts/bash/xua_osworld_runtime_local.sh status
  bash scripts/bash/xua_osworld_runtime_local.sh logs

Environment overrides:
  XUAEVAL_HOME=/path/to/xua-eval
  XUA_LOCAL_E2E_DIR=/tmp/xua-osworld-e2e-local
  OSWORLD_RUNTIME_PORT=7001
EOF
}

assert_safe_reset_dir() {
  local dir="$1"

  if [[ -z "${dir}" || "${dir}" == "/" ]]; then
    echo "[xua-runtime] unsafe reset directory: ${dir}" >&2
    exit 1
  fi
  if [[ "${dir}" != /* ]]; then
    echo "[xua-runtime] reset directory must be absolute: ${dir}" >&2
    exit 1
  fi
  if [[ "${dir}" == *".."* ]]; then
    echo "[xua-runtime] reset directory must not contain '..': ${dir}" >&2
    exit 1
  fi

  case "${dir}" in
    /tmp/xua-*|/private/tmp/xua-*)
      return 0
      ;;
  esac

  if [[ "${XUA_LOCAL_E2E_ALLOW_RESET_NON_TMP:-0}" == "1" ]]; then
    return 0
  fi

  echo "[xua-runtime] refusing to reset non-/tmp local state directory: ${dir}" >&2
  echo "[xua-runtime] set XUA_LOCAL_E2E_ALLOW_RESET_NON_TMP=1 only if this is intentional" >&2
  exit 1
}

remove_runtime_path() {
  local path="$1"
  local label="$2"

  if [[ -z "${path}" ]]; then
    return 0
  fi
  if [[ "${path}" == "${XUA_LOCAL_E2E_DIR}" ]]; then
    echo "[xua-runtime] skip ${label}; refusing to delete full state directory: ${path}"
    return 0
  fi

  case "${path}" in
    "${XUA_LOCAL_E2E_DIR}/"*)
      echo "[xua-runtime] deleting ${label}: ${path}"
      rm -rf "${path}"
      ;;
    *)
      echo "[xua-runtime] skip ${label}; path is outside XUA_LOCAL_E2E_DIR: ${path}"
      ;;
  esac
}

running_pid() {
  if [[ -f "${PID_FILE}" ]]; then
    local pid
    pid="$(cat "${PID_FILE}")"
    if [[ -n "${pid}" ]] && kill -0 "${pid}" 2>/dev/null; then
      echo "${pid}"
      return 0
    fi
  fi
  return 1
}

port_pids() {
  if command -v lsof >/dev/null 2>&1; then
    lsof -tiTCP:"${PORT}" -sTCP:LISTEN 2>/dev/null || true
  fi
}

wait_for_http() {
  local url="$1"
  local seconds="${2:-60}"
  for _ in $(seq 1 "${seconds}"); do
    if curl -fsS "${url}" >/dev/null 2>&1; then
      return 0
    fi
    if [[ -f "${PID_FILE}" ]] && ! kill -0 "$(cat "${PID_FILE}")" 2>/dev/null; then
      return 1
    fi
    sleep 1
  done
  return 1
}

start_runtime() {
  if [[ ! -d "${RUNTIME_PROJECT}" ]]; then
    echo "[xua-runtime] missing runtime project: ${RUNTIME_PROJECT}" >&2
    echo "[xua-runtime] set XUAEVAL_HOME=/path/to/xua-eval and retry" >&2
    exit 1
  fi

  local existing_pid
  if existing_pid="$(running_pid)"; then
    echo "[xua-runtime] already running pid=${existing_pid}"
    return 0
  fi

  mkdir -p "${PID_DIR}" "${LOG_DIR}" \
    "${RUNTIME_RESULT_ROOT}" \
    "${RUNTIME_BOOTSTRAP_ROOT}"

  (
    set -euo pipefail
    if [[ "${OSWORLD_SOURCE_ENV:-1}" == "1" && -f "${OSWORLD_ROOT}/.env" ]]; then
      set -a
      # shellcheck source=/dev/null
      source "${OSWORLD_ROOT}/.env"
      set +a
    fi

    export OSWORLD_HOME="${OSWORLD_HOME:-${OSWORLD_ROOT}}"
    export OSWORLD_RUNTIME_HOST="${OSWORLD_RUNTIME_HOST:-${HOST}}"
    export OSWORLD_RUNTIME_PORT="${OSWORLD_RUNTIME_PORT:-${PORT}}"
    export OSWORLD_RUNTIME_PUBLIC_BASE_URL="${OSWORLD_RUNTIME_PUBLIC_BASE_URL:-http://127.0.0.1:${OSWORLD_RUNTIME_PORT}/v1}"
    export OSWORLD_RUNTIME_INSTANCE_ID="${OSWORLD_RUNTIME_INSTANCE_ID:-osworld-runtime-local-e2e}"
    export OSWORLD_RESOURCE_PROFILE_ID="${OSWORLD_RESOURCE_PROFILE_ID:-osworld-volcengine-e2e}"
    export OSWORLD_RUNTIME_MAX_CONCURRENCY="${OSWORLD_RUNTIME_MAX_CONCURRENCY:-1}"
    export OSWORLD_RUNTIME_STATE_DB="${RUNTIME_STATE_DB}"
    export OSWORLD_RUNTIME_RESULT_ROOT="${RUNTIME_RESULT_ROOT}"
    export OSWORLD_RUNTIME_BOOTSTRAP_ROOT="${RUNTIME_BOOTSTRAP_ROOT}"
    export OSWORLD_RUNTIME_EXECUTION_BACKEND="${OSWORLD_RUNTIME_EXECUTION_BACKEND:-subprocess}"

    cd "${OSWORLD_ROOT}"
    if command -v rtk >/dev/null 2>&1; then
      exec rtk uv run --project "${RUNTIME_PROJECT}" xua-osworld-runtime
    fi
    exec uv run --project "${RUNTIME_PROJECT}" xua-osworld-runtime
  ) >>"${LOG_FILE}" 2>&1 &

  local pid="$!"
  echo "${pid}" > "${PID_FILE}"
  echo "[xua-runtime] started pid=${pid}"
  echo "[xua-runtime] log=${LOG_FILE}"

  if wait_for_http "http://127.0.0.1:${PORT}/v1/health" 60; then
    echo "[xua-runtime] healthy: http://127.0.0.1:${PORT}/v1/health"
  else
    echo "[xua-runtime] start did not become healthy; tail log:" >&2
    tail -n 80 "${LOG_FILE}" >&2 || true
    exit 1
  fi
}

stop_pid() {
  local pid="$1"
  local label="$2"

  if [[ -z "${pid}" ]]; then
    return 0
  fi
  if ! kill -0 "${pid}" 2>/dev/null; then
    echo "[xua-runtime] stale ${label} pid=${pid}"
    return 0
  fi

  local command
  command="$(ps -p "${pid}" -o command= 2>/dev/null || true)"
  echo "[xua-runtime] stopping ${label} pid=${pid} command=${command}"
  kill -TERM "${pid}" 2>/dev/null || true

  for _ in $(seq 1 20); do
    if ! kill -0 "${pid}" 2>/dev/null; then
      echo "[xua-runtime] stopped pid=${pid}"
      return 0
    fi
    sleep 0.5
  done

  echo "[xua-runtime] pid=${pid} did not exit after TERM; sending KILL"
  kill -KILL "${pid}" 2>/dev/null || true
}

stop_runtime() {
  if [[ -f "${PID_FILE}" ]]; then
    stop_pid "$(cat "${PID_FILE}")" "pid-file"
    rm -f "${PID_FILE}"
  fi

  while IFS= read -r pid; do
    stop_pid "${pid}" "port-${PORT}"
  done < <(port_pids)

  echo "[xua-runtime] stopped"
}

reset_runtime() {
  assert_safe_reset_dir "${XUA_LOCAL_E2E_DIR}"
  stop_runtime
  echo "[xua-runtime] resetting Runtime local state under: ${XUA_LOCAL_E2E_DIR}"
  remove_runtime_path "${RUNTIME_STATE_DB}" "state db"
  remove_runtime_path "${RUNTIME_RESULT_ROOT}" "result root"
  remove_runtime_path "${RUNTIME_BOOTSTRAP_ROOT}" "bootstrap root"
  remove_runtime_path "${PID_FILE}" "pid file"
  remove_runtime_path "${LOG_FILE}" "log file"
  mkdir -p "${PID_DIR}" "${LOG_DIR}" "${RUNTIME_RESULT_ROOT}" "${RUNTIME_BOOTSTRAP_ROOT}"
  echo "[xua-runtime] reset complete"
}

status_runtime() {
  local pid=""
  pid="$(running_pid || true)"
  if [[ -n "${pid}" ]]; then
    echo "[xua-runtime] pid-file running pid=${pid}"
  else
    echo "[xua-runtime] pid-file not running"
  fi

  local listeners
  listeners="$(port_pids | tr '\n' ' ' | sed 's/[[:space:]]*$//')"
  if [[ -n "${listeners}" ]]; then
    echo "[xua-runtime] port ${PORT} listener pid(s): ${listeners}"
  else
    echo "[xua-runtime] port ${PORT} has no listener"
  fi

  if curl -fsS "http://127.0.0.1:${PORT}/v1/health" >/dev/null 2>&1; then
    echo "[xua-runtime] health ok: http://127.0.0.1:${PORT}/v1/health"
  else
    echo "[xua-runtime] health failed"
  fi
}

case "${1:-}" in
  start)
    start_runtime
    ;;
  stop)
    stop_runtime
    ;;
  restart)
    stop_runtime
    start_runtime
    ;;
  reset)
    reset_runtime
    ;;
  status)
    status_runtime
    ;;
  logs)
    mkdir -p "${LOG_DIR}"
    touch "${LOG_FILE}"
    tail -f "${LOG_FILE}"
    ;;
  "" | -h | --help | help)
    usage
    ;;
  *)
    usage >&2
    exit 2
    ;;
esac
