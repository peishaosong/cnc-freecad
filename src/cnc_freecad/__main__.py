"""
CNC AutoCAM CLI entry point.

Usage examples:
  python -m cnc_freecad info
  python -m cnc_freecad run-pocket --width 80 --depth 80 --pocket-depth 15 --output pocket.nc
"""
from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from cnc_freecad import __version__
from cnc_freecad.data.models import (
    BoundingBox,
    Feature,
    FeatureType,
    Material,
    MaterialCategory,
    Operation,
    ProcessPlan,
    ProcessTemplate,
    Strategy,
    Tool,
    ToolMaterial,
    ToolType,
)
from cnc_freecad.core.engine import CNCEngine


def cmd_info(_args) -> int:
    print(f"CNC AutoCAM v{__version__}")
    print(f"Python: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    try:
        import FreeCAD
        print(f"FreeCAD: {FreeCAD.Version()[0]}.{FreeCAD.Version()[1]}.{FreeCAD.Version()[2]}")
    except ImportError:
        print("FreeCAD: not installed")
    return 0


def cmd_run_pocket(args) -> int:
    """Generate G-code for a single rectangular pocket (M1 demo)."""
    # Pocket is centered on the origin
    half_x = args.width / 2
    half_y = args.depth / 2
    bb = BoundingBox(
        x_min=-half_x, x_max=half_x,
        y_min=-half_y, y_max=half_y,
        z_min=-args.pocket_depth, z_max=0.0,
    )
    feature = Feature(
        id="pocket_001",
        type=FeatureType.POCKET,
        depth_mm=args.pocket_depth,
        bounding_box=bb,
        bottom_z=-args.pocket_depth,
        top_z=0.0,
        material_allowance_mm=0.5,
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
        id=f"T1_d{args.tool_diameter}_flat",
        type=ToolType.FLAT_ENDMILL,
        diameter_mm=args.tool_diameter,
        flute_length_mm=args.tool_diameter * 2.2,
        overall_length_mm=83.0,
        shank_diameter_mm=args.tool_diameter,
        material=ToolMaterial.CARBIDE,
        num_flutes=4,
        max_rpm=15000,
        max_feedrate_mmmin=3000.0,
        tool_number=1,
    )
    template = ProcessTemplate(
        id="rough_parallel_d12_al",
        tool_id=tool.id,
        material_category=MaterialCategory.ALUMINUM,
        strategy=Strategy.ROUGH_PARALLEL,
        spindle_rpm=args.rpm,
        feedrate_mmmin=args.feed,
        depth_of_cut_mm=args.doc,
        width_of_cut_mm=args.tool_diameter * 0.6,
    )
    plan = ProcessPlan(
        part_name=args.part_name,
        material=material,
        operations=[
            Operation(feature_id=feature.id, template=template, tool=tool, sequence=1)
        ],
    )
    engine = CNCEngine()
    toolpaths = engine.generate_toolpaths(plan, features={feature.id: feature})
    gcode = engine.postprocess(toolpaths, machine=args.machine)

    if args.output:
        with open(args.output, "w") as f:
            f.write(gcode)
        print(f"[OK] G-code written to: {args.output} ({len(gcode)} chars)")
    else:
        print(gcode)
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="cnc-freecad",
        description="CNC AutoCAM - automatic programming for CNC mills",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("info", help="Show version and environment info")

    p_run = sub.add_parser("run-pocket", help="Generate G-code for a rectangular pocket")
    p_run.add_argument("--width", type=float, default=80.0, help="Pocket width in mm (X)")
    p_run.add_argument("--depth", type=float, default=80.0, help="Pocket depth in mm (Y)")
    p_run.add_argument("--pocket-depth", type=float, default=15.0, help="Pocket depth in mm (Z, below origin)")
    p_run.add_argument("--tool-diameter", type=float, default=12.0, help="End mill diameter in mm")
    p_run.add_argument("--rpm", type=int, default=8000, help="Spindle RPM")
    p_run.add_argument("--feed", type=float, default=1500.0, help="Feed rate mm/min")
    p_run.add_argument("--doc", type=float, default=2.0, help="Depth of cut per pass mm")
    p_run.add_argument("--machine", default="fanuc", help="Post processor (default fanuc)")
    p_run.add_argument("--part-name", default="pocket_demo", help="Part name")
    p_run.add_argument("-o", "--output", help="Output file path (.nc)")

    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 1

    if args.command == "info":
        return cmd_info(args)
    elif args.command == "run-pocket":
        return cmd_run_pocket(args)
    return 1


if __name__ == "__main__":
    sys.exit(main())