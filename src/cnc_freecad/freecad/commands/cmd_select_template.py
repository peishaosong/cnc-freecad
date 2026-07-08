"""
Command: Select process template via dialog (rough/finish presets).
"""
import FreeCAD
import FreeCADGui
from PySide6 import QtWidgets

from cnc_freecad.data.models import (
    MaterialCategory,
    ProcessTemplate,
    Strategy,
)
from cnc_freecad.freecad.session import session


# Preset templates for aluminum (M1 scope)
PRESETS = [
    {
        "name": "Aluminum Roughing (Parallel, D12)",
        "strategy": Strategy.ROUGH_PARALLEL,
        "spindle_rpm": 8000,
        "feedrate": 1500,
        "doc": 2.0,
        "woc": 7.2,
        "coolant": True,
    },
    {
        "name": "Aluminum Finishing (Contour, D12)",
        "strategy": Strategy.FINISH_CONTOUR,
        "spindle_rpm": 10000,
        "feedrate": 1200,
        "doc": 0.5,
        "woc": 6.0,
        "coolant": True,
    },
    {
        "name": "Aluminum Roughing (Parallel, D8)",
        "strategy": Strategy.ROUGH_PARALLEL,
        "spindle_rpm": 10000,
        "feedrate": 1200,
        "doc": 1.5,
        "woc": 4.8,
        "coolant": True,
    },
]


class TemplateDialog(QtWidgets.QDialog):
    """Dialog to select process template."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Process Template")
        self.setMinimumWidth(400)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(QtWidgets.QLabel("Select a process template:"))

        self.list = QtWidgets.QListWidget()
        for p in PRESETS:
            self.list.addItem(p["name"])
        self.list.setCurrentRow(0)
        layout.addWidget(self.list)

        # Material category
        form = QtWidgets.QFormLayout()
        self.material_combo = QtWidgets.QComboBox()
        for cat in MaterialCategory:
            self.material_combo.addItem(cat.value)
        self.material_combo.setCurrentText(MaterialCategory.ALUMINUM.value)
        form.addRow("Material:", self.material_combo)
        layout.addLayout(form)

        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def to_template(self) -> ProcessTemplate:
        idx = self.list.currentRow()
        p = PRESETS[idx]
        tool = session.tool
        if tool is None:
            raise RuntimeError("Select a tool first (Ctrl+T)")
        return ProcessTemplate(
            id=p["name"].lower().replace(" ", "_"),
            tool_id=tool.id,
            material_category=MaterialCategory(self.material_combo.currentText()),
            strategy=p["strategy"],
            spindle_rpm=p["spindle_rpm"],
            feedrate_mmmin=p["feedrate"],
            depth_of_cut_mm=p["doc"],
            width_of_cut_mm=p["woc"],
            coolant=p["coolant"],
        )


class CncmSelectTemplate:
    def GetResources(self):
        return {
            "MenuText": "Select Template",
            "ToolTip": "Select process template (cutting parameters)",
            "Accel": "Ctrl+M",
            "Pixmap": "",
        }

    def Activated(self):
        if session.tool is None:
            QtWidgets.QMessageBox.warning(
                None, "No Tool",
                "Please select a tool first (CNC AutoCAM > Select Tool)"
            )
            return
        dlg = TemplateDialog(FreeCADGui.getMainWindow())
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            template = dlg.to_template()
            session.set_template(template)
            FreeCAD.Console.PrintMessage(
                f"Selected template: {template.id}\n"
                f"  RPM={template.spindle_rpm}, Feed={template.feedrate_mmmin} mm/min\n"
                f"  Doc={template.depth_of_cut_mm}, Woc={template.width_of_cut_mm}\n"
            )

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None