#!/bin/bash

# Project Identity Setup
echo "=========================================="
echo "   Update Project Identity & Repository"
echo "=========================================="

read -p "Enter Author Name (Default: Roti18): " AUTHOR_NAME
if [ -z "$AUTHOR_NAME" ]; then AUTHOR_NAME="Roti18"; fi

read -p "Enter GitHub Username (Default: Roti18): " GITHUB_USER
if [ -z "$GITHUB_USER" ]; then GITHUB_USER="Roti18"; fi

CURRENT_YEAR=$(date +%Y)
REPO_NAME=$(basename "$(pwd)")
REPO_URL="https://github.com/$GITHUB_USER/$REPO_NAME"

# Update _config.yml
if [ -f "_config.yml" ]; then
    sed -i "s/^author: .*/author: \"$AUTHOR_NAME\"/" _config.yml
    sed -i "s|^  url: .*|  url: $REPO_URL|" _config.yml
    # Add or update copyright year
    if grep -q "^copyright:" _config.yml; then
        sed -i "s/^copyright: .*/copyright: \"$CURRENT_YEAR\"/" _config.yml
    else
        sed -i "/^author:/a copyright: \"$CURRENT_YEAR\"" _config.yml
    fi
    echo "[SUCCESS] _config.yml updated."
else
    echo "[ERROR] _config.yml not found!"
    exit 1
fi

echo "------------------------------------------"
echo "Identity: $AUTHOR_NAME | $CURRENT_YEAR"
echo "Repo URL: $REPO_URL"
echo "------------------------------------------"

# Ingin build ulang juga?
read -p "Build & Publish now? (y/n): " BUILD_NOW
if [[ "$BUILD_NOW" =~ ^[Yy]$ ]]; then
    bash scripts/publish.sh
fi

echo "Done."
