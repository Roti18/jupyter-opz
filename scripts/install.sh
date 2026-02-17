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
pip install -r scripts/requirements.txt

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
rm -f intro.md markdown.md markdown-notebooks.md notebooks.ipynb
rm -f _build/html/markdown.html _build/html/markdown-notebooks.html _build/html/notebooks.html
rm -f docs/markdown.html docs/markdown-notebooks.html docs/notebooks.html

# Project Identity Setup
echo "------------------------------------------"
read -p "Enter Author Name (Default: Roti18): " AUTHOR_NAME
if [ -z "$AUTHOR_NAME" ]; then AUTHOR_NAME="Roti18"; fi

read -p "Enter GitHub Repository URL (e.g. https://github.com/roti18/jupyter-opz): " REPO_URL
if [ -z "$REPO_URL" ]; then 
    GITHUB_USER="Roti18"
    REPO_NAME=$(basename "$(pwd)")
    REPO_URL="https://github.com/$GITHUB_USER/$REPO_NAME"
fi

CURRENT_YEAR=$(date +%Y)

# Update _config.yml
if [ -f "_config.yml" ]; then
    sed -i "s/^author: .*/author: \"$AUTHOR_NAME\"/" _config.yml
    sed -i "s|^  url: .*|  url: $REPO_URL|" _config.yml
    sed -i "s/^  branch: .*/  branch: main/" _config.yml
    # Add or update copyright year
    if grep -q "^copyright:" _config.yml; then
        sed -i "s/^copyright: .*/copyright: \"$CURRENT_YEAR\"/" _config.yml
    else
        sed -i "/^author:/a copyright: \"$CURRENT_YEAR\"" _config.yml
    fi
fi

echo "[SUCCESS] Identity updated: $AUTHOR_NAME | $CURRENT_YEAR"
echo "[SUCCESS] Repository set to: $REPO_URL"

bash scripts/publish.sh

echo "=========================================="
echo "   Process Finished & Published!"
echo "   Venv: Active"
echo "   Run 'bash run.sh dev' to start Canvas."
echo "=========================================="
