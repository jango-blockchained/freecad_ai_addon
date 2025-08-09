#!/usr/bin/env python3
"""
Quick test to verify InitGui.py can be imported without basic errors.
This simulates what happens when FreeCAD tries to load the workbench.
"""

import sys
import os

# Add current directory to path to simulate FreeCAD's import context
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_initgui_import():
    """Test importing InitGui.py without FreeCAD context"""
    try:
        # This should work even without FreeCAD, though some functionality will be limited
        import InitGui

        print("✅ InitGui.py imported successfully")

        # Check if AIWorkbench class exists
        if hasattr(InitGui, "AIWorkbench"):
            print("✅ AIWorkbench class found")

            # Try to instantiate it (this might fail due to missing FreeCAD, but shouldn't crash)
            try:
                workbench = InitGui.AIWorkbench()
                print("✅ AIWorkbench instance created successfully")

                # Check if basic attributes exist
                if hasattr(workbench, "MenuText"):
                    print(f"✅ MenuText: {workbench.MenuText}")
                if hasattr(workbench, "ToolTip"):
                    print(f"✅ ToolTip: {workbench.ToolTip}")

            except Exception as e:
                print(
                    f"⚠️  AIWorkbench instantiation failed (expected without FreeCAD): {e}"
                )

        else:
            print("❌ AIWorkbench class not found")

        # Check if required functions exist
        if hasattr(InitGui, "safe_print"):
            print("✅ safe_print function found")
        else:
            print("❌ safe_print function not found")

        if hasattr(InitGui, "get_addon_dir"):
            print("✅ get_addon_dir function found")
        else:
            print("❌ get_addon_dir function not found")

        return True

    except Exception as e:
        print(f"❌ Failed to import InitGui.py: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Testing InitGui.py import...")
    success = test_initgui_import()
    sys.exit(0 if success else 1)
