#!/usr/bin/env python3
"""
scripts/setup.py - Install/uninstall CNC AutoCAM as a FreeCAD workbench.

Mode: symlink ~/.FreeCAD/Mod/CncmAutoCAM -> <project>/src/Mod/CncmAutoCAM

After running once, every FreeCAD startup auto-loads this workbench
(Dock icon, Spotlight, command line — any way you launch it).

Usage:
  setup.py add      # Install (default)
  setup.py remove   # Uninstall
  setup.py status   # Show install state
"""
from __future__ import annotations

import argparse
import os
import platform
import shutil
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROJECT_MOD = PROJECT_ROOT / "src" / "Mod" / "CncmAutoCAM"


def find_mod_dir() -> Path | None:
    """Locate the FreeCAD user Mod directory (where FreeCAD scans for workbenches).

    FreeCAD 1.x on macOS scans:
        ~/Library/Application Support/FreeCAD/<version>/Mod/

    On Linux:
        ~/.local/share/FreeCAD/<version>/Mod/

    On Windows:
        %APPDATA%/FreeCAD/<version>/Mod/
    """
    system = platform.system()
    home = Path.home()

    if system == "Darwin":
        base = home / "Library/Application Support/FreeCAD"
    elif system == "Linux":
        base = home / ".local/share/FreeCAD"
    elif system == "Windows":
        appdata = os.environ.get("APPDATA")
        if not appdata:
            return None
        base = Path(appdata) / "FreeCAD"
    else:
        return None

    if not base.exists():
        return None

    # Pick the highest-version dir (e.g. v1-1 > v0-21)
    candidates = sorted((p for p in base.iterdir() if p.is_dir()), reverse=True)
    for c in candidates:
        mod = c / "Mod"
        return mod  # Always create if needed
    return None


def add() -> int:
    if not PROJECT_MOD.exists():
        print(f"[ERROR] Project Mod dir not found: {PROJECT_MOD}")
        return 1

    mod_dir = find_mod_dir()
    if mod_dir is None:
        print("[ERROR] FreeCAD user config directory not found.")
        print("        Please launch FreeCAD once, then re-run.")
        return 1

    mod_dir.mkdir(parents=True, exist_ok=True)
    target = mod_dir / "CncmAutoCAM"

    if target.is_symlink():
        if target.resolve() == PROJECT_MOD.resolve():
            print(f"[OK] Already installed: {target} -> {PROJECT_MOD}")
            return 0
        print(f"[INFO] Replacing existing symlink: {target}")
        target.unlink()
    elif target.exists():
        print(f"[ERROR] {target} exists and is not a symlink.")
        print(f"        Please remove manually: rm -rf {target}")
        return 1

    target.symlink_to(PROJECT_MOD)
    print(f"[OK] Installed: {target} -> {PROJECT_MOD}")
    print()
    print("Setup complete. Restart FreeCAD to see 'CNC AutoCAM' workbench.")
    print("Any way you launch FreeCAD (Dock, Spotlight, command line) auto-loads it.")
    return 0


def remove() -> int:
    mod_dir = find_mod_dir()
    if mod_dir is None:
        print("[info] FreeCAD user dir not found; nothing to remove.")
        return 0
    target = mod_dir / "CncmAutoCAM"

    if target.is_symlink():
        target.unlink()
        print(f"[OK] Removed symlink: {target}")
        return 0
    if target.exists():
        print(f"[WARN] {target} exists but is not a symlink (not removing).")
        return 1
    print("[info] Not installed; nothing to remove.")
    return 0


def status() -> int:
    mod_dir = find_mod_dir()
    if mod_dir is None:
        print("[ERROR] FreeCAD user config directory not found.")
        return 1
    target = mod_dir / "CncmAutoCAM"

    print(f"Project Mod dir:  {PROJECT_MOD}")
    print(f"FreeCAD Mod dir:  {mod_dir}")
    print(f"Target symlink:   {target}")
    print()
    if target.is_symlink():
        resolved = target.resolve()
        match = resolved == PROJECT_MOD.resolve()
        print(f"Status: INSTALLED" + (" (correct target)" if match else " (WRONG target!)"))
        print(f"  -> {resolved}")
        return 0 if match else 1
    if target.exists():
        print(f"Status: EXISTS but not a symlink")
        return 1
    print(f"Status: NOT INSTALLED")
    print(f"  Run ./scripts/setup.sh to install.")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Install CNC AutoCAM as FreeCAD workbench")
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("add", help="Install (default)")
    sub.add_parser("remove", help="Uninstall")
    sub.add_parser("status", help="Show install state")
    args = parser.parse_args()
    cmd = args.cmd or "add"

    if cmd == "remove":
        return remove()
    if cmd == "status":
        return status()
    return add()


if __name__ == "__main__":
    sys.exit(main())