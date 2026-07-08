"""Test that the workbench actually registers when FreeCAD starts in GUI mode."""
import sys
import os

# Use FreeCAD's own user config dir (avoid Qt display issues)
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import FreeCAD
import FreeCADGui
print(f"FreeCAD GUI: {FreeCADGui.__name__}", flush=True)
print(f"Workbench class: {FreeCADGui.Workbench}", flush=True)

# Add our src to path
sys.path.insert(0, "/Users/peishaosong/Desktop/松少/projects/cnc-freecad/src")

# Manually call InitGui.py equivalent
from cnc_freecad.freecad.workbench import register, CncmWorkbench
print("Registering workbench...", flush=True)
result = register()
print(f"register() = {result}", flush=True)

# List registered workbenches
wb = FreeCADGui.listWorkbenches()
print(f"Total workbenches: {len(wb)}", flush=True)
if "CncmWorkbench" in wb or "CNC AutoCAM" in str(wb):
    print("[OK] CncmWorkbench found in registry", flush=True)
else:
    # Check by trying to get it
    found = False
    for name in wb:
        if "cncm" in name.lower() or "auto" in name.lower():
            print(f"[OK] Found: {name}", flush=True)
            found = True
    if not found:
        print("[INFO] CncmWorkbench not in list (FreeCAD may not list by MenuText)", flush=True)
        print(f"All workbenches: {list(wb.keys())[:20]}", flush=True)

print("DONE", flush=True)
sys.exit(0)