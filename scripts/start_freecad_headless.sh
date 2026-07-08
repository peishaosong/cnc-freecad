#!/bin/bash
# scripts/start_freecad_headless.sh - Launch FreeCAD headless (no GUI) with project auto-loaded.
#
# For CI, batch processing, or testing.

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FREECADCMD="/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd"

if [ ! -x "$FREECADCMD" ]; then
    echo "FreeCAD not found at $FREECADCMD"
    exit 1
fi

export PYTHONUTF8=1
export PYTHONIOENCODING=utf-8
export LANG=en_US.UTF-8

echo "Starting FreeCAD (headless) with project auto-loaded: $PROJECT_ROOT/src"
exec "$FREECADCMD" -P "$PROJECT_ROOT/src" "$@"