#!/bin/sh
set -e

echo "=== SentinelX AI Backend Container Startup ==="

# Create runtime directories if they do not exist
mkdir -p "${MODEL_DIR:-/app/models}" "${DATASETS_DIR:-/app/datasets}" "${REPORTS_DIR:-/app/reports}" "${LOGS_DIR:-/app/logs}"

# Execute Alembic Database Migrations
echo "[Entrypoint] Executing database migrations (alembic upgrade head)..."
if alembic upgrade head; then
    echo "[Entrypoint] Database migrations applied successfully."
else
    echo "[Entrypoint] WARNING: Database migration step encountered an issue or database is uninitialized."
fi

echo "[Entrypoint] Launching application server: $@"
exec "$@"
