#!/bin/bash
# scripts/verify_env.sh - M0 environment verification
#
# Usage: ./scripts/verify_env.sh
FREECAD_PYTHON="/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd"
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

cd "$PROJECT_ROOT" || exit 1

echo "==================================="
echo "CNC AutoCAM - M0 Environment Check"
echo "Project: $PROJECT_ROOT"
echo "==================================="

# Save freecadcmd output to temp file and display
TMPFILE=$(mktemp)
$FREECAD_PYTHON -c "
import sys
sys.path.insert(0, '.')
from tests.test_env import run_all
run_all()
" > "$TMPFILE" 2>&1
EXIT_CODE=$?

cat "$TMPFILE"
rm -f "$TMPFILE"

echo
echo "==================================="
if [ $EXIT_CODE -eq 0 ]; then
    echo "[OK] M0 verification: PASSED"
else
    echo "[FAIL] M0 verification: FAILED (exit $EXIT_CODE)"
fi
echo "==================================="

exit $EXIT_CODE