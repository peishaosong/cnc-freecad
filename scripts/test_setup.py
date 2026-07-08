"""Verify workbench auto-loads via AdditionalModulePaths (no -P flag)."""
import sys
import os

# Do NOT use -P flag - this tests the user.cfg AdditionalModulePaths mechanism

import FreeCAD
import FreeCADGui
print(f"FreeCAD GUI: {FreeCADGui.__name__}", flush=True)

# Workbench should already be loaded (from AdditionalModulePaths scan)
wb_list = FreeCADGui.listWorkbenches()
print(f"Total workbenches: {len(wb_list)}", flush=True)

found = False
print("All workbenches:", flush=True)
for name in wb_list:
    print(f"  - {name}", flush=True)
    if "Cncm" in name or "_Cncm" in name:
        found = True

if found:
    print("[OK] CncmWorkbench auto-loaded", flush=True)
else:
    print("[FAIL] CncmWorkbench NOT auto-loaded", flush=True)
    print("       Try: ./scripts/setup.sh", flush=True)
    sys.exit(1)

print("DONE", flush=True)
sys.exit(0)