#!/usr/bin/env just --justfile

set dotenv-required

# Source the .env file
set dotenv-load := true

# List recipes
list:
    @just --list --unsorted

# Setup the environment for development
install: setup-env
    #!/usr/bin/env bash
    conda env create -f environment.yml
    conda activate fastapi-vss
    python -m pip install https://github.com/redis/redis-py/archive/refs/tags/v5.0.9.zip

# Setup the environment for development
setup-env:
    #!/usr/bin/env bash
    CONFIG_DIR=$(pwd)/config

    cat > .env <<EOF
    REDIS_PASSWD=xvN2ErdyY4
    LOG_LEVEL=INFO
    GIT_VERSION=latest
    CONFIG_PATH=$CONFIG_DIR
    EOF

    mkdir -p logs

# Update the conda development environment. Run this command after checking out any code changes
update:
    #!/usr/bin/env bash
    conda env update --file environment.yml --prune
    conda activate fastapi-vss
    python -m pip install https://github.com/redis/redis-py/archive/refs/tags/v5.0.9.zip

# Kill existing uvicorn processes
kill-uvicorn:
    #!/usr/bin/env bash
    if pgrep -f "uvicorn main:app"; then
      pkill -f "uvicorn main:app"
    fi

# Run the FastAPI server locally in development mode
run-server: kill-uvicorn
    #!/usr/bin/env bash
    echo "FastAPI server running at http://localhost:8000"
    echo "FastAPI docs running at http://localhost:8000/docs"
    conda activate fastapi-vss
    export PYTHONPATH=$PWD/src
    cd src/app &&
    uvicorn main:app --port 8000 --reload

# Test the github action with act
run-act:
    act -P ubuntu-latest=catthehacker/ubuntu:act-latest -j test --container-architecture linux/amd64

# Run the FastAPI server in development mode with Docker Compose
run-server-dev: setup-env
    #!/usr/bin/env bash
    tag=$(git describe --tags --always)
    GIT_VERSION=$tag COMPOSE_PROJECT_NAME=fastapi-vss docker-compose -f compose.dev.yml down && \
    GIT_VERSION=$tag COMPOSE_PROJECT_NAME=fastapi-vss docker-compose -f compose.dev.yml up -d

#  Stop the FastAPI server in development mode with Docker Compose
stop-server-dev:
    #!/usr/bin/env bash
    tag=$(git describe --tags --always)
    GIT_VERSION=$tag COMPOSE_PROJECT_NAME=fastapi-vss docker-compose -f compose.dev.yml down

run-server-prod: setup-env
    #!/usr/bin/env bash
    tag=$(git describe --tags --always)
    GIT_VERSION=$tag COMPOSE_PROJECT_NAME=fastapi-vss docker-compose -f compose.yml down --remove-orphans && \
    GIT_VERSION=$tag COMPOSE_PROJECT_NAME=fastapi-vss docker-compose -f compose.yml up -d

#  Stop the FastAPI server in development mode with Docker Compose
stop-server-prod:
    #!/usr/bin/env bash
    tag=$(git describe --tags --always)
    GIT_VERSION=$tag COMPOSE_PROJECT_NAME=fastapi-vss docker-compose -f compose.yml down

# Build the Docker image without CUDA support for development
build-docker:
    #!/usr/bin/env bash
    tag=$(git describe --tags --always)
    docker build -t mbari/fastapi-vss:$tag -f Dockerfile .

# Build the CUDA Docker image for development
build-docker-cuda:
    #!/usr/bin/env bash
    tag=$(git describe --tags --always)
    docker build -t mbari/fastapi-vss:$tag -f Dockerfile.cuda .

# Build the docker images for linux/amd64 and push to Docker Hub
build-and-push:
    #!/usr/bin/env bash
    echo "Building and pushing the Docker image"
    RELEASE_VERSION=$(git describe --tags --abbrev=0)
    echo "Release version: $RELEASE_VERSION"
    RELEASE_VERSION=${RELEASE_VERSION:1}
    docker buildx create --name mybuilder --platform linux/amd64 --use
    docker buildx build --sbom=true --provenance=true --push --platform linux/amd64  -t mbari/fastapi-vss:$RELEASE_VERSION-cuda124 --build-arg IMAGE_URI=mbari/fastapi-vss:$RELEASE_VERSION -f Dockerfile.cuda .

# Default recipe
default:
    just run-server-dev

# Quick test to fetch all IDs from the test project
test_all_ids:
    #!/usr/bin/env bash
    curl -X 'GET' \
      'http://localhost:8000/ids/testproject' \
      -H 'accept: application/json' \
      -d ''

# Quick test to fetch all IDs from the test project
process_atolla:
    #!/usr/bin/env bash
    cd ./tests/images/atolla

    echo "Processing Atolla images..."
    response=$(curl -s -X 'POST' \
      'http://localhost:8000/knn/3/testproject' \
      -H 'accept: application/json' \
      -H 'Content-Type: multipart/form-data' \
      -F 'files=@atolla1.png;type=image/png' \
      -F 'files=@atolla2.png;type=image/png')

    id=$(echo "$response" | sed -n 's/.*"job_id":"\([^"]*\)".*/\1/p')
    echo "Job ID extracted: $id"

    if [[ -z "$id" ]]; then
      echo "Failed to extract job ID from response: $response"
      exit 1
    fi
process_copepods:
    #!/usr/bin/env bash
    cd ./tests/images/copepod
    curl -X 'POST' \
     'http:/localhost:8000/knn/3/testproject' \
     -H 'accept: application/json' \
     -H 'Content-Type: multipart/form-data' \
     -F 'files=@copepod1.png;type=image/png'
    curl -X 'POST' \
     'http:/localhost:8000/knn/3/testproject' \
     -H 'accept: application/json' \
     -H 'Content-Type: multipart/form-data' \
     -F 'files=@copepod2.png;type=image/png'
    curl -X 'POST' \
     'http:/localhost:8000/knn/3/testproject' \
     -H 'accept: application/json' \
     -H 'Content-Type: multipart/form-data' \
     -F 'files=@copepod3.png;type=image/png'
