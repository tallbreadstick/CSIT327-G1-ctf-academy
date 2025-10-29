#!/usr/bin/env bash
set -e  # Stop on first error

echo "=== Step 1: Setting up Python environment ==="

# Ensure we're in project root
cd "$(dirname "$0")"

# Use .venv if it exists, else create it
VENV_DIR=".venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment in $VENV_DIR ..."
    python -m venv "$VENV_DIR"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
if [ -f requirements.txt ]; then
    echo "Installing dependencies from requirements.txt ..."
    pip install -r requirements.txt
else
    echo "requirements.txt not found. Installing Django only ..."
    pip install Django
fi

echo
echo "=== Step 2: Building TailwindCSS assets ==="

# Navigate to Tailwind source
cd ctf_academy/theme/static_src

# Ensure Node.js is installed
if ! command -v npm &> /dev/null; then
    echo "Error: Node.js and npm are not installed or not in PATH."
    exit 1
fi

echo "Installing Node.js dependencies ..."
npm install

echo "Building TailwindCSS assets ..."
npm run build

echo
echo "=== Build complete! ==="
