"""
Workbench entry point for FreeCAD AI Addon

This module provides the main workbench class that FreeCAD can find and
instantiate based on the package.xml configuration.
"""

import os
import sys

# Add the addon directory to Python path if not already there
addon_dir = os.path.dirname(__file__)
if addon_dir not in sys.path:
    sys.path.insert(0, addon_dir)

try:
    # Import FreeCAD modules
    import FreeCADGui as Gui
    import FreeCAD as App
    
    # Import the actual workbench implementation
    from freecad_ai_addon.integration.workbench import (
        AIWorkbench as _AIWorkbench
    )
    
    # Create the workbench class that FreeCAD will find
    class AIWorkbench(_AIWorkbench):
        """AI Workbench class for FreeCAD - Root level accessor"""
        pass
        
except ImportError as e:
    # Fallback if imports fail
    import warnings
    warnings.warn(f"Failed to import AIWorkbench: {e}")
    
    # Create a minimal fallback workbench
    try:
        import FreeCADGui as Gui
        import FreeCAD as App
        
        class AIWorkbench(Gui.Workbench):
            """Fallback AI Workbench class"""
            MenuText = "AI Assistant"
            ToolTip = "AI-powered design assistant (limited mode)"
            
            def Initialize(self):
                App.Console.PrintWarning(
                    "AI Workbench running in limited mode due to import "
                    "issues\n")
                    
            def GetClassName(self):
                return "AIWorkbench"
                
    except ImportError:
        # Ultimate fallback - this should not happen in FreeCAD
        class AIWorkbench:
            """Ultimate fallback workbench"""
            pass

# Make it available at module level for FreeCAD discovery
__all__ = ['AIWorkbench']
