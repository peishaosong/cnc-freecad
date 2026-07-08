"""
M1 end-to-end test: manually defined pocket -> toolpath -> G-code.

This is the minimum-viable loop:
  1. Define a pocket Feature by hand (no auto recognition yet)
  2. Define a Tool + ProcessTemplate
  3. Run ToolpathGenerator.rough_parallel
  4. Run PostProcessor (Fanuc)
  5. Write G-code to output.nc
  6. Validate G-code (must contain key instructions)
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

PASSED = 0
FAILED = 0


def check(name: str, condition: bool, detail: str = ""):
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
    print("M1 Minimum Closed Loop Test", flush=True)
    print("=" * 50, flush=True)

    from cnc_freecad.data.models import (
        BoundingBox,
        Feature,
        FeatureType,
        Operation,
        ProcessPlan,
        ProcessTemplate,
        Material,
        MaterialCategory,
        Tool,
        ToolMaterial,
        ToolType,
        Strategy,
    )
    from cnc_freecad.core.toolpath_generator import ToolpathGenerator
    from cnc_freecad.core.postprocessor import PostProcessor
    from cnc_freecad.core.engine import CNCEngine

    # --- 1. Define entities ---
    bb = BoundingBox(
        x_min=10.0, x_max=90.0,
        y_min=10.0, y_max=90.0,
        z_min=-15.0, z_max=0.0,
    )
    feature = Feature(
        id="pocket_001",
        type=FeatureType.POCKET,
        depth_mm=15.0,
        bounding_box=bb,
        bottom_z=-15.0,
        top_z=0.0,
        material_allowance_mm=0.5,
        priority=1,
    )

    material = Material(
        id="6061_t6_al",
        name="6061-T6 Aluminum",
        category=MaterialCategory.ALUMINUM,
        hardness_hrc=20.0,
        density_gcc=2.7,
        tensile_strength_mpa=310.0,
        is_soft=True,
    )

    tool = Tool(
        id="T1_d12_flat",
        type=ToolType.FLAT_ENDMILL,
        diameter_mm=12.0,
        flute_length_mm=26.0,
        overall_length_mm=83.0,
        shank_diameter_mm=12.0,
        material=ToolMaterial.CARBIDE,
        num_flutes=4,
        max_rpm=15000,
        max_feedrate_mmmin=3000.0,
        tool_number=1,
        description="12mm carbide flat endmill",
    )

    template = ProcessTemplate(
        id="rough_parallel_d12_al",
        tool_id=tool.id,
        material_category=MaterialCategory.ALUMINUM,
        strategy=Strategy.ROUGH_PARALLEL,
        spindle_rpm=8000,
        feedrate_mmmin=1500,
        depth_of_cut_mm=2.0,
        width_of_cut_mm=7.2,  # 60% diameter
        coolant=True,
    )

    print("[1/4] Defined entities: pocket, tool, template", flush=True)

    # --- 2. Generate toolpath ---
    generator = ToolpathGenerator()
    toolpath = generator.generate(feature, template, tool)
    check("Toolpath generated", len(toolpath.segments) > 0,
          f"got {len(toolpath.segments)} segments")
    check("Toolpath has feed segments",
          any(s.motion_type.value == "feed" for s in toolpath.segments),
          "no feed segments found")
    check("Toolpath has rapid segments",
          any(s.motion_type.value == "rapid" for s in toolpath.segments),
          "no rapid segments found")
    print(f"[2/4] Toolpath: {len(toolpath.segments)} segments", flush=True)

    # --- 3. Post-process ---
    pp = PostProcessor(machine="fanuc")
    gcode = pp.process([toolpath], part_name="test_pocket")
    check("G-code non-empty", len(gcode) > 100, f"only {len(gcode)} chars")
    check("G-code has program start (%)", "%" in gcode, "no % found")
    check("G-code has G21 (mm)", "G21" in gcode, "no G21")
    check("G-code has G17 (XY plane)", "G17" in gcode, "no G17")
    check("G-code has spindle S8000", "S8000" in gcode, "no S8000")
    check("G-code has M6 (tool change)", "M6" in gcode, "no M6")
    check("G-code has M30 (end)", "M30" in gcode, "no M30")
    check("G-code has G0 rapid", "G0 " in gcode, "no G0 ")
    check("G-code has G1 feed", "G1 " in gcode, "no G1 ")
    print(f"[3/4] G-code: {len(gcode)} chars, {gcode.count(chr(10))} lines", flush=True)

    # --- 4. Write output ---
    out_path = os.path.join(os.path.dirname(__file__), "..", "examples", "test_m1_pocket.nc")
    out_path = os.path.abspath(out_path)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        f.write(gcode)
    check(f"G-code written to {os.path.basename(out_path)}",
          os.path.exists(out_path), f"missing: {out_path}")
    check("File size > 1KB", os.path.getsize(out_path) > 1024,
          f"only {os.path.getsize(out_path)} bytes")

    # --- 5. Full engine test ---
    plan = ProcessPlan(
        part_name="engine_test",
        material=material,
        operations=[
            Operation(
                feature_id="pocket_001",
                template=template,
                tool=tool,
                sequence=1,
            )
        ],
    )
    engine = CNCEngine()
    tps = engine.generate_toolpaths(plan, features={feature.id: feature})
    check("Engine returns toolpaths", len(tps) == 1, f"got {len(tps)}")
    gcode2 = engine.postprocess(tps, machine="fanuc")
    check("Engine G-code non-empty", len(gcode2) > 100, "")
    print(f"[4/4] Engine end-to-end OK", flush=True)

    print("=" * 50, flush=True)
    print(f"Result: {PASSED} passed, {FAILED} failed", flush=True)
    print("=" * 50, flush=True)
    if FAILED == 0:
        print("[SUCCESS] M1 minimum loop verified.", flush=True)
        return 0
    print("[FAILED] M1 verification failed.", flush=True)
    return 1


if __name__ == "__main__":
    sys.exit(run_all())