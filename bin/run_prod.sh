#!/usr/bin/env bash
# Run production compose stack
# Run with ./run_prod.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASE_DIR="$(cd "$(dirname "${SCRIPT_DIR}/../.." )" && pwd )"

# Get the user and group id
MLDEVOPS_UID=$(id -u)
MLDEVOPS_GID=$(id -g)

echo MLDEVOPS_UID=$MLDEVOPS_UID >> .env
echo MLDEVOPS_GID=$MLDEVOPS_GID >> .env

# Run the production compose stack with the MLDEVOPS_UID and MLDEVOPS_GID
#GIT_VERSION="${git_hash}" COMPOSE_PROJECT_NAME=fastapi-vss docker-compose -f compose.yml up -d --build --force-recreate --runtime nvidia --gpus all --no-deps -
echo COMPOSE_PROJECT_NAME=fastapi-vss docker-compose -f compose.yml up -d --build --force-recreate --runtime nvidia --gpus all --no-deps .
