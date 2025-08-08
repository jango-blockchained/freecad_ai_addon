#!/usr/bin/env python3
"""
Test script to run InitGui.py in actual FreeCAD environment
"""

import sys
import os

print("=== Testing InitGui.py in FreeCAD Environment ===")
print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")

# Try to import FreeCAD modules to test availability
try:
    import FreeCAD as App

    print("✅ FreeCAD App module imported successfully")
    print(f"FreeCAD version: {App.Version()}")
    print(f"User data dir: {App.getUserDataDir()}")
except ImportError as e:
    print(f"❌ Failed to import FreeCAD App: {e}")
    sys.exit(1)

try:
    import FreeCADGui as Gui

    print("✅ FreeCADGui module imported successfully")
except ImportError as e:
    print(f"❌ Failed to import FreeCADGui: {e}")
    sys.exit(1)

# Now test our InitGui.py script
print("\n=== Executing InitGui.py ===")

try:
    # Add the current directory to path so we can import our module
    if os.getcwd() not in sys.path:
        sys.path.insert(0, os.getcwd())

    # Execute InitGui.py
    with open("InitGui.py", "r") as f:
        initgui_code = f.read()

    exec(initgui_code)

    print("✅ InitGui.py executed successfully")

    # Test if variables are set correctly
    if "WORKBENCH_ICON" in locals():
        print(f"WORKBENCH_ICON: {locals()['WORKBENCH_ICON']}")
    else:
        print("❌ WORKBENCH_ICON variable not found")

    if "AIWorkbench" in globals():
        wb_class = globals()["AIWorkbench"]
        print("✅ AIWorkbench class found")
        print(f"AIWorkbench.Icon: {getattr(wb_class, 'Icon', 'NOT_SET')}")
        print(f"AIWorkbench.MenuText: {getattr(wb_class, 'MenuText', 'NOT_SET')}")

        # Try to instantiate the workbench
        try:
            wb_instance = wb_class()
            print("✅ AIWorkbench instance created successfully")
        except Exception as e:
            print(f"❌ Failed to create AIWorkbench instance: {e}")
    else:
        print("❌ AIWorkbench class not found")

    # Test the Initialize function
    if "Initialize" in globals():
        print("\n=== Testing Initialize function ===")
        try:
            globals()["Initialize"]()
            print("✅ Initialize function executed successfully")
        except Exception as e:
            print(f"❌ Initialize function failed: {e}")
    else:
        print("❌ Initialize function not found")

except Exception as e:
    print(f"❌ Error executing InitGui.py: {e}")
    import traceback

    traceback.print_exc()

print("\n=== Test completed ===")
