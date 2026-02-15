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

echo "[3/6] Installing Requirements (Tools)..."
python3 -m pip install --upgrade pip
pip install -r scripts/requirements-install.txt

echo "[4/6] Initializing Project..."
# Only create temporary folder if it doesn't exist
if [ ! -d "Pendat" ]; then
    jupyter-book create Pendat
fi

# Build the book
echo "Building Jupyter Book..."
jupyter-book build Pendat/

echo "[5/6] Moving contents to Root..."
cp -rn Pendat/* ./ 2>/dev/null
cp -rn Pendat/.* ./ 2>/dev/null
rm -rf Pendat

# Create .nojekyll in root
touch .nojekyll

echo "[6/7] Cleaning up sample files..."
rm -f markdown.md markdown-notebooks.md notebooks.ipynb
rm -f _build/html/markdown.html _build/html/markdown-notebooks.html _build/html/notebooks.html
rm -f docs/markdown.html docs/markdown-notebooks.html docs/notebooks.html

echo "[7/7] Finishing Installation..."

# Project Title Setup
echo "------------------------------------------"
read -p "Enter your Project/Book Title (e.g. My Awesome Book): " PROJECT_TITLE
if [ -z "$PROJECT_TITLE" ]; then
    PROJECT_TITLE="Jupyter Optimization"
fi

# Update _config.yml with the new title
if [ -f "_config.yml" ]; then
    sed -i "s/^title: .*/title: \"$PROJECT_TITLE\"/" _config.yml
fi
echo "[SUCCESS] Project Title set to: $PROJECT_TITLE"

bash scripts/publish.sh

echo "=========================================="
echo "   Process Finished & Published!"
echo "   Venv: Active"
echo "   Run 'bash run.sh dev' to start Canvas."
echo "=========================================="
