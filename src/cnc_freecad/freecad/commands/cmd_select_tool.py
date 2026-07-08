"""
Command: Select tool via dialog (preset library).
"""
import FreeCAD
import FreeCADGui
from PySide6 import QtWidgets

from cnc_freecad.data.models import Tool, ToolMaterial, ToolType
from cnc_freecad.freecad.session import session


# Preset tool library for M1 (aluminum cutting, common sizes)
PRESETS = [
    {
        "id": "T1_d12_flat", "type": ToolType.FLAT_ENDMILL, "diameter": 12.0,
        "material": ToolMaterial.CARBIDE, "num_flutes": 4, "max_rpm": 15000,
        "description": "12mm Carbide Flat (roughing)",
    },
    {
        "id": "T2_d8_flat", "type": ToolType.FLAT_ENDMILL, "diameter": 8.0,
        "material": ToolMaterial.CARBIDE, "num_flutes": 4, "max_rpm": 18000,
        "description": "8mm Carbide Flat (finishing)",
    },
    {
        "id": "T3_d6_ball", "type": ToolType.BALL_ENDMILL, "diameter": 6.0,
        "material": ToolMaterial.CARBIDE, "num_flutes": 2, "max_rpm": 20000,
        "description": "6mm Carbide Ball (3D)",
    },
    {
        "id": "T4_d6_drill", "type": ToolType.DRILL, "diameter": 6.0,
        "material": ToolMaterial.HSS, "num_flutes": 2, "max_rpm": 3000,
        "description": "6mm HSS Drill",
    },
]


class ToolDialog(QtWidgets.QDialog):
    """Dialog to select a tool from presets."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Tool")
        self.setMinimumWidth(400)

        layout = QtWidgets.QVBoxLayout()

        # List of presets
        layout.addWidget(QtWidgets.QLabel("Select a tool preset:"))
        self.list = QtWidgets.QListWidget()
        for p in PRESETS:
            self.list.addItem(p["description"])
        self.list.setCurrentRow(0)
        layout.addWidget(self.list)

        # Buttons
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def to_tool(self) -> Tool:
        idx = self.list.currentRow()
        p = PRESETS[idx]
        d = p["diameter"]
        return Tool(
            id=p["id"],
            type=p["type"],
            diameter_mm=d,
            flute_length_mm=d * 2.2,
            overall_length_mm=83.0,
            shank_diameter_mm=d,
            material=p["material"],
            num_flutes=p["num_flutes"],
            max_rpm=p["max_rpm"],
            max_feedrate_mmmin=3000.0,
            tool_number=int(p["id"][1]),
            description=p["description"],
        )


class CncmSelectTool:
    def GetResources(self):
        return {
            "MenuText": "Select Tool",
            "ToolTip": "Select cutting tool from preset library",
            "Accel": "Ctrl+T",
            "Pixmap": "",
        }

    def Activated(self):
        dlg = ToolDialog(FreeCADGui.getMainWindow())
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            tool = dlg.to_tool()
            session.set_tool(tool)
            FreeCAD.Console.PrintMessage(
                f"Selected tool: {tool.id} ({tool.description})\n"
            )

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None