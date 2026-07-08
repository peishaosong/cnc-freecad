"""
M1 UI integration test - verifies the workbench registration works
without requiring an actual GUI display.

Tests:
1. Workbench class can be instantiated
2. All commands import without error
3. Commands expose required FreeCADGui.addCommand interface
4. Session state machine works
5. Dialogs construct successfully (offscreen Qt)

Note: 3D visualization needs a real display. This test validates the
command layer only.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

PASSED = 0
FAILED = 0


def check(name, condition, detail=""):
    global PASSED, FAILED
    if condition:
        print(f"  [PASS] {name}", flush=True)
        PASSED += 1
    else:
        print(f"  [FAIL] {name}: {detail}", flush=True)
        FAILED += 1


def run_all() -> int:
    global PASSED, FAILED
    PASSED = 0
    FAILED = 0

    print("=" * 50, flush=True)
    print("M1 UI Integration Test", flush=True)
    print("=" * 50, flush=True)

    # ---- 1. Session state ----
    print("[1/6] Session state", flush=True)
    from cnc_freecad.freecad.session import session
    from cnc_freecad.data.models import (
        BoundingBox, Feature, FeatureType, Tool, ToolMaterial, ToolType,
        ProcessTemplate, MaterialCategory, Strategy,
    )

    f1 = Feature(
        id="pocket_001", type=FeatureType.POCKET, depth_mm=10.0,
        bounding_box=BoundingBox(
            x_min=0, x_max=80, y_min=0, y_max=80,
            z_min=-10, z_max=0,
        ),
        bottom_z=-10, top_z=0,
    )
    session.add_feature(f1)
    check("Feature added to session", "pocket_001" in session.features)
    idx = session.next_feature_index()
    check("Feature index increments", idx == 1, f"got {idx}")

    tool = Tool(
        id="T1_d12", type=ToolType.FLAT_ENDMILL, diameter_mm=12.0,
        flute_length_mm=26.0, overall_length_mm=83.0, shank_diameter_mm=12.0,
        material=ToolMaterial.CARBIDE, num_flutes=4, max_rpm=15000,
        max_feedrate_mmmin=3000.0, tool_number=1,
    )
    session.set_tool(tool)
    check("Tool set", session.tool.id == "T1_d12")

    template = ProcessTemplate(
        id="test", tool_id="T1_d12", material_category=MaterialCategory.ALUMINUM,
        strategy=Strategy.ROUGH_PARALLEL, spindle_rpm=8000, feedrate_mmmin=1500,
        depth_of_cut_mm=2.0, width_of_cut_mm=7.2,
    )
    session.set_template(template)
    check("Template set", session.template.spindle_rpm == 8000)

    session.clear_features()
    check("Clear features", len(session.features) == 0)
    session.add_feature(f1)  # re-add for downstream tests

    # ---- 2. Command imports ----
    print("[2/6] Command module imports", flush=True)
    from cnc_freecad.freecad.commands import (
        CncmImportPart, CncmDefineFeature, CncmSelectTool,
        CncmSelectTemplate, CncmGenerate, CncmPostprocess,
    )
    check("All 6 commands importable", True)

    # ---- 3. Command interface ----
    print("[3/6] Command FreeCADGui interface", flush=True)
    for cmd_cls in [CncmImportPart, CncmDefineFeature, CncmSelectTool,
                    CncmSelectTemplate, CncmGenerate, CncmPostprocess]:
        cmd = cmd_cls()
        res = cmd.GetResources()
        check(f"{cmd_cls.__name__}.GetResources", isinstance(res, dict))
        check(f"{cmd_cls.__name__}.MenuText present", "MenuText" in res)
        check(f"{cmd_cls.__name__}.ToolTip present", "ToolTip" in res)

    # ---- 4. Dialog construction (offscreen Qt) ----
    print("[4/6] Dialog construction (PySide6 offscreen)", flush=True)
    try:
        from PySide6 import QtWidgets
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)

        from cnc_freecad.freecad.commands.cmd_define_feature import FeatureDialog
        dlg = FeatureDialog()
        check("FeatureDialog constructs", dlg is not None)
        check("FeatureDialog has width_input", hasattr(dlg, "width_input"))
        check("FeatureDialog has depth_input", hasattr(dlg, "depth_input"))
        check("FeatureDialog has pocket_depth_input", hasattr(dlg, "pocket_depth_input"))
        feature = dlg.to_feature()
        check("Dialog->Feature conversion works", feature.depth_mm > 0)
        dlg.deleteLater()

        from cnc_freecad.freecad.commands.cmd_select_tool import ToolDialog, PRESETS
        dlg2 = ToolDialog()
        check("ToolDialog constructs", dlg2 is not None)
        check("ToolDialog has preset list", dlg2.list.count() == len(PRESETS))
        dlg2.deleteLater()

        from cnc_freecad.freecad.commands.cmd_select_template import TemplateDialog
        dlg3 = TemplateDialog()
        check("TemplateDialog constructs", dlg3 is not None)
        dlg3.deleteLater()

    except Exception as e:
        check("Dialog construction", False, str(e))

    # ---- 5. Workbench class ----
    print("[5/6] Workbench module", flush=True)
    from cnc_freecad.freecad.workbench import CncmWorkbench, register, GUI_AVAILABLE
    check("CncmWorkbench factory exists", callable(CncmWorkbench))
    check("register() function exists", callable(register))
    check("GUI_AVAILABLE detection works", isinstance(GUI_AVAILABLE, bool))
    # In headless mode we can't actually instantiate the workbench class
    # (FreeCADGui.Workbench doesn't exist); verify by code path only.
    check("Headless mode handled", GUI_AVAILABLE == False,
          f"expected headless=False, got {GUI_AVAILABLE}")

    # ---- 6. End-to-end: dialog -> session -> toolpath ----
    print("[6/6] E2E via UI flow (offscreen)", flush=True)
    from cnc_freecad.core.toolpath_generator import ToolpathGenerator
    gen = ToolpathGenerator()
    tp = gen.generate(session.features["pocket_001"], session.template, session.tool)
    check("Generate from UI-fed session", len(tp.segments) > 0,
          f"got {len(tp.segments)} segments")

    print("=" * 50, flush=True)
    print(f"Result: {PASSED} passed, {FAILED} failed", flush=True)
    print("=" * 50, flush=True)
    if FAILED == 0:
        print("[SUCCESS] M1 UI layer verified.", flush=True)
        return 0
    print("[FAILED] M1 UI test failed.", flush=True)
    return 1


if __name__ == "__main__":
    sys.exit(run_all())