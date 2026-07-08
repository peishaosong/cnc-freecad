"""
CNCEngine - main entry point that wires together data, toolpath, and post-processing.

M1 uses a simple model: caller passes feature definitions alongside each Operation,
or reuses the Operation.feature_id as a lookup key.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from cnc_freecad.core.postprocessor import PostProcessor
from cnc_freecad.core.toolpath_generator import ToolpathGenerator
from cnc_freecad.data.models import (
    Feature,
    ProcessPlan,
    Toolpath,
)


class CNCEngine:
    """Main entry point: features -> plan -> toolpaths -> G-code."""

    def __init__(self):
        self.toolpath_generator = ToolpathGenerator()

    def generate_toolpaths(
        self,
        plan: ProcessPlan,
        features: Optional[Dict[str, Feature]] = None,
    ) -> List[Toolpath]:
        """Run each operation through toolpath generation.

        Args:
            plan: ProcessPlan with operations
            features: Optional map of feature_id -> Feature. Required for real geometry;
                      if None, generates a placeholder toolpath (useful for plan structure tests).
        """
        toolpaths: List[Toolpath] = []
        for op in sorted(plan.operations, key=lambda o: o.sequence):
            if features and op.feature_id in features:
                feature = features[op.feature_id]
                tp = self.toolpath_generator.generate(feature, op.template, op.tool)
            else:
                tp = self._placeholder_toolpath(op)
            toolpaths.append(tp)
        return toolpaths

    def postprocess(self, toolpaths: List[Toolpath], machine: str = "fanuc") -> str:
        pp = PostProcessor(machine=machine)
        return pp.process(toolpaths, part_name="CNC_PART")

    @staticmethod
    def _placeholder_toolpath(op):
        from cnc_freecad.data.models import Toolpath
        return Toolpath(
            id=f"tp_{op.feature_id}",
            feature_id=op.feature_id,
            tool_id=op.tool.id,
            strategy=op.template.strategy,
            segments=[],
        )