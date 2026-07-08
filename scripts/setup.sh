#!/bin/bash
# scripts/setup.sh - Install CNC AutoCAM as a FreeCAD workbench (one-time).
#
# After this, every FreeCAD startup auto-loads the project.
#
# Usage:
#   ./scripts/setup.sh           # Install
#   ./scripts/setup.sh remove    # Uninstall
#   ./scripts/setup.sh status    # Show install state

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON="${PYTHON:-python3}"

case "${1:-add}" in
    remove) exec "$PYTHON" "$SCRIPT_DIR/setup.py" remove ;;
    status) exec "$PYTHON" "$SCRIPT_DIR/setup.py" status ;;
    add|"") exec "$PYTHON" "$SCRIPT_DIR/setup.py" add ;;
    *) echo "Usage: $0 [add|remove|status]"; exit 1 ;;
esac