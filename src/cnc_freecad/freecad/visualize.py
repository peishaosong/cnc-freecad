"""
Convert cnc_freecad Toolpath objects to FreeCAD Path objects for 3D visualization.

M1: use FreeCAD Path workbench's Path::FeatureCompound or wire points as Part::Line.
"""
from __future__ import annotations

import FreeCAD
from PySide6 import QtCore

from cnc_freecad.data.models import MotionType, Toolpath


# Color map by motion type (RGB tuple 0..1)
COLOR_RAPID = (1.0, 0.5, 0.0)      # orange
COLOR_FEED = (0.0, 0.6, 1.0)        # blue
COLOR_ARC = (0.0, 0.85, 0.0)        # green
COLOR_PLUNGE = (1.0, 0.0, 0.0)      # red


def display_toolpath(toolpaths, strategy=None):
    """Add toolpath as a visible FreeCAD object in the 3D view.

    Strategy: build one wire per ToolpathSegment, colored by motion type.
    """
    if not toolpaths:
        FreeCAD.Console.PrintWarning("No toolpath to display\n")
        return

    import Part

    doc = FreeCAD.ActiveDocument

    # Remove old CNCM toolpath objects first
    for obj in list(doc.Objects):
        if obj.Name.startswith("CNCM_Toolpath"):
            doc.removeObject(obj.Name)

    for tp_idx, tp in enumerate(toolpaths):
        wires = []  # group of wires for this toolpath

        for seg_idx, seg in enumerate(tp.segments):
            if seg.motion_type == MotionType.RAPID:
                color = COLOR_RAPID
            elif seg.motion_type == MotionType.FEED:
                color = COLOR_FEED
            else:
                color = COLOR_ARC

            pts = [FreeCAD.Vector(p.x, p.y, p.z) for p in seg.points]
            if len(pts) < 2:
                continue

            # Build polyline as edges
            edges = []
            for i in range(len(pts) - 1):
                edge = Part.makeLine(pts[i], pts[i + 1])
                edges.append(edge)

            # Add to a single Compound for visualization
            wire = Part.Wire(edges)
            wires.append((wire, color))

        # Create a single Part::Feature for the whole toolpath
        compound = Part.makeCompound([w for w, _ in wires])
        obj = doc.addObject("Part::Feature", f"CNCM_Toolpath_{tp.id}")
        obj.Shape = compound

        # Set color line by line via ViewProvider
        vp = obj.ViewObject
        if hasattr(vp, "LineColor"):
            # Set a default color (first segment color)
            if wires:
                r, g, b = wires[0][1]
                vp.LineColor = (r, g, b)
        if hasattr(vp, "LineWidth"):
            vp.LineWidth = 2

    doc.recompute()
    FreeCAD.Console.PrintMessage(
        f"Displayed {len(toolpaths)} toolpath(s) in 3D view (rapid=orange, feed=blue)\n"
    )