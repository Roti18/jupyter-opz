#!/bin/bash

echo "=========================================="
echo "   Deploying Jupyter Book to /docs"
echo "=========================================="

# Activate venv
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "[ERROR] venv not found. Run install.sh first."
    exit 1
fi

# Step 1: Build the book
echo "[1/3] Building Jupyter Book..."
jupyter-book build .

# Step 2: Prepare docs folder
echo "[2/3] Preparing /docs folder..."
rm -rf docs
mkdir docs

# Step 3: Copy HTML files to docs
echo "[3/3] Copying build files to /docs..."
cp -R _build/html/. docs/

# Create .nojekyll
touch docs/.nojekyll

echo "=========================================="
echo "   Done! HTML files are in /docs"
echo "=========================================="
