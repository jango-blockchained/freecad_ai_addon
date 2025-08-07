"""
FreeCAD AI Addon - GUI Initialization Module

This module handles the initialization of the AI Workbench and related GUI
components when FreeCAD starts with a GUI interface.
"""

import FreeCAD as App
import FreeCADGui as Gui
import sys
import os


def get_addon_dir():
    """
    Get the addon directory in a way that is robust to the FreeCAD execution
    context.
    """
    try:
        # Try to get the directory from __file__ if available
        return os.path.dirname(__file__)
    except NameError:
        # Fallback for FreeCAD execution context where __file__ might not be
        # defined. Use FreeCAD's App module to get the user data directory.
        try:
            user_data_dir = App.getUserDataDir()
            return os.path.join(user_data_dir, "Mod", "freecad-ai-addon")
        except (AttributeError, NameError):
            # Final fallback - use current working directory
            return os.getcwd()


# Get the addon directory and add it to the Python path
addon_dir = get_addon_dir()
if addon_dir and addon_dir not in sys.path:
    sys.path.insert(0, addon_dir)


class AIWorkbench(Gui.Workbench):
    """AI Workbench class for FreeCAD"""

    MenuText = "AI Assistant"
    ToolTip = "AI-powered design assistant with conversation and agent tools"

    def __init__(self):
        """Initialize the workbench"""
        super().__init__()
        # Set Icon dynamically to avoid initialization issues
        icon_path = os.path.join(
            get_addon_dir(), "resources", "icons", "freecad_ai_addon.svg"
        )
        if os.path.exists(icon_path):
            self.Icon = icon_path
        else:
            # Fallback to a default icon or no icon
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
                f"AI Workbench initialization failed: {e}\n"
            )

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
            "FreeCAD AI Addon: Workbench registered successfully\n"
        )
    except ImportError as e:
        App.Console.PrintError(
            f"FreeCAD AI Addon: Failed to initialize workbench: {str(e)}\n"
        )
