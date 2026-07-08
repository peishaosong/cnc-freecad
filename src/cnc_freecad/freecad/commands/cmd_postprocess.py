"""
Command: Post-process toolpath to G-code, save to file.
"""
import os
from datetime import datetime

import FreeCAD
import FreeCADGui
from PySide6 import QtWidgets

from cnc_freecad.core.engine import CNCEngine
from cnc_freecad.core.toolpath_generator import ToolpathGenerator
from cnc_freecad.data.models import Operation, ProcessPlan
from cnc_freecad.freecad.session import session


class CncmPostprocess:
    def GetResources(self):
        return {
            "MenuText": "Post-process",
            "ToolTip": "Convert toolpath to G-code and save to file",
            "Accel": "Ctrl+E",
            "Pixmap": "",
        }

    def Activated(self):
        if not session.features or session.tool is None or session.template is None:
            FreeCAD.Console.PrintError(
                "Missing feature/tool/template. Complete steps 1-3 first.\n"
            )
            return

        # Ask for save path
        default_name = f"{FreeCAD.ActiveDocument.Name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.nc"
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            None, "Save G-code",
            os.path.join(os.path.expanduser("~/Desktop"), default_name),
            "G-code Files (*.nc *.gcode *.fnc);;All Files (*)",
        )
        if not path:
            return

        # Build plan + generate
        plan = ProcessPlan(
            part_name=FreeCAD.ActiveDocument.Name,
            material=session.material,
            operations=[
                Operation(feature_id=f.id, template=session.template,
                         tool=session.tool, sequence=i + 1)
                for i, f in enumerate(session.features.values())
            ],
        )
        gen = ToolpathGenerator()
        features = session.features
        toolpaths = []
        for op in plan.operations:
            tp = gen.generate(features[op.feature_id], op.template, op.tool)
            toolpaths.append(tp)

        engine = CNCEngine()
        gcode = engine.postprocess(toolpaths, machine="fanuc")

        with open(path, "w") as f:
            f.write(gcode)

        FreeCAD.Console.PrintMessage(f"G-code written to: {path}\n")
        FreeCAD.Console.PrintMessage(f"  Size: {len(gcode)} chars, {gcode.count(chr(10))} lines\n")

        QtWidgets.QMessageBox.information(
            None, "G-code Generated",
            f"G-code saved to:\n{path}\n\nSize: {len(gcode)} chars"
        )

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None