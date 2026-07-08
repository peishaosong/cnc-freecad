"""
InitGui.py - FreeCAD looks for this file in the Mod directory.

When FreeCAD loads this workbench, it calls register() which adds the workbench.
"""
import sys
import os

# Make sure our package is importable
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_THIS_DIR)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from cnc_freecad.freecad.workbench import register

register()