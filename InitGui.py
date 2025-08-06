"""
FreeCAD AI Addon - GUI Initialization Module

This module handles the initialization of the AI Workbench and related GUI
components when FreeCAD starts with a GUI interface.
"""

import FreeCAD as App
import FreeCADGui as Gui
import sys
import os


# Add the addon directory to Python path if not already there
addon_dir = os.path.dirname(__file__)
if addon_dir not in sys.path:
    sys.path.insert(0, addon_dir)


class AIWorkbench(Gui.Workbench):
    """AI Workbench class for FreeCAD"""

    MenuText = "AI Assistant"
    ToolTip = ("AI-powered design assistant with conversation and "
               "agent capabilities")
    
    def __init__(self):
        """Initialize the AI Workbench"""
        try:
            # Set icon path
            self._set_icon_path()
        except (ImportError, OSError) as e:
            App.Console.PrintWarning(f"AI Workbench icon setup failed: {e}\n")

    def _set_icon_path(self):
        """Set the workbench icon path"""
        try:
            # Get the addon directory
            icon_path = os.path.join(
                addon_dir, "resources", "icons", "freecad_ai_addon.svg")
            
            if os.path.exists(icon_path):
                self.Icon = icon_path
            else:
                # Use empty string if icon not found
                self.Icon = ""
        except (OSError, AttributeError):
            self.Icon = ""

    def Initialize(self):
        """Initialize workbench GUI elements"""
        try:
            App.Console.PrintMessage("AI Workbench initializing...\n")
            
            # Create basic menu structure
            self.appendMenu("AI Assistant", [])
            
            App.Console.PrintMessage("AI Workbench initialized successfully\n")

        except (ImportError, AttributeError) as e:
            App.Console.PrintError(
                f"AI Workbench initialization failed: {e}\n")

    def Activated(self):
        """Called when workbench is activated"""
        App.Console.PrintMessage("AI Assistant workbench activated\n")

    def Deactivated(self):
        """Called when workbench is deactivated"""
        App.Console.PrintMessage("AI Assistant workbench deactivated\n")

    def GetClassName(self):
        """Return the class name"""
        return "AIWorkbench"


def Initialize():
    """Initialize the AI Workbench and register it with FreeCAD"""
    try:
        # Register the AI Workbench
        Gui.addWorkbench(AIWorkbench())
        App.Console.PrintMessage(
            "FreeCAD AI Addon: Workbench registered successfully\n")
    except ImportError as e:
        App.Console.PrintError(
            f"FreeCAD AI Addon: Failed to initialize workbench: {str(e)}\n")
