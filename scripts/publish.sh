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

echo "[1/4] Auto-Generating Table of Contents (_toc.yml)..."
IGNORE="intro.md README.md requirements.txt requirements-install.txt .nojekyll markdown.md markdown-notebooks.md notebooks.ipynb"

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

# Numbered files first
for f in $(find . -maxdepth 2 -name "*.md" -o -name "*.ipynb" | grep -vE "venv|_build|docs|scripts" | sort); do
    fname=$(basename "$f")
    if [[ ! " $IGNORE " =~ " $fname " ]] && [[ "$fname" =~ ^[0-9] ]]; then
        rel_path=$(echo "$f" | sed 's|^\./||; s|\.\(md\|ipynb\)$||')
        title=$(get_title "$f")
        echo "- file: $rel_path" >> _toc.yml
        echo "  title: \"$title\"" >> _toc.yml
    fi
done

# Non-numbered files
for f in $(find . -maxdepth 2 -name "*.md" -o -name "*.ipynb" | grep -vE "venv|_build|docs|scripts" | sort); do
    fname=$(basename "$f")
    if [[ ! " $IGNORE " =~ " $fname " ]] && [[ ! "$fname" =~ ^[0-9] ]]; then
        rel_path=$(echo "$f" | sed 's|^\./||; s|\.\(md\|ipynb\)$||')
        title=$(get_title "$f")
        echo "- file: $rel_path" >> _toc.yml
        echo "  title: \"$title\"" >> _toc.yml
    fi
done

echo "[2/4] Building Jupyter Book..."
jupyter-book build .

echo "[3/4] Preparing /docs folder..."
rm -rf docs
mkdir docs

echo "[4/4] Copying build files to /docs..."
cp -R _build/html/. docs/
touch docs/.nojekyll

# Post-processing: Replace all types of em-dash/dash with pipe in titles
echo "[EXTRA] Fixing Title separators (em-dash/dash -> |)..."
find docs -name "*.html" -exec sed -i -E 's/<title>(.*) (&#8212;|&mdash;|—|-) (.*)<\/title>/<title>\1 | \3<\/title>/g' {} +

echo "=========================================="
echo "   Done! Sidebar & Titles automated."
echo "=========================================="
