"""
FreeCAD AI Addon - GUI Initialization Module

This module handles the initialization of the AI Workbench and related GUI components
when FreeCAD starts with a GUI interface.
"""

import FreeCAD as App
import FreeCADGui as Gui
from freecad_ai_addon.integration.workbench import AIWorkbench


def Initialize():
    """Initialize the AI Workbench and register it with FreeCAD"""
    try:
        # Commands are imported through workbench
        # Register the AI Workbench
        Gui.addWorkbench(AIWorkbench())
        App.Console.PrintMessage("FreeCAD AI Addon: Workbench registered successfully\n")
    except Exception as e:
        App.Console.PrintError(f"FreeCAD AI Addon: Failed to initialize workbench: {str(e)}\n")
