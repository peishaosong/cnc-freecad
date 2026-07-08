"""CNC AutoCAM FreeCAD commands."""

from cnc_freecad.freecad.commands.cmd_import_part import CncmImportPart
from cnc_freecad.freecad.commands.cmd_define_feature import CncmDefineFeature
from cnc_freecad.freecad.commands.cmd_select_tool import CncmSelectTool
from cnc_freecad.freecad.commands.cmd_select_template import CncmSelectTemplate
from cnc_freecad.freecad.commands.cmd_generate import CncmGenerate
from cnc_freecad.freecad.commands.cmd_postprocess import CncmPostprocess

__all__ = [
    "CncmImportPart",
    "CncmDefineFeature",
    "CncmSelectTool",
    "CncmSelectTemplate",
    "CncmGenerate",
    "CncmPostprocess",
]