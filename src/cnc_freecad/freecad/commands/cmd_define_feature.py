"""
Command: Define a pocket feature manually via dialog.
"""
import FreeCAD
import FreeCADGui
from PySide6 import QtCore, QtGui, QtWidgets

from cnc_freecad.data.models import BoundingBox, Feature, FeatureType
from cnc_freecad.freecad.session import session


class FeatureDialog(QtWidgets.QDialog):
    """Dialog to manually define a rectangular pocket feature."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Define Pocket Feature")
        self.setMinimumWidth(360)

        layout = QtWidgets.QFormLayout()

        # Feature ID
        self.id_input = QtWidgets.QLineEdit(f"pocket_{session.next_feature_index():03d}")
        layout.addRow("Feature ID:", self.id_input)

        # Dimensions
        self.width_input = QtWidgets.QDoubleSpinBox()
        self.width_input.setRange(1.0, 1000.0)
        self.width_input.setValue(80.0)
        self.width_input.setSuffix(" mm")
        layout.addRow("Width (X):", self.width_input)

        self.depth_input = QtWidgets.QDoubleSpinBox()
        self.depth_input.setRange(1.0, 1000.0)
        self.depth_input.setValue(80.0)
        self.depth_input.setSuffix(" mm")
        layout.addRow("Depth (Y):", self.depth_input)

        self.pocket_depth_input = QtWidgets.QDoubleSpinBox()
        self.pocket_depth_input.setRange(0.1, 100.0)
        self.pocket_depth_input.setValue(15.0)
        self.pocket_depth_input.setSuffix(" mm")
        layout.addRow("Pocket Depth (Z):", self.pocket_depth_input)

        # Allowance
        self.allowance_input = QtWidgets.QDoubleSpinBox()
        self.allowance_input.setRange(0.0, 5.0)
        self.allowance_input.setValue(0.5)
        self.allowance_input.setSingleStep(0.1)
        self.allowance_input.setSuffix(" mm")
        layout.addRow("Stock to leave:", self.allowance_input)

        # Buttons
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        self.setLayout(layout)

    def to_feature(self) -> Feature:
        """Build a Feature from current dialog values."""
        w = self.width_input.value()
        d = self.depth_input.value()
        z = self.pocket_depth_input.value()
        return Feature(
            id=self.id_input.text(),
            type=FeatureType.POCKET,
            depth_mm=z,
            bounding_box=BoundingBox(
                x_min=-w / 2, x_max=w / 2,
                y_min=-d / 2, y_max=d / 2,
                z_min=-z, z_max=0.0,
            ),
            bottom_z=-z,
            top_z=0.0,
            material_allowance_mm=self.allowance_input.value(),
            priority=1,
        )


class CncmDefineFeature:
    """Define a pocket feature (opens dialog, stores in session)."""

    def GetResources(self):
        return {
            "MenuText": "Define Feature",
            "ToolTip": "Manually define a pocket feature for machining",
            "Accel": "Ctrl+F",
            "Pixmap": "",
        }

    def Activated(self):
        dlg = FeatureDialog(FreeCADGui.getMainWindow())
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            feature = dlg.to_feature()
            session.add_feature(feature)
            FreeCAD.Console.PrintMessage(
                f"Defined feature: {feature.id} "
                f"({feature.bounding_box.width_x:.1f} x {feature.bounding_box.width_y:.1f} x {feature.depth_mm:.1f} mm)\n"
            )

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None