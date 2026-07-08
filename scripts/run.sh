#!/bin/bash
# scripts/run.sh - Universal runner for cnc-freecad scripts
#
# Usage:
#   ./scripts/run.sh verify           - Run M0 environment verification
#   ./scripts/run.sh hello            - Run Hello CNC demo
#   ./scripts/run.sh test             - Run all tests
#   ./scripts/run.sh <script.py>      - Run a custom script

set -e

# Force UTF-8 for freecadcmd's bundled Python
export PYTHONUTF8=1
export PYTHONIOENCODING=utf-8
export LANG=en_US.UTF-8

FREECAD_PYTHON="/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd"
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

cd "$PROJECT_ROOT"

CMD="${1:-verify}"

case "$CMD" in
    verify)
        $FREECAD_PYTHON -c "
import sys
sys.path.insert(0, '.')
from tests.test_env import run_all
sys.exit(run_all())
"
        ;;
    hello)
        $FREECAD_PYTHON -c "
import sys
sys.path.insert(0, '.')
from scripts.hello_cnc import main
main()
"
        ;;
    test)
        $FREECAD_PYTHON -c "
import sys
sys.path.insert(0, '.')
from tests.test_env import run_all
sys.exit(run_all())
"
        ;;
    *)
        # Treat as custom script path
        if [ -f "$CMD" ]; then
            $FREECAD_PYTHON "$CMD"
        else
            echo "Unknown command or missing script: $CMD"
            echo "Usage: $0 [verify|hello|test|<script.py>]"
            exit 1
        fi
        ;;
esac