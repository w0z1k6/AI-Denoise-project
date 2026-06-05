#!/usr/bin/env bash
# Denoise Studio — one-click start (Linux / macOS / Git Bash)
# Usage:
#   ./start-webapp.sh
#   ./start-webapp.sh --install
#   ./start-webapp.sh --stop

set -euo pipefail

WEBAPP_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEMO_ROOT="$(cd "$WEBAPP_ROOT/../../.." && pwd)"
BACKEND_DIR="$WEBAPP_ROOT/backend"
FRONTEND_DIR="$WEBAPP_ROOT/frontend"
ENV_FILE="$WEBAPP_ROOT/.env"
ENV_EXAMPLE="$WEBAPP_ROOT/.env.example"

INSTALL_DEPS=0
NO_BROWSER=0
STOP=0

for arg in "$@"; do
  case "$arg" in
    --install) INSTALL_DEPS=1 ;;
    --no-browser) NO_BROWSER=1 ;;
    --stop) STOP=1 ;;
  esac
done

load_env() {
  if [[ ! -f "$ENV_FILE" ]]; then
    cp "$ENV_EXAMPLE" "$ENV_FILE"
    echo "Created .env from .env.example"
  fi
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
}

stop_ports() {
  for port in "$@"; do
    if command -v lsof >/dev/null 2>&1; then
      pids=$(lsof -ti tcp:"$port" -sTCP:LISTEN 2>/dev/null || true)
      if [[ -n "$pids" ]]; then
        echo "Stopping port $port (PIDs: $pids)"
        kill $pids 2>/dev/null || true
      fi
    fi
  done
}

if [[ "$STOP" -eq 1 ]]; then
  stop_ports 8000 5173
  echo "Stopped listeners on 8000 / 5173 (if any)."
  exit 0
fi

echo ""
echo "=== Denoise Studio ==="
echo "Repo root : $DEMO_ROOT"
echo "Web app   : $WEBAPP_ROOT"
echo ""

command -v python >/dev/null || { echo "python not found"; exit 1; }
command -v npm >/dev/null || { echo "npm not found"; exit 1; }

load_env

export DEEPFILTER_CONDA_ENV="${DEEPFILTER_CONDA_ENV:-dfnet311}"
export APP_HOST="${APP_HOST:-0.0.0.0}"
export APP_PORT="${APP_PORT:-8000}"
export VITE_API_BASE_URL="${VITE_API_BASE_URL:-http://127.0.0.1:8000}"
export APP_DATA_DIR="${APP_DATA_DIR:-$DEMO_ROOT/analysis/denoise_selection/webapp/data}"

FRONTEND_ENV="$FRONTEND_DIR/.env.local"
if [[ ! -f "$FRONTEND_ENV" ]]; then
  printf '%s\n' "VITE_API_BASE_URL=$VITE_API_BASE_URL" > "$FRONTEND_ENV"
  echo "Created frontend/.env.local"
fi

if [[ "$INSTALL_DEPS" -eq 1 ]]; then
  python -m pip install -r "$BACKEND_DIR/requirements.txt"
  (cd "$FRONTEND_DIR" && npm install)
elif [[ ! -d "$FRONTEND_DIR/node_modules" ]]; then
  echo "node_modules missing — running npm install..."
  (cd "$FRONTEND_DIR" && npm install)
fi

stop_ports "$APP_PORT"

echo "Starting backend on port $APP_PORT ..."
(
  cd "$DEMO_ROOT"
  export DEEPFILTER_CONDA_ENV APP_HOST APP_PORT APP_DATA_DIR CORS_ORIGINS
  exec python -m uvicorn app.main:app --reload --host "$APP_HOST" --port "$APP_PORT" --app-dir "$BACKEND_DIR"
) &
BACKEND_PID=$!

sleep 2

echo "Starting frontend on http://localhost:5173 ..."
(
  cd "$FRONTEND_DIR"
  export VITE_API_BASE_URL
  exec npm run dev
) &
FRONTEND_PID=$!

if [[ "$NO_BROWSER" -eq 0 ]]; then
  sleep 2
  if command -v xdg-open >/dev/null; then
    xdg-open "http://localhost:5173" >/dev/null 2>&1 || true
  elif command -v open >/dev/null; then
    open "http://localhost:5173" >/dev/null 2>&1 || true
  fi
fi

echo ""
echo "Backend PID : $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo "  Frontend : http://localhost:5173"
echo "  Backend  : http://127.0.0.1:$APP_PORT/docs"
echo "  Stop     : kill $BACKEND_PID $FRONTEND_PID  (or ./start-webapp.sh --stop)"
echo ""
wait
