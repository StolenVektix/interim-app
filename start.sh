#!/usr/bin/env bash
# Démarre le backend (FastAPI) et le frontend (Vite) en local.
# Usage : ./start.sh   puis ouvrir http://localhost:5173
# Arrêt : ./stop.sh

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
BACKEND_LOG="$ROOT_DIR/backend.log"
FRONTEND_LOG="$ROOT_DIR/frontend.log"
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"

if lsof -i ":$BACKEND_PORT" -sTCP:LISTEN -t >/dev/null 2>&1; then
  echo "Le port $BACKEND_PORT est déjà occupé (backend déjà démarré ?). Lance ./stop.sh d'abord si besoin."
  exit 1
fi
if lsof -i ":$FRONTEND_PORT" -sTCP:LISTEN -t >/dev/null 2>&1; then
  echo "Le port $FRONTEND_PORT est déjà occupé (frontend déjà démarré ?). Lance ./stop.sh d'abord si besoin."
  exit 1
fi

# --- Backend ---
if [ ! -x "$BACKEND_DIR/.venv/bin/python" ]; then
  echo "Création de l'environnement virtuel backend..."
  python3 -m venv "$BACKEND_DIR/.venv" --without-pip
  curl -sS https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py
  "$BACKEND_DIR/.venv/bin/python" /tmp/get-pip.py -q
fi

echo "Installation des dépendances backend (si nécessaire)..."
"$BACKEND_DIR/.venv/bin/pip" install -q -r "$BACKEND_DIR/requirements.txt"

echo "Démarrage du backend sur http://localhost:$BACKEND_PORT ..."
(
  cd "$BACKEND_DIR"
  nohup ./.venv/bin/uvicorn app.main:app --port "$BACKEND_PORT" > "$BACKEND_LOG" 2>&1 &
)

# --- Frontend ---
if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
  echo "Installation des dépendances frontend..."
  (cd "$FRONTEND_DIR" && npm install --no-fund --no-audit)
fi

echo "Démarrage du frontend sur http://localhost:$FRONTEND_PORT ..."
(
  cd "$FRONTEND_DIR"
  nohup npm run dev -- --port "$FRONTEND_PORT" > "$FRONTEND_LOG" 2>&1 &
)

sleep 2
echo ""
echo "Backend  : http://localhost:$BACKEND_PORT (docs interactives : /docs)"
echo "Frontend : http://localhost:$FRONTEND_PORT"
echo "Logs     : $BACKEND_LOG / $FRONTEND_LOG"
echo "Pour arrêter : ./stop.sh"
