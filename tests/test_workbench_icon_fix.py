#!/usr/bin/env python3
"""
Regression test for workbench icon handling in InitGui.py.

Verifies that:
- InitGui imports without FreeCAD
- AIWorkbench is exposed at module level
- AIWorkbench has a class-level Icon attribute (string; may be empty)
- GetClassName returns the FreeCAD-expected value
"""

import sys
import os


def test_workbench_icon_contract():
    """Test contract for AIWorkbench icon and class attributes."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    import InitGui  # noqa: E402

    assert hasattr(InitGui, "AIWorkbench"), "AIWorkbench not exported in InitGui"
    wb_cls = InitGui.AIWorkbench

    # Class attributes present
    assert hasattr(wb_cls, "MenuText")
    assert hasattr(wb_cls, "ToolTip")
    assert hasattr(wb_cls, "Icon"), "Class-level Icon attribute missing"
    assert isinstance(getattr(wb_cls, "Icon"), str), "Icon must be a string"

    # Instantiate to allow fallback class to compute icon path
    inst = wb_cls()
    assert hasattr(inst, "Icon")
    assert isinstance(inst.Icon, str)

    # FreeCAD expects this identifier for Python workbenches
    assert inst.GetClassName() == "Gui::PythonWorkbench"


if __name__ == "__main__":
    ok = test_workbench_icon_contract()
    sys.exit(0 if ok is not False else 1)
