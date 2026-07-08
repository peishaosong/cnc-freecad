#!/bin/bash
# scripts/uninstall_from_freecad.sh - Remove the symlink from FreeCAD's Mod directory

set -e

MOD_DIR="$HOME/Library/Preferences/FreeCAD/v1-1/Mod"
TARGET="$MOD_DIR/CncmAutoCAM"

if [ -L "$TARGET" ]; then
    rm "$TARGET"
    echo "[OK] Removed: $TARGET"
else
    echo "Not installed (no symlink at $TARGET)"
fi