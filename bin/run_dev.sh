#!/usr/bin/env bash
# Run development stack locally
# Get the directory of this script and the base directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
BASE_DIR="$(cd "$(dirname "${SCRIPT_DIR}/../.." )" && pwd )"
cd $BASE_DIR

# Export the environment variables in the .env file
export $(grep -v '^#' $BASE_DIR/.env |  xargs)

# Run the api server
export PYTHONPATH=$BASE_DIR/src:$BASE_DIR/src/submodules/aidata
pkill -f "uvicorn main:app"

echo "FastAPI server running at http://localhost:8002"
echo "FastAPI docs running at http://localhost:8002/docs"
export CONFIG_PATH=/u/mldevops/code/fastapi-vss/config
cd $BASE_DIR/src/app && uvicorn main:app --port 8002 --reload
