#!/bin/bash
# scripts/start_freecad.sh - Launch FreeCAD with this project auto-loaded.
#
# No installation needed. Just run this script.
#
# Usage:
#   ./scripts/start_freecad.sh                # Launch FreeCAD GUI
#   ./scripts/start_freecad.sh --foo          # Pass through args to FreeCAD

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FREECAD_APP="/Applications/FreeCAD.app/Contents/MacOS/FreeCAD"

if [ ! -x "$FREECAD_APP" ]; then
    echo "FreeCAD not found at $FREECAD_APP"
    echo "Please install FreeCAD from https://www.freecad.org/"
    exit 1
fi

echo "Starting FreeCAD with project auto-loaded: $PROJECT_ROOT/src"
exec "$FREECAD_APP" -P "$PROJECT_ROOT/src" "$@"