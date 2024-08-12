#!/usr/bin/env bash
# Run production compose stack
# Run with ./run_prod.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASE_DIR="$(cd "$(dirname "${SCRIPT_DIR}/../.." )" && pwd )"

# Get the short version of the hash of the commit
git_hash=$(git log -1 --format=%h)

# Run the production compose stack
GIT_VERSION="${git_hash}"

# Run the production compose stack with the MLDEVOPS_UID and MLDEVOPS_GID
GIT_VERSION="${git_hash}" COMPOSE_PROJECT_NAME=fastapi-vss docker-compose -f ${BASE_DIR}/docker/compose.yml up -d --build --force-recreate --runtime nvidia --gpus all --no-deps .
