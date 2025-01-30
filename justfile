#!/usr/bin/env just --justfile

set dotenv-required

# Source the .env file
set dotenv-load := true

# List recipes
list:
    @just --list --unsorted

# Build the docker images for linux/amd64 and linux/arm64 and push to Docker Hub
build-and-push:
    #!/usr/bin/env bash
    echo "Building and pushing the Docker image"
    RELEASE_VERSION=$(git describe --tags --abbrev=0)
    echo "Release version: $RELEASE_VERSION"
    RELEASE_VERSION=${RELEASE_VERSION:1}
    docker buildx create --name mybuilder --platform linux/amd64,linux/arm64 --use
    docker buildx build --sbom=true --provenance=true --push --platform linux/amd64,linux/arm64 -t mbari/fastapi-vss:$RELEASE_VERSION --build-arg IMAGE_URI=mbari/fastapi-vss:$RELEASE_VERSION -f Dockerfile .
    docker buildx build --sbom=true --provenance=true --push --platform linux/amd64,linux/arm64 -t mbari/fastapi-vss:$RELEASE_VERSION-cuda124 --build-arg IMAGE_URI=mbari/fastapi-vss:$RELEASE_VERSION -f Dockerfile.cuda .

# Setup the environment
install:
    conda env create -f environment.yml
    git clone --branch v1.16.0 https://github.com/mbari-org/aidata ./src/aidata
    python -m pip install -r src/aidata/requirements.txt
    python -m pip install https://github.com/redis/redis-py/archive/refs/tags/v5.0.9.zip

# Update the conda environment. Run this command after checking out any code changes
update:
    conda env update --file environment.yml --prune
    python -m pip install https://github.com/redis/redis-py/archive/refs/tags/v5.0.9.zip

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
    export PYTHONPATH=$PWD/src:/Users/dcline/Dropbox/code/aidata
    cd src/app && conda run -n fastapi-vss --no-capture-output uvicorn main:app --port 8002 --reload

run-server-prod: build-docker
    #!/usr/bin/env bash
    tag=$(git describe --tags --always)
    GIT_VERSION=$tag COMPOSE_PROJECT_NAME=fastapi-vss docker-compose -f compose.yml down --remove-orphans && \
    GIT_VERSION=$tag COMPOSE_PROJECT_NAME=fastapi-vss docker-compose -f compose.yml up -d

# Build the Docker image
build-docker:
    #!/usr/bin/env bash
    tag=$(git describe --tags --always)
    docker build -t mbari/fastapi-app:$tag .

# Build the CUDA Docker image
build-docker-cuda:
    #!/usr/bin/env bash
    tag=$(git describe --tags --always)
    docker build -t mbari/fastapi-app:$tag -f Dockerfile.cuda .

build-docker-no-cache:
    #!/usr/bin/env bash
    tag=$(git describe --tags --always)
    docker build --no-cache -t mbari/fastapi-app:$tag .

run-docker:
    echo "FastAPI server running at http://localhost:8001"
    docker run -p "8001:80" mbari/fastapi-app

# Default recipe
default:
    just run-server

test_all_ids:
    #!/usr/bin/env bash
    curl -X 'POST' \
      'http://localhost:8002/ids/cfe' \
      -H 'accept: application/json' \
      -d ''

process_atolla:
    #!/usr/bin/env bash
    cd ./tests/images/atolla
    curl -X 'POST' \
     'http:/localhost:8002/knn/3/i2map' \
     -H 'accept: application/json' \
     -H 'Content-Type: multipart/form-data' \
     -F 'files=@atolla1.png;type=image/png'
    curl -X 'POST' \
     'http:/localhost:8002/knn/3/i2map' \
     -H 'accept: application/json' \
     -H 'Content-Type: multipart/form-data' \
     -F 'files=@atolla2.png;type=image/png'
    curl -X 'POST' \
     'http:/localhost:8002/knn/3/i2map' \
     -H 'accept: application/json' \
     -H 'Content-Type: multipart/form-data' \
     -F 'files=@atolla3.png;type=image/png'


process_copepods:
    #!/usr/bin/env bash
    cd ./tests/images/copepod
    curl -X 'POST' \
     'http:/localhost:8002/knn/3/902111-CFE' \
     -H 'accept: application/json' \
     -H 'Content-Type: multipart/form-data' \
     -F 'files=@copepod1.png;type=image/png'
    curl -X 'POST' \
     'http:/localhost:8002/knn/3/902111-CFE' \
     -H 'accept: application/json' \
     -H 'Content-Type: multipart/form-data' \
     -F 'files=@copepod2.png;type=image/png'
    curl -X 'POST' \
     'http:/localhost:8002/knn/3/902111-CFE' \
     -H 'accept: application/json' \
     -H 'Content-Type: multipart/form-data' \
     -F 'files=@copepod3.png;type=image/png'
