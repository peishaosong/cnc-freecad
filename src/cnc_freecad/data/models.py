"""
Pydantic data models for CNC AutoCAM.

Defines the core entities used across feature recognition,
process matching, toolpath generation, and post-processing.

See docs/cnc-freecad/03-data-model.md for schema details.
"""
from __future__ import annotations

from enum import Enum
from typing import List, Literal, Optional
from pydantic import BaseModel, Field, field_validator, model_validator


# === Enumerations ===

class FeatureType(str, Enum):
    POCKET = "pocket"
    DRILL = "drill"
    BORE = "bore"
    TAP = "tap"
    CONTOUR_PROFILE = "profile"
    CHAMFER = "chamfer"
    SLOT = "slot"
    STEP = "step"


class ToolType(str, Enum):
    FLAT_ENDMILL = "flat_endmill"
    BALL_ENDMILL = "ball_endmill"
    BULL_NOSE = "bull_nose"
    DOVE_TAIL = "dove_tail"
    DRILL = "drill"
    TAP = "tap"
    REAMER = "reamer"
    COUNTERSINK = "countersink"
    END_MILL = "end_mill"


class ToolMaterial(str, Enum):
    HSS = "HSS"
    CARBIDE = "carbide"
    COATED_CARBIDE = "coated_carbide"


class MaterialCategory(str, Enum):
    ALUMINUM = "aluminum"
    STEEL = "steel"
    STAINLESS = "stainless"
    TITANIUM = "titanium"
    BRASS = "brass"
    CAST_IRON = "cast_iron"
    PLASTIC = "plastic"


class Strategy(str, Enum):
    ROUGH_PARALLEL = "rough_parallel"
    ROUGH_SPIRAL = "rough_spiral"
    ROUGH_ZIGZAG = "rough_zigzag"
    FINISH_CONTOUR = "finish_contour"
    FINISH_PARALLEL = "finish_parallel"
    FINISH_SCALLOP = "finish_scallop"
    FINISH_SPIRAL = "finish_spiral"
    CLEANUP_PENCIL = "cleanup_pencil"
    CLEANUP_PARALLEL = "cleanup_parallel"
    DRILL_PECK = "drill_peck"
    DRILL_PECK_DEEP = "drill_peck_deep"
    DRILL_TAP = "drill_tap"


# === Geometry helpers ===

class BoundingBox(BaseModel):
    x_min: float
    x_max: float
    y_min: float
    y_max: float
    z_min: float
    z_max: float

    @property
    def center_x(self) -> float:
        return (self.x_min + self.x_max) / 2

    @property
    def center_y(self) -> float:
        return (self.y_min + self.y_max) / 2

    @property
    def center_z(self) -> float:
        return (self.z_min + self.z_max) / 2

    @property
    def width_x(self) -> float:
        return self.x_max - self.x_min

    @property
    def width_y(self) -> float:
        return self.y_max - self.y_min

    @property
    def depth_z(self) -> float:
        return self.z_max - self.z_min


class Point3D(BaseModel):
    x: float
    y: float
    z: float

    def __add__(self, other: Point3D) -> Point3D:
        return Point3D(x=self.x + other.x, y=self.y + other.y, z=self.z + other.z)

    def __sub__(self, other: Point3D) -> Point3D:
        return Point3D(x=self.x - other.x, y=self.y - other.y, z=self.z - other.z)


# === Core entities ===

class Feature(BaseModel):
    """A manufacturing feature (pocket, hole, profile, etc)."""
    id: str
    type: FeatureType
    depth_mm: float = Field(gt=0)
    bounding_box: BoundingBox
    bottom_z: float
    top_z: float
    wall_angle_deg: float = 0.0
    floor_type: Literal["flat", "curved"] = "flat"
    diameter_mm: Optional[float] = None  # only for drill/bore/tap
    parent_feature_id: Optional[str] = None
    material_allowance_mm: float = 0.5
    priority: int = 0

    @model_validator(mode="after")
    def check_z_order(self):
        if self.top_z <= self.bottom_z:
            raise ValueError(f"top_z ({self.top_z}) must be > bottom_z ({self.bottom_z})")
        return self


class Tool(BaseModel):
    """A cutting tool definition."""
    id: str
    type: ToolType
    diameter_mm: float = Field(gt=0)
    flute_length_mm: float = Field(gt=0)
    overall_length_mm: float = Field(gt=0)
    shank_diameter_mm: float = Field(gt=0)
    material: ToolMaterial
    num_flutes: int = Field(ge=1, le=8)
    max_rpm: int = Field(ge=500, le=30000)
    max_feedrate_mmmin: float = Field(gt=0)
    holder_type: str = "side_lock"
    description: str = ""
    tool_number: int = 1  # T-number on the machine

    @property
    def corner_radius_mm(self) -> float:
        if self.type == ToolType.BALL_ENDMILL:
            return self.diameter_mm / 2
        return 0.0


class Material(BaseModel):
    """Workpiece material definition."""
    id: str
    name: str
    category: MaterialCategory
    hardness_hrc: float = Field(ge=0)
    density_gcc: float = Field(gt=0)
    tensile_strength_mpa: float = Field(gt=0)
    is_soft: bool = True

    @property
    def cutting_difficulty(self) -> str:
        if self.is_soft:
            return "easy"
        elif self.hardness_hrc < 35:
            return "medium"
        elif self.hardness_hrc < 50:
            return "hard"
        return "very_hard"


class ProcessTemplate(BaseModel):
    """Cutting parameters for a specific tool/material/strategy combination."""
    id: str
    tool_id: str
    material_category: MaterialCategory
    strategy: Strategy
    spindle_rpm: int = Field(ge=500, le=30000)
    feedrate_mmmin: float = Field(gt=0)
    depth_of_cut_mm: float = Field(gt=0)
    width_of_cut_mm: float = Field(gt=0)
    coolant: bool = True
    stepover_mm: float = 0.0
    lead_in_mm: float = 2.0
    lead_out_mm: float = 2.0
    ramping_angle_deg: float = 3.0
    helix_entry: bool = True
    notes: str = ""


class Operation(BaseModel):
    """A single machining operation within a process plan."""
    feature_id: str
    template: ProcessTemplate
    tool: Tool
    sequence: int = 0
    stock_to_leave_mm: float = 0.5
    rapid_safe_z_mm: float = 5.0
    rapid_retract_z_mm: float = 2.0


class ProcessPlan(BaseModel):
    """Ordered set of operations for a part."""
    part_name: str
    material: Material
    operations: List[Operation] = Field(default_factory=list)
    total_estimated_time_min: float = 0.0


# === Toolpath output ===

class MotionType(str, Enum):
    RAPID = "rapid"
    FEED = "feed"
    ARC = "arc"


class ArcPoint(BaseModel):
    """G02/G03 arc interpolation."""
    start: Point3D
    end: Point3D
    center: Point3D
    clockwise: bool  # True=G02, False=G03


class ToolpathSegment(BaseModel):
    points: List[Point3D]
    arc_points: List[ArcPoint] = Field(default_factory=list)
    motion_type: MotionType
    feedrate_mmmin: float = 0.0
    spindle_rpm: int = 0
    coolant_on: bool = True


class Toolpath(BaseModel):
    id: str
    feature_id: str
    tool_id: str
    strategy: Strategy
    segments: List[ToolpathSegment]
    total_length_mm: float = 0.0
    estimated_time_min: float = 0.0
    bounding_box: Optional[BoundingBox] = None