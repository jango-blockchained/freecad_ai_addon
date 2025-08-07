#!/usr/bin/env python3
"""
Test script to verify AIWorkbench can be loaded correctly

This script simulates what FreeCAD does when loading the addon.
"""

import sys
import os

# Add current directory to path (simulating FreeCAD environment)
addon_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, addon_dir)


def test_workbench_import():
    """Test if the workbench can be imported correctly"""
    try:
        print("Testing AIWorkbench import...")

        # Test direct import from InitGui (what FreeCAD does)
        from InitGui import AIWorkbench

        print("✓ AIWorkbench imported successfully from InitGui")

        # Test workbench instantiation
        workbench = AIWorkbench()
        print("✓ AIWorkbench instance created successfully")

        # Test basic properties
        print(f"  MenuText: {workbench.MenuText}")
        print(f"  ToolTip: {workbench.ToolTip}")
        print(f"  ClassName: {workbench.GetClassName()}")

        # Test icon property (should be set even if empty)
        print(f"  Icon: {getattr(workbench, 'Icon', 'Not set')}")

        print("✓ All workbench tests passed!")
        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_workbench_import()
    sys.exit(0 if success else 1)
