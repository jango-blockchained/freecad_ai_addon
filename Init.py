"""
FreeCAD AI Addon - Non-GUI Initialization Module

This module handles initialization tasks that don't require a GUI interface,
such as setting up logging, configuration, and core services.
"""

import FreeCAD as App
import os
import sys

# Add the addon directory to Python path
addon_dir = os.path.dirname(__file__)
if addon_dir not in sys.path:
    sys.path.insert(0, addon_dir)

try:
    # Initialize logging system
    from freecad_ai_addon.utils.logging import setup_logging
    setup_logging()
    
    # Initialize configuration system
    from freecad_ai_addon.utils.config import ConfigManager
    config = ConfigManager()
    
    App.Console.PrintMessage("FreeCAD AI Addon: Core initialization completed\n")
    
except Exception as e:
    App.Console.PrintError(f"FreeCAD AI Addon: Failed to initialize core components: {str(e)}\n")
