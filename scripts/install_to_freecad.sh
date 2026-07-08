#!/bin/bash
# scripts/install_to_freecad.sh - Symlink project into FreeCAD's Mod directory
#
# After running, restart FreeCAD and the "CNC AutoCAM" workbench will appear.

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# FreeCAD's user Mod directory on macOS
MOD_DIR="$HOME/Library/Preferences/FreeCAD/v1-1/Mod"
TARGET="$MOD_DIR/CncmAutoCAM"

mkdir -p "$MOD_DIR"

if [ -L "$TARGET" ]; then
    echo "Removing old symlink: $TARGET"
    rm "$TARGET"
elif [ -d "$TARGET" ]; then
    echo "WARNING: $TARGET is a real directory, not a symlink"
    echo "Please remove manually: rm -rf $TARGET"
    exit 1
fi

echo "Symlinking: $TARGET -> $PROJECT_ROOT/src"
ln -s "$PROJECT_ROOT/src" "$TARGET"

echo
echo "[OK] Installed. Restart FreeCAD to see 'CNC AutoCAM' workbench."
echo
echo "Verification:"
ls -la "$TARGET"