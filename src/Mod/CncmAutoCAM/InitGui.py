"""
FreeCAD Workbench entry point for CNC AutoCAM.

Loaded by FreeCAD at startup when symlinked into ~/Library/Application Support/FreeCAD/v1-1/Mod/CncmAutoCAM/.

This wrapper:
  1. Adds the project's src/ directory to sys.path (FreeCAD does NOT set __file__ in InitGui.py)
  2. Registers the CNC AutoCAM workbench

Path derivation: the symlink lives at
    <FreeCAD user Mod dir>/CncmAutoCAM -> <project>/src/Mod/CncmAutoCAM
We need to derive <project>/src/ from the symlink target, since __file__ is undefined.
"""
import os
import sys

# In FreeCAD 1.x InitGui.py, __file__ is NOT defined. We have to find our location another way.
# Strategy: FreeCAD adds the Mod/<name> directory to sys.path, so a unique import from
# within that directory works. We can also use FreeCAD.getUserAppDataDir() to find the symlink.

import FreeCAD

_USER_DATA = FreeCAD.getUserAppDataDir()  # ~/Library/Application Support/FreeCAD/v1-1/
_SYMLINK = os.path.join(_USER_DATA, "Mod", "CncmAutoCAM")

if os.path.islink(_SYMLINK):
    # Resolve symlink to project: .../src/Mod/CncmAutoCAM
    # We want .../src
    _resolved = os.path.realpath(_SYMLINK)  # .../src/Mod/CncmAutoCAM
    _SRC_DIR = os.path.dirname(os.path.dirname(_resolved))  # .../src
    if _SRC_DIR not in sys.path:
        sys.path.insert(0, _SRC_DIR)
else:
    # Dev mode fallback: if running directly (e.g. from test), use __file__ if available
    try:
        _THIS_DIR = os.path.dirname(os.path.abspath(__file__))
        _SRC_DIR = os.path.dirname(os.path.dirname(_THIS_DIR))
        if _SRC_DIR not in sys.path:
            sys.path.insert(0, _SRC_DIR)
    except NameError:
        # No __file__ and no symlink - try current dir's parent
        _SRC_DIR = os.path.dirname(os.path.dirname(os.getcwd()))
        if _SRC_DIR not in sys.path:
            sys.path.insert(0, _SRC_DIR)

from cnc_freecad.freecad.workbench import register

register()