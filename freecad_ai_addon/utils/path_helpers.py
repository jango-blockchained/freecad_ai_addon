"""
Path helper functions for the FreeCAD AI Addon.
"""

import os
import sys

try:
    import FreeCAD as App
except ImportError:
    App = None


def get_addon_dir():
    """
    Get the addon directory in a way that is robust to the FreeCAD execution
    context.
    """
    try:
        # Try to get the directory from __file__ if available
        return os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    except Exception:
        # Fallbacks for contexts where __file__ might not be defined (some FreeCAD flows)
        try:
            if App is not None:
                # Correct API per FreeCAD: getUserAppDataDir
                user_data_dir = App.getUserAppDataDir()
                candidate = os.path.join(user_data_dir, "Mod", "freecad_ai_addon")
                return os.path.realpath(candidate)
        except Exception:
            pass

        # Final fallback - use current working directory
        return os.path.realpath(os.getcwd())
