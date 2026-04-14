#!/usr/bin/env bash
# Run Ergo UI server

set -e

cd "$(dirname "$0")/ui"

echo "Starting Ergo UI..."
echo "Interface will be available at: http://localhost:3000"
echo

# Set PYTHONPATH to include ui directory
export PYTHONPATH="$(pwd):${PYTHONPATH:-}"

# Try to use uvicorn directly if installed
if command -v uvicorn &> /dev/null; then
    exec uvicorn src.server:app \
        --host 127.0.0.1 \
        --port 3000
else
    echo "Error: uvicorn not found"
    echo "Please run from nix-shell: nix-shell"
    echo "Or install uvicorn: pip install uvicorn"
    exit 1
fi
