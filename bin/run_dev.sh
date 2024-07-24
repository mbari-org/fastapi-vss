#!/usr/bin/env bash
# Run development stack locally
# Get the directory of this script and the base directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
BASE_DIR="$(cd "$(dirname "${SCRIPT_DIR}/../.." )" && pwd )"
cd $BASE_DIR

# Export the environment variables in the .env file
export $(grep -v '^#' $BASE_DIR/.env |  xargs)

# Run the api server
export PYTHONPATH=$BASE_DIR/src
pkill -f "uvicorn main:app"

echo "FastAPI server running at http://localhost:8001"
echo "FastAPI docs running at http://localhost:8001/docs"
cd $BASE_DIR/src/app && uvicorn main:app --port 8001 --reload
