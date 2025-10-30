#!/bin/bash
# Simple Setup Script - Mac/Linux

echo "Setting up development environment..."

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

echo ""
echo "Setup complete"
echo ""
echo "To start developing:"
echo "  1. Activate environment: source venv/bin/activate"
echo "  2. Run app: python xxx.py"
echo "  3. Open in VS Code: code ."
