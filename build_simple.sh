#!/bin/bash
# Simple build script for Survival Curve Extractor

echo "Building Survival Curve Extractor..."

# Clean previous builds
rm -rf build dist __pycache__

# Build using PyInstaller with Poetry
poetry run pyinstaller \
    --onefile \
    --windowed \
    --name "SurvivalCurveExtractor" \
    --clean \
    --noconfirm \
    --hidden-import="PIL._tkinter_finder" \
    main.py

echo "Build complete! Check the dist/ directory for the executable."