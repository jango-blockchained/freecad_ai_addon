"""
Path helper functions for the FreeCAD AI Addon.
"""

import os
import sys
import FreeCAD as App


def get_addon_dir():
    """
    Get the addon directory in a way that is robust to the FreeCAD execution
    context.
    """
    try:
        # Try to get the directory from __file__ if available
        return os.path.dirname(os.path.dirname(__file__))
    except NameError:
        # Fallback for FreeCAD execution context where __file__ might not be
        # defined. Use FreeCAD's App module to get the user data directory.
        try:
            user_data_dir = App.getUserDataDir()
            return os.path.join(user_data_dir, "Mod", "freecad_ai_addon")
        except (AttributeError, NameError):
            # Final fallback - use current working directory
            return os.getcwd()
