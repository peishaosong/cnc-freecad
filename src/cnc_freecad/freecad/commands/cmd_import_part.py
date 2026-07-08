"""
Command: Import STEP file and create a Body.
"""
import os

import FreeCAD
import FreeCADGui
from PySide6 import QtCore, QtGui, QtWidgets


class CncmImportPart:
    """Import a STEP file as the active Body."""

    def GetResources(self):
        return {
            "MenuText": "Import STEP",
            "ToolTip": "Import a STEP/IGES file and create a Body for machining",
            "Accel": "Ctrl+I",
            "Pixmap": "",
        }

    def Activated(self):
        # Show file dialog
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            None,
            "Import STEP/IGES",
            "",
            "STEP Files (*.step *.stp);;IGES Files (*.iges *.igs);;All Files (*)",
        )
        if not path:
            return

        # Import
        try:
            import Part
            Part.insert(path, FreeCAD.ActiveDocument.Name)
            shape = FreeCAD.ActiveDocument.ActiveObject.Shape
            FreeCAD.Console.PrintMessage(f"Imported: {path}\n")
            FreeCAD.Console.PrintMessage(f"  Volume: {shape.Volume:.2f}\n")
            FreeCAD.Console.PrintMessage(f"  Faces: {len(shape.Faces)}\n")
            FreeCAD.ActiveDocument.recompute()
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                None, "Import Failed", f"Failed to import file:\n{e}"
            )

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None