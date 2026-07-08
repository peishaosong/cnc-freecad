import sys
import FreeCAD
print("FreeCAD:", FreeCAD.Version()[0], flush=True)
sys.path.insert(0, "/Users/peishaosong/Desktop/松少/projects/cnc-freecad/src")
from cnc_freecad.freecad.workbench import register, GUI_AVAILABLE
print("Module import OK", flush=True)
print("GUI_AVAILABLE:", GUI_AVAILABLE, flush=True)
print("register() returned:", register(), flush=True)
print("All OK", flush=True)