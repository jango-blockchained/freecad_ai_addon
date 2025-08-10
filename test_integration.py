#!/usr/bin/env python3
"""
Test the full workbench initialization without FreeCAD dependencies.
"""

import os
import sys

# Add the addon to path
addon_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, addon_dir)


def mock_freecad_modules():
    """Create mock FreeCAD modules for testing"""
    import types

    # Mock FreeCAD App module
    mock_app = types.ModuleType("FreeCAD")
    mock_app.Console = types.SimpleNamespace()
    mock_app.Console.PrintMessage = lambda msg: print(f"[FreeCAD] {msg}", end="")
    mock_app.Console.PrintError = lambda msg: print(f"[ERROR] {msg}", end="")
    mock_app.Console.PrintWarning = lambda msg: print(f"[WARNING] {msg}", end="")
    mock_app.getUserAppDataDir = lambda: os.path.expanduser("~/.FreeCAD")
    mock_app.ActiveDocument = None
    mock_app.newDocument = lambda name: print(f"Created document: {name}")

    # Mock FreeCADGui module
    mock_gui = types.ModuleType("FreeCADGui")
    mock_gui.addCommand = lambda name, cmd: print(f"Registered command: {name}")
    mock_gui.getMainWindow = lambda: None

    # Mock PySide6 modules
    mock_pyside = types.ModuleType("PySide6")
    mock_qtcore = types.ModuleType("PySide6.QtCore")
    mock_qtwidgets = types.ModuleType("PySide6.QtWidgets")
    mock_qtgui = types.ModuleType("PySide6.QtGui")

    # Add to sys.modules
    sys.modules["FreeCAD"] = mock_app
    sys.modules["FreeCADGui"] = mock_gui
    sys.modules["PySide6"] = mock_pyside
    sys.modules["PySide6.QtCore"] = mock_qtcore
    sys.modules["PySide6.QtWidgets"] = mock_qtwidgets
    sys.modules["PySide6.QtGui"] = mock_qtgui


def test_workbench_initialization():
    """Test complete workbench initialization"""
    print("Testing workbench initialization...")

    try:
        # Mock the FreeCAD environment
        mock_freecad_modules()

        # Import the InitGui module
        import InitGui

        # Create workbench instance
        workbench = InitGui.AIWorkbench()
        print("✓ Workbench instance created")

        # Test initialization
        workbench.Initialize()
        print("✓ Workbench initialization completed")

        # Test activation/deactivation
        workbench.Activated()
        workbench.Deactivated()
        print("✓ Workbench activation/deactivation works")

        return True

    except Exception as e:
        print(f"✗ Workbench initialization failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_command_imports():
    """Test command imports"""
    print("\nTesting command imports...")

    try:
        # This should work with mocked modules
        from freecad_ai_addon.integration.commands import (
            OpenChatCommand,
            ProviderManagerCommand,
        )

        # Test command instantiation
        chat_cmd = OpenChatCommand()
        provider_cmd = ProviderManagerCommand()

        # Test command resources
        chat_resources = chat_cmd.GetResources()
        provider_resources = provider_cmd.GetResources()

        print("✓ Commands imported and instantiated successfully")
        print(f"✓ OpenChatCommand: {chat_resources['MenuText']}")
        print(f"✓ ProviderManagerCommand: {provider_resources['MenuText']}")

        return True

    except Exception as e:
        print(f"✗ Command import failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("FreeCAD AI Addon - Full Integration Test")
    print("=" * 50)

    success = True

    success &= test_workbench_initialization()
    success &= test_command_imports()

    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! The workbench appears to be working correctly.")
    else:
        print("❌ Some tests failed. Check the errors above.")
