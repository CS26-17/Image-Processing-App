#!/usr/bin/env bash
set -e

# This script lives in scripts/ but the project root is one level up
cd "$(dirname "$0")/.."

echo "Project root: $(pwd)"

# Create virtual env if it doesn't exist
if [ ! -f ".venv/bin/python" ]; then
  echo "Creating virtual environment..."
  python3 -m venv .venv
fi

# Install / upgrade dependencies
echo "Installing dependencies..."
.venv/bin/python -m pip install --upgrade pip --quiet
.venv/bin/python -m pip install -r requirements.txt --quiet

# Launch the app
echo "Launching app..."
.venv/bin/python image_processing_app.py