"""
Post-processing: convert Toolpath objects into G-code for a specific machine.

M1 scope: Fanuc-compatible G-code (covers most 3-axis CNC mills).
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from cnc_freecad.data.models import (
    MotionType,
    Point3D,
    Toolpath,
    ToolpathSegment,
)


class PostProcessor:
    """Convert Toolpath list to G-code string."""

    def __init__(self, machine: str = "fanuc"):
        if machine != "fanuc":
            raise NotImplementedError(f"Machine {machine} not implemented yet (M1: fanuc only)")
        self.machine = machine

    def process(
        self,
        toolpaths: List[Toolpath],
        part_name: str = "CNC_PART",
        include_comments: bool = True,
    ) -> str:
        lines: List[str] = []
        c = include_comments

        if c:
            lines.append("%")
            lines.append(f"({part_name})")
            lines.append(f"(Fanuc post processor v0.1.0)")
            lines.append(f"(Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
            lines.append("")

        # Init
        lines.append("G17 G40 G49 G80 G90")
        lines.append("G21 (mm)")

        prev_tool_id: Optional[str] = None
        for tp in toolpaths:
            tool_id = tp.tool_id

            # Tool change if needed
            if tool_id != prev_tool_id:
                tool_number = self._tool_number(tool_id)
                lines.append("")
                if c:
                    lines.append(f"(Tool change: {tool_id})")
                lines.append(f"T{tool_number} M6")

            # Spindle on (set once per tool, take from first segment)
            rpm = tp.segments[0].spindle_rpm if tp.segments else 0
            lines.append(f"S{rpm} M3")

            # Work coord
            lines.append("G54")
            if c:
                lines.append(f"(Feature: {tp.feature_id})")
                lines.append(f"(Strategy: {tp.strategy.value})")

            for seg in tp.segments:
                lines.extend(self._segment_to_gcode(seg, c))

            lines.append("M5 (Spindle stop)")
            prev_tool_id = tool_id

        # End
        lines.append("")
        lines.append("M30 (Program end)")
        if c:
            lines.append("%")
        return "\n".join(lines) + "\n"

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    def _segment_to_gcode(self, seg: ToolpathSegment, comments: bool) -> List[str]:
        lines: List[str] = []
        if comments and seg.coolant_on:
            pass  # coolant handled per-tool for simplicity

        if seg.motion_type == MotionType.RAPID:
            if len(seg.points) == 1:
                p = seg.points[0]
                lines.append(f"G0 X{p.x:.3f} Y{p.y:.3f} Z{p.z:.3f}")
            else:
                # Multi-point rapid (traverse): emit one line per point except start
                for p in seg.points[1:]:
                    lines.append(f"G0 X{p.x:.3f} Y{p.y:.3f} Z{p.z:.3f}")

        elif seg.motion_type == MotionType.FEED:
            if len(seg.points) >= 2:
                feed = seg.feedrate_mmmin
                # First point sets position
                lines.append(f"G1 X{seg.points[0].x:.3f} Y{seg.points[0].y:.3f} Z{seg.points[0].z:.3f} F{feed:.0f}")
                # Subsequent points feed
                for p in seg.points[1:]:
                    lines.append(f"G1 X{p.x:.3f} Y{p.y:.3f} Z{p.z:.3f}")

        elif seg.motion_type == MotionType.ARC:
            for arc in seg.arc_points:
                cw = "G02" if arc.clockwise else "G03"
                # I/J = center - start
                i = arc.center.x - arc.start.x
                j = arc.center.y - arc.start.y
                lines.append(
                    f"{cw} X{arc.end.x:.3f} Y{arc.end.y:.3f} "
                    f"I{i:.3f} J{j:.3f} F{seg.feedrate_mmmin:.0f}"
                )
        return lines

    @staticmethod
    def _tool_number(tool_id: str) -> int:
        """Extract T-number from tool id, fallback to 1."""
        # Convention: tool IDs like "T1_d12_carbide" or "d12_carbide" -> 1
        if tool_id.upper().startswith("T"):
            num_str = ""
            for ch in tool_id[1:]:
                if ch.isdigit():
                    num_str += ch
                else:
                    break
            if num_str:
                return int(num_str)
        # Hash-based fallback for deterministic numbering
        return (abs(hash(tool_id)) % 20) + 1