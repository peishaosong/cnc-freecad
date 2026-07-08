"""
Environment Verification Test - M0 Acceptance

Tests:
1. Python >= 3.10
2. FreeCAD importable
3. FreeCAD Part module works
4. FreeCAD Path Workbench available
5. Pydantic v2 importable (core dep)
6. NumPy importable (path calculation)
7. Project main module importable
"""
import sys


PASSED = 0
FAILED = 0


def test(name: str, func):
    """Single test case runner"""
    global PASSED, FAILED
    try:
        func()
        print(f"  [PASS] {name}", flush=True)
        PASSED += 1
    except AssertionError as e:
        print(f"  [FAIL] {name}: {e}", flush=True)
        FAILED += 1
    except Exception as e:
        print(f"  [FAIL] {name}: {type(e).__name__}: {e}", flush=True)
        FAILED += 1


def test_python_version():
    """Python >= 3.10"""
    assert sys.version_info >= (3, 10), (
        f"Python {sys.version_info} too old, need >= 3.10"
    )


def test_freecad_import():
    """FreeCAD importable"""
    import FreeCAD
    version = FreeCAD.Version()
    assert version[0] >= "1", f"FreeCAD {version[0]} too old, need >= 1.0"


def test_freecad_part_module():
    """FreeCAD Part module works (geometry kernel)"""
    import Part
    box = Part.makeBox(10, 10, 10)
    # OCC volume is float, allow 0.01 tolerance
    assert abs(box.Volume - 1000.0) < 0.01, f"Volume {box.Volume} not 1000"


def test_freecad_path_module():
    """FreeCAD Path Workbench available (CAM base)"""
    import Path
    assert hasattr(Path, "Command"), "Path.Command not found"


def test_pydantic_import():
    """Pydantic v2 importable (core dep)"""
    from pydantic import BaseModel

    class TestModel(BaseModel):
        name: str
        age: int

    m = TestModel(name="test", age=42)
    assert m.name == "test"


def test_numpy_import():
    """NumPy importable (path calculation)"""
    import numpy as np
    arr = np.array([1.0, 2.0, 3.0])
    assert arr.sum() == 6.0


def test_project_import():
    """Project main module importable"""
    sys.path.insert(0, "src")
    import cnc_freecad
    assert cnc_freecad.__version__ == "0.1.0"


def run_all() -> int:
    """Run all tests"""
    global PASSED, FAILED
    PASSED = 0
    FAILED = 0

    print("=" * 50, flush=True)
    print("CNC AutoCAM - M0 Environment Verification", flush=True)
    print(f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}", flush=True)
    print("=" * 50, flush=True)

    test("Python version", test_python_version)
    test("FreeCAD import", test_freecad_import)
    test("FreeCAD Part module", test_freecad_part_module)
    test("FreeCAD Path module", test_freecad_path_module)
    test("Pydantic v2 import", test_pydantic_import)
    test("NumPy import", test_numpy_import)
    test("Project module import", test_project_import)

    print("=" * 50, flush=True)
    print(f"Result: {PASSED} passed, {FAILED} failed", flush=True)
    print("=" * 50, flush=True)

    if FAILED == 0:
        print("[SUCCESS] All env checks passed. Ready for M1.", flush=True)
        return 0
    else:
        print("[FAILED] Env verification failed. Check above.", flush=True)
        return 1


if __name__ == "__main__":
    sys.exit(run_all())