#!/bin/bash
set -e

# === Wait for Qdrant ===
echo "=== [Entrypoint] Waiting for Qdrant to be ready... ==="
until curl -sSf http://qdrant:6333/collections >/dev/null 2>&1; do
  sleep 0.5
done
echo "✅ Qdrant is up!"

# === Wait for Postgres ===
echo "=== [Entrypoint] Waiting for Postgres to be ready... ==="
until pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" >/dev/null 2>&1; do
  sleep 1
done
echo "✅ Postgres is up!"

# === Start Gunicorn ===
echo "=== [Entrypoint] Starting Gunicorn... ==="

# === Start Gunicorn ===
echo "=== [Entrypoint] Starting Gunicorn... ==="
exec uv run gunicorn -w 4 -b 0.0.0.0:8000 e_commerce_rag.app:app