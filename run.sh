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

# Run Django server, forwarding all args
python ctf_academy/manage.py runserver "$@"
