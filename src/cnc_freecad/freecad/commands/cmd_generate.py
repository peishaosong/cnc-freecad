"""
Command: Generate toolpath from current feature + tool + template, display in 3D view.
"""
import FreeCAD
import FreeCADGui

from cnc_freecad.core.toolpath_generator import ToolpathGenerator
from cnc_freecad.data.models import Operation, ProcessPlan
from cnc_freecad.freecad.session import session
from cnc_freecad.freecad.visualize import display_toolpath


class CncmGenerate:
    def GetResources(self):
        return {
            "MenuText": "Generate Toolpath",
            "ToolTip": "Generate toolpath from selected feature + tool + template",
            "Accel": "Ctrl+G",
            "Pixmap": "",
        }

    def Activated(self):
        # Validate session state
        if not session.features:
            FreeCAD.Console.PrintError("No features defined. Use 'Define Feature' first.\n")
            return
        if session.tool is None:
            FreeCAD.Console.PrintError("No tool selected. Use 'Select Tool' first.\n")
            return
        if session.template is None:
            FreeCAD.Console.PrintError("No template selected. Use 'Select Template' first.\n")
            return

        # Build process plan
        plan = ProcessPlan(
            part_name=FreeCAD.ActiveDocument.Name,
            material=session.material,
            operations=[
                Operation(
                    feature_id=f.id,
                    template=session.template,
                    tool=session.tool,
                    sequence=i + 1,
                )
                for i, f in enumerate(session.features.values())
            ],
        )

        # Generate
        gen = ToolpathGenerator()
        toolpaths = []
        for op in plan.operations:
            feature = session.features[op.feature_id]
            try:
                tp = gen.generate(feature, op.template, op.tool)
                toolpaths.append(tp)
            except Exception as e:
                FreeCAD.Console.PrintError(f"Failed: {e}\n")
                return

        # Display in 3D view
        display_toolpath(toolpaths, session.template.strategy)

        FreeCAD.Console.PrintMessage(
            f"Generated {len(toolpaths)} toolpath(s), "
            f"total {sum(len(tp.segments) for tp in toolpaths)} segments\n"
        )

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None