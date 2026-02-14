#!/bin/bash

echo "=========================================="
echo "   Installing Jupyter Book 1.0.3 (VENV)"
echo "=========================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null
then
    echo "[ERROR] python3 could not be found. Please install Python first."
    exit 1
fi

echo "[1/6] Creating Virtual Environment (venv)..."
python3 -m venv venv

echo "[2/6] Activating Virtual Environment..."
source venv/bin/activate

echo "[3/6] Menginstall Requirements (Tools)..."
python3 -m pip install --upgrade pip
pip install -r requirements-install.txt

echo "[4/6] Creating and Building 'Pendat' Folder..."
# Create a template book in 'Pendat' if it doesn't exist
if [ ! -d "Pendat" ]; then
    jupyter-book create Pendat
fi

# Build the book
echo "Building Jupyter Book..."
jupyter-book build Pendat/

echo "[5/6] Moving all contents from Pendat to Root..."
# Move everything from Pendat to the current directory
if [ -d "Pendat" ]; then
    cp -rn Pendat/* ./ 2>/dev/null
    cp -rn Pendat/.* ./ 2>/dev/null
fi

echo "[6/6] Cleaning up Pendat folder..."
# Remove Pendat folder as requested
rm -rf Pendat

echo "=========================================="
echo "   Process Finished!"
echo "   Venv: Active (use 'source venv/bin/activate' next time)"
echo "   Build: results in '_build' folder"
echo "=========================================="
