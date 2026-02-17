#!/bin/bash

echo "=========================================="
echo "   Deploying Jupyter Book to /docs"
echo "=========================================="

# Activate venv
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "[ERROR] venv not found. Run run.sh install first."
    exit 1
fi

echo "[1/4] Cleaning & Generating Table of Contents (_toc.yml)..."
IGNORE="README.md requirements.txt .nojekyll markdown.md markdown-notebooks.md notebooks.ipynb"
rm -rf _build docs
mkdir docs

echo "format: jb-book" > _toc.yml
echo "root: intro" >> _toc.yml
echo "chapters:" >> _toc.yml

# Function to get title from H1 or filename
get_title() {
    local file=$1
    local title=$(grep -m 1 "^# " "$file" | sed 's/^# //')
    if [ -z "$title" ]; then
        title=$(basename "$file" | sed -E 's/^[0-9]+[_-]//; s/\.(md|ipynb)$//; s/[-_]/ /g')
    fi
    echo "$title"
}

CHAPTERS_BLOCK=""

# Numbered files first
for f in $(find . -maxdepth 2 -name "*.md" -o -name "*.ipynb" | grep -vE "venv|_build|docs|scripts" | sort); do
    fname=$(basename "$f")
    if [[ ! " $IGNORE " =~ " $fname " ]] && [[ "$fname" =~ ^[0-9] ]]; then
        rel_path=$(echo "$f" | sed 's|^\./||; s|\.\(md\|ipynb\)$||')
        if [[ "$rel_path" == "md/intro" || "$rel_path" == "intro" ]]; then continue; fi
        title=$(get_title "$f")
        CHAPTERS_BLOCK="${CHAPTERS_BLOCK}\n- file: $rel_path\n  title: \"$title\""
    fi
done

# Non-numbered files
for f in $(find . -maxdepth 2 -name "*.md" -o -name "*.ipynb" | grep -vE "venv|_build|docs|scripts" | sort); do
    fname=$(basename "$f")
    if [[ ! " $IGNORE " =~ " $fname " ]] && [[ ! "$fname" =~ ^[0-9] ]]; then
        rel_path=$(echo "$f" | sed 's|^\./||; s|\.\(md\|ipynb\)$||')
        if [[ "$rel_path" == "md/intro" || "$rel_path" == "intro" ]]; then continue; fi
        title=$(get_title "$f")
        CHAPTERS_BLOCK="${CHAPTERS_BLOCK}\n- file: $rel_path\n  title: \"$title\""
    fi
done

if [ ! -z "$CHAPTERS_BLOCK" ]; then
    echo "chapters:" >> _toc.yml
    echo -e "$CHAPTERS_BLOCK" >> _toc.yml
fi

echo "[2/4] Building Jupyter Book..."
jupyter-book build --all .

echo "[3/4] Preparing /docs folder..."
rm -rf docs
mkdir docs

echo "[4/4] Copying build files to /docs..."
cp -R _build/html/. docs/
touch docs/.nojekyll
cp scripts/canvas-restricted.html docs/canvas.html

echo "=========================================="
echo "   Done! Sidebar & Titles automated."
echo "=========================================="
