#!/usr/bin/env bash
# Run production compose stack
# Run with ./run_prod.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASE_DIR="$(cd "$(dirname "${SCRIPT_DIR}/../.." )" && pwd )"

# Export the environment variables in the .env file
export $(grep -v '^#' $BASE_DIR/.env |  xargs)

# Get the short version of the hash of the commit
git_hash=$(git log -1 --format=%h)

# Run the production compose stack
GIT_VERSION="${git_hash}" COMPOSE_PROJECT_NAME=fastapi-tator docker-compose -f compose.yml up -d
