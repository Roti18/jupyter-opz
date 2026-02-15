#!/bin/bash

# Master Script for Jupyter-OPZ
CMD=$1

show_usage() {
    echo "=========================================="
    echo "         Jupyter-OPZ Master Tool"
    echo "=========================================="
    echo "Usage: bash run.sh [command]"
    echo ""
    echo "Commands:"
    echo "  install   : Setup environment and build book"
    echo "  dev       : Start dev server & Markdown Canvas"
    echo "  publish   : Update TOC and build to /docs"
    echo "  config    : Update Author identity & GitHub Repo"
    echo "  reset     : Full cleanup (removes venv, build, etc)"
    echo "=========================================="
}

if [ -z "$CMD" ]; then
    show_usage
    exit 1
fi

case $CMD in
    install)
        bash scripts/install.sh
        ;;
    dev)
        bash scripts/dev.sh
        ;;
    publish)
        bash scripts/publish.sh
        ;;
    config)
        bash scripts/setup.sh
        ;;
    reset)
        echo "Resetting project..."
        rm -rf __pycache__ _build docs .env scripts/dev.log scripts/dev_server.log venv Pendat 2>/dev/null
        echo "Done. All build artifacts and virtual environment removed."
        ;;
    *)
        echo "[ERROR] Unknown command: $CMD"
        show_usage
        exit 1
        ;;
esac
