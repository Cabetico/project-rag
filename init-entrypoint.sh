#!/bin/bash
set -e

# === Wait for Qdrant ===
echo "=== [Init] Waiting for Qdrant to be ready... ==="
until curl -sSf http://qdrant:6333/collections >/dev/null 2>&1; do
  sleep 1
done
echo "✅ Qdrant is up!"

# === Wait for Postgres ===
echo "=== [Init] Waiting for Postgres to be ready... ==="
until pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" >/dev/null 2>&1; do
  sleep 1
done
echo "✅ Postgres is up!"

# === Initialize Database ===
echo "=== [Init] Running init_db()... ==="
uv run python - <<'PY'
from e_commerce_rag.db import init_db
init_db()
PY

# === Load Qdrant Index ===
echo "=== [Init] Running load_index()... ==="
uv run python - <<'PY'
from e_commerce_rag.ingest import load_index
load_index()
PY

echo "✅ Initialization completed!"