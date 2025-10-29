#!/usr/bin/env bash
set -e

# Go to project root
cd "$(dirname "$0")"

VENV_DIR=".venv"
if [ ! -f "$VENV_DIR/bin/activate" ]; then
    if [ -f "venv/bin/activate" ]; then
        VENV_DIR="venv"
    fi
fi

if [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo "No virtual environment found. Run build.sh first to create and install dependencies."
    exit 1
fi

# Activate the virtual environment
source "$VENV_DIR/bin/activate"

# Determine port: use $PORT if provided (Render), otherwise default to 8000
if [ -z "$PORT" ]; then
    PORT=8000
fi

# Determine host: 0.0.0.0 if deployed, else localhost
if [ "$PORT" != "8000" ]; then
    HOST="0.0.0.0"
else
    HOST="127.0.0.1"
fi

echo "Starting Django development server on $HOST:$PORT ..."
python ctf_academy/manage.py runserver "$HOST:$PORT"
