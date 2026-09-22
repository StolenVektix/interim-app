#!/usr/bin/env bash
# Arrête le backend et le frontend démarrés par start.sh.

set -uo pipefail

BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"

stop_port() {
  local port="$1"
  local label="$2"
  local pids
  pids=$(lsof -i ":$port" -sTCP:LISTEN -t 2>/dev/null || true)
  if [ -z "$pids" ]; then
    echo "$label : rien n'écoute sur le port $port."
    return
  fi
  echo "$label : arrêt du/des processus sur le port $port ($pids)..."
  kill $pids 2>/dev/null || true
  sleep 1
  # Si un process traîne encore (ex: vite lancé via npm run dev), on force.
  pids=$(lsof -i ":$port" -sTCP:LISTEN -t 2>/dev/null || true)
  if [ -n "$pids" ]; then
    kill -9 $pids 2>/dev/null || true
  fi
}

stop_port "$BACKEND_PORT" "Backend"
stop_port "$FRONTEND_PORT" "Frontend"

# Filet de sécurité pour les processus enfants (npm -> vite) qui n'écoutent pas
# forcément directement le port au moment du kill ci-dessus.
pkill -f "uvicorn app.main:app" 2>/dev/null || true
pkill -f "vite --port $FRONTEND_PORT" 2>/dev/null || true

echo "Arrêt terminé."
