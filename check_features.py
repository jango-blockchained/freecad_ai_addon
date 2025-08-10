#!/usr/bin/env python3
"""
Simple test to verify FreeCAD AI Addon imports and basic functionality
without requiring full FreeCAD GUI environment.
"""

import os
import sys

# Add the addon to path
addon_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, addon_dir)


def test_basic_imports():
    """Test basic module imports"""
    print("Testing basic imports...")

    try:
        # Test InitGui import
        import InitGui

        print("✓ InitGui imported successfully")

        # Test that workbench class exists
        if hasattr(InitGui, "AIWorkbench"):
            print("✓ AIWorkbench class found")
        else:
            print("✗ AIWorkbench class not found")

    except Exception as e:
        print(f"✗ InitGui import failed: {e}")

    try:
        # Test core modules
        from freecad_ai_addon.utils.logging import get_logger

        print("✓ Logging utils imported")

        from freecad_ai_addon.utils.config import get_config_manager

        print("✓ Config manager imported")

    except Exception as e:
        print(f"✗ Core module import failed: {e}")


def test_icon_paths():
    """Test icon path resolution"""
    print("\nTesting icon paths...")

    icon_dir = os.path.join(addon_dir, "resources", "icons")
    expected_icons = [
        "freecad_ai_addon.svg",
        "freecad_ai_addon_chat.svg",
        "freecad_ai_addon_settings.svg",
    ]

    for icon in expected_icons:
        icon_path = os.path.join(icon_dir, icon)
        if os.path.exists(icon_path):
            print(f"✓ {icon} found")
        else:
            print(f"✗ {icon} missing")


def test_workbench_features():
    """Test workbench feature completeness"""
    print("\nTesting workbench features...")

    # Check if commands are properly implemented
    commands_file = os.path.join(
        addon_dir, "freecad_ai_addon", "integration", "commands.py"
    )
    if os.path.exists(commands_file):
        print("✓ Commands module exists")

        # Read commands file and check for required classes
        with open(commands_file, "r") as f:
            content = f.read()

        if "class OpenChatCommand" in content:
            print("✓ OpenChatCommand implemented")
        else:
            print("✗ OpenChatCommand missing")

        if "class ProviderManagerCommand" in content:
            print("✓ ProviderManagerCommand implemented")
        else:
            print("✗ ProviderManagerCommand missing")
    else:
        print("✗ Commands module missing")


def check_todo_items():
    """Check for remaining TODO items"""
    print("\nChecking for incomplete features (TODOs)...")

    todo_files = [
        "freecad_ai_addon/ui/conversation_widget.py",
        "freecad_ai_addon/ui/interactive_elements.py",
        "freecad_ai_addon/ui/security_dialogs.py",
    ]

    for file_path in todo_files:
        full_path = os.path.join(addon_dir, file_path)
        if os.path.exists(full_path):
            with open(full_path, "r") as f:
                content = f.read()
                todo_count = content.count("TODO:")
                if todo_count > 0:
                    print(f"⚠️  {file_path}: {todo_count} TODO items")
                else:
                    print(f"✓ {file_path}: No TODO items")


if __name__ == "__main__":
    print("FreeCAD AI Addon - Feature Completeness Check")
    print("=" * 50)

    test_basic_imports()
    test_icon_paths()
    test_workbench_features()
    check_todo_items()

    print("\n" + "=" * 50)
    print("Test completed. Review any ✗ or ⚠️  items above.")
