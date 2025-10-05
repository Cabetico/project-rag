#!/bin/bash
set -e

# Create network if it doesn't exist
if ! docker network ls | grep -q "app-net"; then
  echo "Creating docker network app-net..."
  docker network create app-net
else
  echo "Network app-net already exists."
fi

# Build infra
docker compose -f docker-compose-infra.yaml build --no-cache      

# Start infra
docker compose -f docker-compose-infra.yaml up -d 

# Build app
docker compose -f docker-compose-app.yaml build --no-cache     

# Start app
docker compose -f docker-compose-app.yaml up -d
