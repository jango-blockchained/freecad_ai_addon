#!/usr/bin/env python3
"""
Test script to verify the __file__ issue is resolved in InitGui.py

This simulates FreeCAD's execution environment where __file__ might not be defined.
"""

import sys
import os

# Simulate FreeCAD environment by removing __file__ from globals
def test_initgui_without_file():
    """Test InitGui.py execution without __file__ defined"""
    
    print("Testing InitGui.py without __file__ variable...")
    
    # Change to the addon directory
    addon_path = "/home/jango/Git/freecad-ai-addon"
    os.chdir(addon_path)
    
    # Create a mock FreeCAD environment
    class MockApp:
        @staticmethod
        def getUserDataDir():
            return os.path.expanduser("~/.local/share/FreeCAD")
            
        class Console:
            @staticmethod
            def PrintMessage(msg):
                print(f"FreeCAD: {msg.strip()}")
                
            @staticmethod
            def PrintWarning(msg):
                print(f"FreeCAD WARNING: {msg.strip()}")
                
            @staticmethod
            def PrintError(msg):
                print(f"FreeCAD ERROR: {msg.strip()}")
    
    class MockGui:
        class Workbench:
            pass
            
        @staticmethod
        def addWorkbench(wb):
            print(f"FreeCAD: Workbench {wb.__class__.__name__} registered")
    
    # Add mock modules to sys.modules
    sys.modules['FreeCAD'] = MockApp()
    sys.modules['FreeCADGui'] = MockGui()
    
    # Execute the InitGui code in a controlled environment
    try:
        # Read the InitGui.py file
        with open("InitGui.py", "r") as f:
            initgui_code = f.read()
        
        # Create execution environment without __file__
        exec_globals = {
            'FreeCAD': MockApp(),
            'App': MockApp(),
            'Gui': MockGui(),
            'FreeCADGui': MockGui(),
            '__name__': '__main__',
            # Note: __file__ is intentionally NOT included
        }
        
        # Execute the code
        exec(initgui_code, exec_globals)
        
        print("✅ SUCCESS: InitGui.py executed without __file__ errors")
        
        # Test workbench instantiation
        if 'AIWorkbench' in exec_globals:
            workbench = exec_globals['AIWorkbench']()
            print(f"✅ SUCCESS: AIWorkbench instantiated - {workbench.MenuText}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_initgui_without_file()
    sys.exit(0 if success else 1)
