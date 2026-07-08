import sys
import os

print("1. Start", flush=True)
print(f"   cwd: {os.getcwd()}", flush=True)

from PySide6 import QtCore, QtWidgets
print(f"2. PySide6 OK: {QtCore.__version__}", flush=True)

app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
print("3. QApplication OK", flush=True)

w = QtWidgets.QMainWindow()
w.setWindowTitle("Test")
w.resize(400, 300)
print("4. QMainWindow OK", flush=True)

# Test FreeCADGui
import FreeCAD
print(f"5. FreeCAD {FreeCAD.Version()[0]}.{FreeCAD.Version()[1]} OK", flush=True)

import FreeCADGui
print("6. FreeCADGui OK", flush=True)

# Test Workbench
class TestWB(FreeCADGui.Workbench):
    MenuText = "Test WB"
    ToolTip = "Testing"

wb = TestWB()
print(f"7. Workbench: {wb.MenuText}", flush=True)

# Test that we can register commands
class TestCmd:
    def GetResources(self):
        return {"MenuText": "Test Cmd"}
    def Activated(self):
        pass

cmd = TestCmd()
res = cmd.GetResources()
print(f"8. Command: {res['MenuText']}", flush=True)

print("=" * 40, flush=True)
print("All GUI tests passed.", flush=True)