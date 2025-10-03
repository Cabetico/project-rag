#!/bin/bash
set -e

# Create network if it doesn't exist
if ! docker network ls | grep -q "app-net"; then
  echo "Creating docker network app-net..."
  docker network create app-net
else
  echo "Network app-net already exists."
fi

# Start infra
docker compose -f docker-compose-infra.yaml up -d

# Start app
docker compose -f docker-compose-app.yaml up -d