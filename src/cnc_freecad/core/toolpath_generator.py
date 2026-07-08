"""
Toolpath generation - converts features + process templates into concrete motion.

M1 scope: rough_parallel strategy only.
"""
from __future__ import annotations

import math
from typing import List

from cnc_freecad.data.models import (
    Feature,
    Point3D,
    ProcessPlan,
    ProcessTemplate,
    Tool,
    Toolpath,
    ToolpathSegment,
    MotionType,
)


class ToolpathGenerator:
    """Generate toolpaths from features and process templates."""

    def generate(
        self,
        feature: Feature,
        template: ProcessTemplate,
        tool: Tool,
    ) -> Toolpath:
        """Dispatch to the strategy-specific generator."""
        if template.strategy.value == "rough_parallel":
            return self._generate_rough_parallel(feature, template, tool)
        raise ValueError(f"Strategy {template.strategy} not implemented yet (M1 only supports rough_parallel)")

    # ------------------------------------------------------------------
    # rough_parallel: outside-in or inside-out zigzag parallel passes
    # ------------------------------------------------------------------

    def _generate_rough_parallel(
        self,
        feature: Feature,
        template: ProcessTemplate,
        tool: Tool,
    ) -> Toolpath:
        bb = feature.bounding_box
        tool_r = tool.diameter_mm / 2
        retract_z = bb.z_max + template.lead_out_mm

        # Offset pocket boundary by tool radius (inward for closed pockets)
        width_x = bb.width_x - tool_r * 2
        width_y = bb.width_y - tool_r * 2
        if width_x <= 0 or width_y <= 0:
            raise ValueError(f"Pocket too small for tool diameter {tool.diameter_mm}")

        # Number of passes (round up)
        stepover = max(template.width_of_cut_mm, tool.diameter_mm * 0.4)
        num_passes = max(1, math.ceil(width_y / stepover))
        actual_stepover = width_y / num_passes

        # Depth passes
        z_top = bb.z_max
        z_target = bb.z_min + feature.material_allowance_mm
        depth_per_pass = template.depth_of_cut_mm
        z_starts: List[float] = [z for z in self._depth_passes(z_top, z_target, depth_per_pass)]

        segments: List[ToolpathSegment] = []

        # Pre-position to safe Z above first start point
        first_start = Point3D(
            x=bb.x_min + tool_r,
            y=bb.y_min + tool_r,
            z=z_starts[0],
        )
        segments.append(self._rapid_to(first_start.x, first_start.y, retract_z, template))

        for z in z_starts:
            # Helical/ramp entry on the first pass of each depth
            segments.extend(self._ramp_entry(first_start, z_top, z, template))

            for i in range(num_passes):
                y = bb.y_min + tool_r + i * actual_stepover + actual_stepover / 2
                forward = (i % 2 == 0)
                x_start = bb.x_min + tool_r
                x_end = bb.x_max - tool_r

                p1 = Point3D(x=x_start, y=y, z=z)
                p2 = Point3D(x=x_end, y=y, z=z)

                # Feed across
                segments.append(self._feed(p1, p2, template))

                # Rapid retract + lateral move to next pass (except after last)
                if i < num_passes - 1:
                    next_y = bb.y_min + tool_r + (i + 1) * actual_stepover + actual_stepover / 2
                    next_x = x_end if forward else x_start
                    segments.append(self._rapid_to(next_x, y, retract_z, template))
                    segments.append(self._rapid_to(next_x, next_y, retract_z, template))

            # After final pass at this depth, retract
            segments.append(self._rapid_to(x_end, bb.y_min + tool_r, retract_z, template))

        # Final retract to safe Z
        segments.append(self._rapid_to(first_start.x, first_start.y, retract_z, template))

        return Toolpath(
            id=f"tp_{feature.id}_{template.strategy.value}",
            feature_id=feature.id,
            tool_id=tool.id,
            strategy=template.strategy,
            segments=segments,
        )

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    def _depth_passes(self, z_top: float, z_target: float, depth_per_pass: float):
        """Yield z-levels for each depth pass, from top down."""
        z = z_top
        while z > z_target + 1e-6:
            z_next = max(z - depth_per_pass, z_target)
            yield z_next
            z = z_next

    def _rapid_to(self, x: float, y: float, z: float, template: ProcessTemplate) -> ToolpathSegment:
        return ToolpathSegment(
            points=[Point3D(x=x, y=y, z=z)],
            motion_type=MotionType.RAPID,
            feedrate_mmmin=0,
            spindle_rpm=template.spindle_rpm,
        )

    def _feed(self, p1: Point3D, p2: Point3D, template: ProcessTemplate) -> ToolpathSegment:
        return ToolpathSegment(
            points=[p1, p2],
            motion_type=MotionType.FEED,
            feedrate_mmmin=template.feedrate_mmmin,
            spindle_rpm=template.spindle_rpm,
        )

    def _ramp_entry(self, target: Point3D, z_top: float, z_target: float, template: ProcessTemplate):
        """Ramp/helical entry: two-point plunge from z_top to z_target at target XY."""
        if abs(z_top - z_target) < 1e-6:
            return []
        start = Point3D(x=target.x, y=target.y, z=z_top)
        end = Point3D(x=target.x, y=target.y, z=z_target)
        return [ToolpathSegment(
            points=[start, end],
            motion_type=MotionType.FEED,
            feedrate_mmmin=template.feedrate_mmmin / 2,  # slower plunge
            spindle_rpm=template.spindle_rpm,
        )]