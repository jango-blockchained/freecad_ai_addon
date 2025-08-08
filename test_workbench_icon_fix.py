#!/usr/bin/env python3
"""
Test script to verify WORKBENCH_ICON variable is properly defined
in InitGui.py without importing FreeCAD modules.
"""

import sys
import os
import ast


def test_workbench_icon_definition():
    """Test that WORKBENCH_ICON is defined at module level in InitGui.py"""

    # Read the InitGui.py file
    initgui_path = os.path.join(os.path.dirname(__file__), "InitGui.py")

    with open(initgui_path, "r") as f:
        content = f.read()

    # Parse the AST to check for WORKBENCH_ICON definition
    tree = ast.parse(content)

    workbench_icon_defined = False
    definition_line = None

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "WORKBENCH_ICON":
                    workbench_icon_defined = True
                    definition_line = node.lineno
                    break

    print(f"WORKBENCH_ICON defined: {workbench_icon_defined}")
    if definition_line:
        print(f"Definition found at line: {definition_line}")

    # Also check that it's defined before the class definition
    class_definition_line = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "AIWorkbench":
            class_definition_line = node.lineno
            break

    if class_definition_line:
        print(f"AIWorkbench class defined at line: {class_definition_line}")

        if definition_line and definition_line < class_definition_line:
            print("✅ WORKBENCH_ICON is defined BEFORE AIWorkbench class")
        else:
            print("❌ WORKBENCH_ICON is NOT defined before AIWorkbench class")

    return (
        workbench_icon_defined
        and definition_line
        and definition_line < class_definition_line
    )


if __name__ == "__main__":
    success = test_workbench_icon_definition()
    sys.exit(0 if success else 1)
