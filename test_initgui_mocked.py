#!/usr/bin/env python3
"""
Test InitGui.py import with FreeCAD mocks.
This simulates the FreeCAD environment to test our workbench initialization.
"""

import sys
import os
from unittest.mock import MagicMock

# Add current directory to path to simulate FreeCAD's import context
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def setup_freecad_mocks():
    """Setup mock FreeCAD modules"""
    # Mock FreeCAD App module
    mock_app = MagicMock()
    mock_app.Console = MagicMock()
    mock_app.Console.PrintMessage = MagicMock()
    mock_app.Console.PrintError = MagicMock()
    mock_app.getUserAppDataDir = MagicMock(
        return_value="/home/jango/.local/share/FreeCAD"
    )

    # Mock FreeCADGui module
    mock_gui = MagicMock()
    mock_workbench = MagicMock()
    mock_gui.Workbench = mock_workbench
    mock_gui.addWorkbench = MagicMock()

    # Add mocks to sys.modules before importing
    sys.modules["FreeCAD"] = mock_app
    sys.modules["FreeCADGui"] = mock_gui

    return mock_app, mock_gui


def test_initgui_with_mocks():
    """Test importing InitGui.py with FreeCAD mocks"""
    try:
        print("Setting up FreeCAD mocks...")
        mock_app, mock_gui = setup_freecad_mocks()

        print("Importing InitGui.py...")
        import InitGui

        print("✅ InitGui.py imported successfully")

        # Check if AIWorkbench class exists
        if hasattr(InitGui, "AIWorkbench"):
            print("✅ AIWorkbench class found")

            # Try to instantiate it
            try:
                workbench = InitGui.AIWorkbench()
                print("✅ AIWorkbench instance created successfully")

                # Check if basic attributes exist
                if hasattr(workbench, "MenuText"):
                    print(f"✅ MenuText: {workbench.MenuText}")
                if hasattr(workbench, "ToolTip"):
                    print(f"✅ ToolTip: {workbench.ToolTip}")
                if hasattr(workbench, "Icon"):
                    print(f"✅ Icon attribute exists: {bool(workbench.Icon)}")

                # Test methods exist
                if hasattr(workbench, "Initialize"):
                    print("✅ Initialize method exists")
                if hasattr(workbench, "Activated"):
                    print("✅ Activated method exists")
                if hasattr(workbench, "Deactivated"):
                    print("✅ Deactivated method exists")
                if hasattr(workbench, "GetClassName"):
                    print("✅ GetClassName method exists")

                # Test that methods can be called
                try:
                    workbench.Initialize()
                    print("✅ Initialize method can be called")
                except Exception as e:
                    print(f"⚠️  Initialize method failed: {e}")

                try:
                    workbench.Activated()
                    print("✅ Activated method can be called")
                except Exception as e:
                    print(f"⚠️  Activated method failed: {e}")

                try:
                    workbench.Deactivated()
                    print("✅ Deactivated method can be called")
                except Exception as e:
                    print(f"⚠️  Deactivated method failed: {e}")

                try:
                    classname = workbench.GetClassName()
                    print(f"✅ GetClassName returned: {classname}")
                except Exception as e:
                    print(f"⚠️  GetClassName method failed: {e}")

            except Exception as e:
                print(f"❌ AIWorkbench instantiation failed: {e}")
                import traceback

                traceback.print_exc()
                return False

        else:
            print("❌ AIWorkbench class not found")
            return False

        # Check if required functions exist
        if hasattr(InitGui, "safe_print"):
            print("✅ safe_print function found")
            try:
                InitGui.safe_print("Test message")
                print("✅ safe_print function works")
            except Exception as e:
                print(f"⚠️  safe_print failed: {e}")
        else:
            print("❌ safe_print function not found")

        if hasattr(InitGui, "get_addon_dir"):
            print("✅ get_addon_dir function found")
            try:
                addon_dir = InitGui.get_addon_dir()
                print(f"✅ get_addon_dir returned: {addon_dir}")
            except Exception as e:
                print(f"⚠️  get_addon_dir failed: {e}")
        else:
            print("❌ get_addon_dir function not found")

        # Check if workbench was registered
        if mock_gui.addWorkbench.called:
            print("✅ Workbench registration was attempted")
        else:
            print("⚠️  Workbench registration was not attempted")

        return True

    except Exception as e:
        print(f"❌ Failed to import InitGui.py: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Testing InitGui.py import with FreeCAD mocks...")
    success = test_initgui_with_mocks()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)
