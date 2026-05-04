#!/bin/bash
# Build script for macOS
# Usage: bash scripts/build_macos.sh
#
# Produces: dist/Image Processing App.app
# Optionally wraps it in a DMG if create-dmg is installed:
#   brew install create-dmg

set -e

cd "$(dirname "$0")/.."

# ── Activate venv ──────────────────────────────────────────────────────────────
if [ ! -d ".venv" ]; then
    echo "ERROR: .venv not found. Run setup_dev_env.sh first."
    exit 1
fi
source .venv/bin/activate

# ── Install / upgrade PyInstaller ─────────────────────────────────────────────
echo ">>> Installing PyInstaller..."
pip install --quiet --upgrade pyinstaller

# ── Clean previous build ───────────────────────────────────────────────────────
echo ">>> Cleaning previous build..."
rm -rf build dist

# ── Build ──────────────────────────────────────────────────────────────────────
echo ">>> Building .app bundle (this will take a few minutes)..."
pyinstaller image_processing_app.spec

echo ""
echo "✓ Build complete: dist/Image Processing App.app"
echo ""

# ── Optional: wrap in DMG ──────────────────────────────────────────────────────
if command -v create-dmg &> /dev/null; then
    echo ">>> Packaging into DMG..."
    create-dmg \
        --volname "Image Processing App" \
        --window-size 600 400 \
        --icon-size 100 \
        --icon "Image Processing App.app" 150 190 \
        --app-drop-link 450 190 \
        "dist/ImageProcessingApp.dmg" \
        "dist/Image Processing App.app"
    echo "✓ DMG ready: dist/ImageProcessingApp.dmg"
else
    echo "Tip: install create-dmg (brew install create-dmg) to also produce a .dmg"
fi
