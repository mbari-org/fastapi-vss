#!/usr/bin/env just --justfile

set dotenv-required

# Source the .env file
set dotenv-load := true

# List recipes
list:
    @just --list --unsorted

# Setup the environment
install:
    conda env create -f environment.yml
    python -m pip install --upgrade pip
    git submodule update --init --recursive
    python -m pip install -r src/submodules/requirements.txt
    python -m pip install https://github.com/redis/redis-py/archive/refs/tags/v5.0.9.zip

# Update the conda environment. Run this command after checking out any code changes
update:
    git submodule update --init --recursive
    conda env update --file environment.yml --prune
    python -m pip install -r src/submodules/aidata/requirements.txt

# Kill existing uvicorn processes
kill-uvicorn:
    #!/usr/bin/env bash
    if pgrep -f "uvicorn main:app"; then
      pkill -f "uvicorn main:app"
    fi

# Run the FastAPI server
run-server: kill-uvicorn
    #!/usr/bin/env bash
    echo "FastAPI server running at http://localhost:8002"
    echo "FastAPI docs running at http://localhost:8002/docs"
    export PYTHONPATH=$PWD/src
    cd src/app && conda run -n fastapi-vss --no-capture-output uvicorn main:app --port 8002 --reload

run-server-prod:
    gitver=$(git describe --tags --always)
    GIT_VERSION=$gitver COMPOSE_PROJECT_NAME=fastapi-vss \
    docker-compose -f compose.yml up -d \
    --build \
    --force-recreate \
    --runtime nvidia \
    --gpus all \
    --no-deps -f Dockerfile.cuda .

# Build the Docker image
build-docker:
    docker build --build-arg GH_TOKEN=$GH_TOKEN -t fastapi-app .

build-docker-no-cache:
    docker build --build-arg GH_TOKEN=$GH_TOKEN --no-cache -t fastapi-app .

build-cuda-docker:
    docker build --build-arg GH_TOKEN=$GH_TOKEN -f Dockerfile.cuda -t fastapi-app .

run-docker:
    echo "FastAPI server running at http://localhost:8001"
    docker run -p "8001:80" fastapi-app

# Default recipe
default:
    just run-server
