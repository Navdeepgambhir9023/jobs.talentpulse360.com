#!/usr/bin/env bash
set -euo pipefail
echo "Starting jobs-service..."
if [ -d "../tp360-shared" ]; then
    pip install -e ../tp360-shared --quiet
fi
pip install -r requirements.txt --quiet
exec uvicorn app.main:app \
    --host "${SERVICE_HOST:-0.0.0.0}" \
    --port "${SERVICE_PORT:-8005}" \
    --reload \
    --log-level "${LOG_LEVEL:-info}"
