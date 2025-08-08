#!/usr/bin/env python3
"""
Test InitGui.py using the FreeCAD Python interpreter from extracted AppImage.
This gives us access to real FreeCAD modules for proper testing.
"""

import sys
import os
import subprocess


def test_with_freecad_python():
    """Test InitGui.py using FreeCAD's Python interpreter"""

    # Path to the FreeCAD Python interpreter
    freecad_python = os.path.join(os.getcwd(), "squashfs-root", "usr", "bin", "python")

    if not os.path.exists(freecad_python):
        print(f"❌ FreeCAD Python interpreter not found at {freecad_python}")
        print("Make sure you have extracted the AppImage to squashfs-root/")
        return False

    # Create a test script that will be run with FreeCAD's Python
    test_script = """
import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

# Set up environment for FreeCAD libraries
freecad_lib_path = os.path.join(os.getcwd(), "squashfs-root", "usr", "lib")
if freecad_lib_path not in sys.path:
    sys.path.insert(0, freecad_lib_path)

# Set environment variables that FreeCAD might need
os.environ["FREECAD_USER_HOME"] = os.path.expanduser("~/.FreeCAD")

try:
    print("Testing FreeCAD module import...")
    
    # Test basic FreeCAD import
    try:
        import FreeCAD as App
        print("✅ FreeCAD module imported successfully")
        print(f"✅ FreeCAD version: {App.Version()}")
    except ImportError as e:
        print(f"❌ Failed to import FreeCAD: {e}")
        sys.exit(1)
    
    # Test FreeCADGui import (might fail in headless mode)
    try:
        import FreeCADGui as Gui
        print("✅ FreeCADGui module imported successfully")
        print(f"FreeCADGui attributes: {[attr for attr in dir(Gui) if not attr.startswith('_')]}")
        
        # Check if Workbench attribute exists
        if hasattr(Gui, 'Workbench'):
            print("✅ FreeCADGui.Workbench found")
        else:
            print("⚠️  FreeCADGui.Workbench not found (headless mode)")
            
    except ImportError as e:
        print(f"⚠️  FreeCADGui import failed (expected in headless mode): {e}")
        # Create a mock for testing
        class MockGui:
            class Workbench:
                pass
            @staticmethod
            def addWorkbench(wb):
                pass
        Gui = MockGui()
        print("✅ Using mock FreeCADGui for testing")
    
    # Now test our InitGui.py
    print("\\nTesting InitGui.py import...")
    try:
        # Import our specific InitGui.py file directly
        import importlib.util
        import sys
        
        initgui_path = os.path.join(os.getcwd(), "InitGui.py")
        print(f"Loading InitGui from: {initgui_path}")
        
        spec = importlib.util.spec_from_file_location("InitGui", initgui_path)
        InitGui = importlib.util.module_from_spec(spec)
        sys.modules["InitGui"] = InitGui
        spec.loader.exec_module(InitGui)
        
        print("✅ InitGui.py imported successfully")
        
        # Debug: list all attributes in InitGui module
        print(f"\\nInitGui module attributes: {[attr for attr in dir(InitGui) if not attr.startswith('_')]}")
        
        # Test AIWorkbench class
        if hasattr(InitGui, 'AIWorkbench'):
            print("✅ AIWorkbench class found")
            
            # Test instantiation
            try:
                workbench = InitGui.AIWorkbench()
                print("✅ AIWorkbench instance created")
                
                # Test basic attributes
                print(f"   MenuText: {getattr(workbench, 'MenuText', 'Not set')}")
                print(f"   ToolTip: {getattr(workbench, 'ToolTip', 'Not set')}")
                print(f"   Icon: {bool(getattr(workbench, 'Icon', ''))}")
                
                # Test methods
                try:
                    workbench.Initialize()
                    print("✅ Initialize method executed successfully")
                except Exception as e:
                    print(f"⚠️  Initialize method failed: {e}")
                
                try:
                    workbench.Activated()
                    print("✅ Activated method executed successfully")
                except Exception as e:
                    print(f"⚠️  Activated method failed: {e}")
                
                try:
                    workbench.Deactivated()
                    print("✅ Deactivated method executed successfully")
                except Exception as e:
                    print(f"⚠️  Deactivated method failed: {e}")
                
                try:
                    classname = workbench.GetClassName()
                    print(f"✅ GetClassName returned: {classname}")
                except Exception as e:
                    print(f"⚠️  GetClassName method failed: {e}")
                    
            except Exception as e:
                print(f"❌ Failed to create AIWorkbench instance: {e}")
                import traceback
                traceback.print_exc()
                sys.exit(1)
        else:
            print("❌ AIWorkbench class not found")
            # Debug: try to see what went wrong during module loading
            if hasattr(InitGui, '__all__'):
                print(f"InitGui.__all__: {InitGui.__all__}")
            
            # Check if there were any import/execution errors
            if hasattr(InitGui, 'safe_print'):
                print("✅ safe_print function found")
            if hasattr(InitGui, 'get_addon_dir'):
                print("✅ get_addon_dir function found")
            if hasattr(InitGui, 'BaseWorkbench'):
                print(f"✅ BaseWorkbench found: {InitGui.BaseWorkbench}")
            
            sys.exit(1)
        
        # Test helper functions
        if hasattr(InitGui, 'get_addon_dir'):
            try:
                addon_dir = InitGui.get_addon_dir()
                print(f"✅ get_addon_dir returned: {addon_dir}")
            except Exception as e:
                print(f"⚠️  get_addon_dir failed: {e}")
        
        if hasattr(InitGui, 'safe_print'):
            try:
                InitGui.safe_print("Test message from FreeCAD environment")
                print("✅ safe_print function works")
            except Exception as e:
                print(f"⚠️  safe_print failed: {e}")
        
        print("\\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Failed to import InitGui.py: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
"""

    # Write the test script to a temporary file
    test_file = "temp_freecad_test.py"
    try:
        with open(test_file, "w") as f:
            f.write(test_script)

        print(f"Running test with FreeCAD Python interpreter: {freecad_python}")
        print("=" * 60)

        # Set up environment for FreeCAD
        env = os.environ.copy()
        env["LD_LIBRARY_PATH"] = os.path.join(
            os.getcwd(), "squashfs-root", "usr", "lib"
        )
        env["PYTHONPATH"] = os.path.join(os.getcwd(), "squashfs-root", "usr", "lib")

        # Run the test with FreeCAD's Python
        result = subprocess.run(
            [freecad_python, test_file],
            cwd=os.getcwd(),
            env=env,
            capture_output=True,
            text=True,
        )

        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)

        success = result.returncode == 0
        print("=" * 60)
        print(f"Test {'PASSED' if success else 'FAILED'}")

        return success

    finally:
        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)


if __name__ == "__main__":
    print("Testing InitGui.py with FreeCAD Python interpreter...")
    success = test_with_freecad_python()
    sys.exit(0 if success else 1)
