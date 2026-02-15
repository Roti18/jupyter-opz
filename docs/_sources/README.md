# Jupyter-OPZ

A streamlined Jupyter Book (v1.0.3) environment with an integrated Markdown Canvas editor for rapid content creation.

## Quick Start (Master Script)

All operations are managed through the master script run.sh (Linux/macOS) or run.bat (Windows).

### 1. Installation & Setup
Initialize the virtual environment, install dependencies, and perform the initial build.
```bash
# Linux/macOS
bash run.sh install

# Windows
run.bat install
```

### 2. Development Mode (Markdown Canvas)
Start the local server to access the Markdown Canvas editor. This command automatically activates the Canvas feature.
```bash
# Linux/macOS
bash run.sh dev

# Windows
run.bat dev
```
- Book Link: http://127.0.0.1:5000
- Canvas Link: http://127.0.0.1:5000/canvas

### 3. Build & Publish
Update the Table of Contents and build the static HTML for deployment.
```bash
bash run.sh publish
```

### 4. Reset Project
Wipe all build artifacts, virtual environments, and temporary files.
```bash
bash run.sh reset
```

---

## Writing Content

- File Naming: Use 0x_name.md format (e.g., 01_introduction.md).
- H1 Titles: Every file must start with an H1 title (# Title).
- Location: Put source files in the md/ directory.

---

## Deployment (GitHub Pages)

1. Build the book: `bash run.sh publish`
2. Push everything to GitHub.
3. In GitHub Settings > Pages, set Branch to `main` and Folder to `/docs`.

---

## Project Structure
- md/: Markdown source files.
- docs/: static HTML (for web).
- scripts/: System logic.
- run.sh / run.bat: Master commands.
