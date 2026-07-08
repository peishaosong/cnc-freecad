"""
FreeCAD integration layer.

Modules:
- workbench: Workbench registration
- commands: FreeCAD command implementations
- ui: PySide6 dialogs and panels
- visualize: convert Toolpath to FreeCAD Path objects
"""
from cnc_freecad.freecad.workbench import register

__all__ = ["register"]