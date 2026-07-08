"""
Session state shared across CNC AutoCAM commands.

Holds the current feature/tool/template selection so commands can read them.
"""
from __future__ import annotations

from typing import Dict, Optional

from cnc_freecad.data.models import (
    Feature,
    Material,
    MaterialCategory,
    ProcessTemplate,
    Tool,
)


class CncmSession:
    """Singleton-style session state."""

    def __init__(self):
        self.features: Dict[str, Feature] = {}
        self.tool: Optional[Tool] = None
        self.template: Optional[ProcessTemplate] = None
        # Default material for aluminum (M1 default)
        self.material = Material(
            id="6061_t6_al",
            name="6061-T6 Aluminum",
            category=MaterialCategory.ALUMINUM,
            hardness_hrc=20.0,
            density_gcc=2.7,
            tensile_strength_mpa=310.0,
            is_soft=True,
        )
        self._feature_counter = 0

    def add_feature(self, feature: Feature):
        self.features[feature.id] = feature

    def clear_features(self):
        self.features.clear()
        self._feature_counter = 0

    def set_tool(self, tool: Tool):
        self.tool = tool

    def set_template(self, template: ProcessTemplate):
        self.template = template

    def next_feature_index(self) -> int:
        self._feature_counter += 1
        return self._feature_counter


# Module-level singleton
session = CncmSession()