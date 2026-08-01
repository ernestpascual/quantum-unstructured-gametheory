#!/bin/bash
set -e

# Default environment variables
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"

echo "🚀 Starting Quantum Game Theory App (FastAPI + Gradio)..."
echo "📍 Server listening on http://${HOST}:${PORT}"
echo "  - Gradio UI: http://${HOST}:${PORT}/"
echo "  - API Docs:  http://${HOST}:${PORT}/docs"

# Run Uvicorn server
exec uvicorn app.main:app --host "$HOST" --port "$PORT" --reload
