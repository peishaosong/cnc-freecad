"""
FreeCAD Workbench registration for CNC AutoCAM.

Loaded by FreeCAD at startup if installed to ~/.FreeCAD/Mod/CncmAutoCAM/

Architecture:
- Workbench: menu bar + toolbars
- Commands: registered via FreeCADGui.addCommand
- Dialogs: PySide6 (UI input/output)
- Visualization: convert Toolpath -> FreeCAD Path object (3D view)

Headless-safe: imports work in both freecadcmd (no GUI) and freecad (GUI).
"""
from __future__ import annotations

import os
import sys

# Make sure we can import the core even if FreeCAD's import path is weird
_PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)


def _detect_gui():
    """Return True if FreeCAD GUI is available."""
    try:
        import FreeCADGui
        # FreeCADGui exists in headless mode but only exposes modules,
        # not classes like Workbench. Check class existence.
        return hasattr(FreeCADGui, "Workbench")
    except ImportError:
        return False


GUI_AVAILABLE = _detect_gui()


def CncmWorkbench():
    """Factory: build a FreeCAD Workbench subclass dynamically.

    Cannot subclass at module load time because in headless mode
    FreeCADGui.Workbench doesn't exist yet.
    """
    import FreeCADGui

    class _CncmWorkbench(FreeCADGui.Workbench):
        MenuText = "CNC AutoCAM"
        ToolTip = "CNC Automatic Programming Module"
        Icon = ""

        def Initialize(self):
            from cnc_freecad.freecad.commands import (
                cmd_import_part, cmd_define_feature, cmd_select_tool,
                cmd_select_template, cmd_generate, cmd_postprocess,
            )
            self.commands = [
                "CncmImportPart",
                "CncmDefineFeature",
                "CncmSelectTool",
                "CncmSelectTemplate",
                "CncmGenerate",
                "CncmPostprocess",
            ]
            self.appendToolbar("CNC AutoCAM", self.commands)
            self.appendMenu("CNC AutoCAM", self.commands)

        def Activated(self):
            FreeCAD.Console.PrintMessage("CNC AutoCAM workbench activated\n")

        def Deactivated(self):
            pass

    return _CncmWorkbench


def register():
    """Register the workbench with FreeCAD. Called by InitGui.py."""
    if not GUI_AVAILABLE:
        return False
    try:
        import FreeCADGui
        FreeCADGui.addWorkbench(CncmWorkbench())
        return True
    except Exception as e:
        try:
            import FreeCAD
            FreeCAD.Console.PrintError(f"CncmWorkbench register failed: {e}\n")
        except ImportError:
            pass
        return False