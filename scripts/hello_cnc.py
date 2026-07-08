"""
scripts/hello_cnc.py - M0 Demo: simplest FreeCAD macro

Demonstrates:
1. Create a FreeCAD document
2. Build a part (box with a hole) via Part Module
3. Save as STEP
4. Reload and verify

Run:
  /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd scripts/hello_cnc.py
"""
import os
import sys

# Make project src importable
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))

import FreeCAD
import Part


def main():
    print("=" * 50)
    print("CNC AutoCAM - Hello CNC Demo (M0)")
    print("=" * 50)

    # 1. Create document
    doc = FreeCAD.newDocument("CNC_Demo")
    print(f"[1/4] Created FreeCAD document: {doc.Name}")

    # 2. Create a part body: box with a hole
    box = doc.addObject("Part::Box", "DemoPart")
    box.Length = 100.0
    box.Width = 80.0
    box.Height = 20.0
    doc.recompute()
    print(f"[2/4] Created Part::Box: {box.Length} x {box.Width} x {box.Height}")

    cylinder = doc.addObject("Part::Cylinder", "DemoHole")
    cylinder.Radius = 6.0
    cylinder.Height = 25.0
    cylinder.Placement.Base = (50.0, 40.0, -2.0)
    doc.recompute()
    print(f"[3/4] Created Part::Cylinder (drill hole): R={cylinder.Radius}, depth={cylinder.Height}")

    cut = doc.addObject("Part::Cut", "DemoPartWithHole")
    cut.Base = box
    cut.Tool = cylinder
    doc.recompute()

    # 验证几何
    shape = cut.Shape
    print(f"[4/4] Boolean cut: Volume={shape.Volume:.2f} (expected ~{100*80*20 - 3.14159*6**2*20:.2f})")

    # 5. Save as STEP
    output_dir = os.path.join(PROJECT_ROOT, "examples")
    os.makedirs(output_dir, exist_ok=True)
    step_path = os.path.join(output_dir, "demo_part.step")
    Part.export([cut], step_path)
    print(f"[SAVE] Exported to: {os.path.basename(output_dir)}/{os.path.basename(step_path)}")

    # 6. Reload STEP to verify (use Part.insert for headless)
    doc2 = FreeCAD.newDocument("CNC_Demo_Verify")
    Part.insert(step_path, doc2.Name)
    doc2.recompute()
    loaded = doc2.ActiveObject.Shape
    print(f"[VERIFY] Reloaded shape: Volume={loaded.Volume:.2f}")

    # Clean up
    FreeCAD.closeDocument(doc.Name)
    FreeCAD.closeDocument(doc2.Name)

    print("=" * 50)
    print("[OK] Hello CNC demo completed successfully!")
    print("=" * 50)
    return 0


if __name__ == "__main__":
    sys.exit(main())