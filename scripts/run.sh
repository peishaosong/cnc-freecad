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
    m1)
        $FREECAD_PYTHON -c "
import sys
sys.path.insert(0, '.')
from tests.test_m1_toolpath import run_all
sys.exit(run_all())
"
        ;;
    ui)
        # UI tests need QT offscreen (3D view won't render, but Qt does)
        export QT_QPA_PLATFORM=offscreen
        $FREECAD_PYTHON -c "
import sys
sys.path.insert(0, '.')
from tests.test_m1_ui import run_all
sys.exit(run_all())
"
        ;;
    all)
        $FREECAD_PYTHON -c "
import sys
sys.path.insert(0, '.')
from tests.test_env import run_all
rc1 = run_all()
from tests.test_m1_toolpath import run_all
rc2 = run_all()
sys.exit(rc1 or rc2)
"
        ;;
    all-ui)
        export QT_QPA_PLATFORM=offscreen
        $FREECAD_PYTHON -c "
import sys
sys.path.insert(0, '.')
from tests.test_env import run_all
rc1 = run_all()
from tests.test_m1_toolpath import run_all
rc2 = run_all()
from tests.test_m1_ui import run_all
rc3 = run_all()
sys.exit(rc1 or rc2 or rc3)
" || true
        ;;
    cli)
        shift
        FREECAD_PY="/Applications/FreeCAD.app/Contents/Resources/bin/python"
        PYTHONPATH="$PROJECT_ROOT/src:$PYTHONPATH" "$FREECAD_PY" -m cnc_freecad "$@"
        ;;
    install)
        bash "$PROJECT_ROOT/scripts/install_to_freecad.sh"
        ;;
    uninstall)
        bash "$PROJECT_ROOT/scripts/uninstall_from_freecad.sh"
        ;;
    *)
        # Treat as custom script path
        if [ -f "$CMD" ]; then
            $FREECAD_PYTHON "$CMD"
        else
            echo "Unknown command or missing script: $CMD"
            echo "Usage: $0 [verify|hello|test|m1|ui|all|all-ui|cli -- <args>|<script.py>]"
            exit 1
        fi
        ;;
esac