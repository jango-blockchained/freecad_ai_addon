"""
FreeCAD AI Addon - GUI Initialization Module

This module handles the initialization of the AI Workbench and related GUI
components when FreeCAD starts with a GUI interface.
"""

import os
import sys

# Then import FreeCAD modules
import FreeCAD as App

try:
    import FreeCADGui as Gui

    # Check if Workbench is available (it's not in headless mode)
    if hasattr(Gui, "Workbench"):
        BaseWorkbench = Gui.Workbench
    else:
        # FreeCAD is running in headless mode, create a dummy base class
        class _DummyWorkbench(object):
            """Fallback base to allow class definition when FreeCAD GUI is not fully available"""

            def __init__(self):
                pass

        BaseWorkbench = _DummyWorkbench
        Gui = None  # Disable GUI features
except ImportError:
    Gui = None  # GUI may not be available during early metadata/icon probing

    class _DummyWorkbench(object):
        """Fallback base to allow class definition before FreeCAD GUI loads"""

        def __init__(self):
            pass

    BaseWorkbench = _DummyWorkbench


# Debug helper function to safely print messages as early as possible
def safe_print(message: str):
    """Print message safely whether in FreeCAD context or not."""
    try:
        if "App" in globals() and hasattr(App, "Console"):
            try:
                App.Console.PrintMessage(f"{message}\n")
            except Exception:
                print(message)
        else:
            print(message)
    except Exception:
        # Last resort if all else fails
        try:
            print(message)
        except Exception:
            pass


def get_addon_dir():
    """
    Get the addon directory in a way that is robust to the FreeCAD execution
    context, including handling symlinks properly.
    """
    try:
        # Try to get the directory from __file__ if available
        return os.path.dirname(os.path.realpath(__file__))
    except NameError:
        # Fallback for FreeCAD execution context where __file__ might not be
        # defined. Try multiple approaches to find the addon directory.
        try:
            # First try using FreeCAD's App module
            user_data_dir = App.getUserAppDataDir()
            addon_path = os.path.join(user_data_dir, "Mod", "freecad_ai_addon")
            if os.path.exists(addon_path):
                # Resolve symlinks to get the real path
                real_path = os.path.realpath(addon_path)
                App.Console.PrintMessage(
                    f"AI Workbench: Found addon at {addon_path}, real path: {real_path}\n"
                )
                return real_path
        except (AttributeError, NameError):
            pass

        # Try to find the addon directory by looking for our package.xml
        # Start from common FreeCAD addon locations
        possible_paths = [
            os.path.join(
                os.path.expanduser("~"),
                ".local",
                "share",
                "FreeCAD",
                "Mod",
                "freecad_ai_addon",
            ),
            os.path.join("/usr", "share", "freecad", "Mod", "freecad_ai_addon"),
            os.path.join(
                os.path.expanduser("~"), ".FreeCAD", "Mod", "freecad_ai_addon"
            ),
        ]

        for path in possible_paths:
            if os.path.exists(path):
                # Resolve symlinks to get the real path
                real_path = os.path.realpath(path)
                App.Console.PrintMessage(
                    f"AI Workbench: Checking {path} -> {real_path}\n"
                )
                if os.path.exists(os.path.join(real_path, "package.xml")):
                    App.Console.PrintMessage(
                        f"AI Workbench: Found package.xml in {real_path}\n"
                    )
                    return real_path

        # Final fallback - use current working directory
        App.Console.PrintMessage(
            "AI Workbench: Using current working directory as fallback\n"
        )
    return os.getcwd()


"""Resolve addon directory and add to sys.path for probing."""
addon_dir = get_addon_dir()
if addon_dir and addon_dir not in sys.path:
    sys.path.insert(0, addon_dir)


# Completely rewrite the AIWorkbench class with hardcoded icon path
class AIWorkbench(BaseWorkbench):
    """AI Workbench class for FreeCAD"""

    # Basic workbench metadata
    MenuText = "AI Assistant"
    ToolTip = "AI-powered design assistant with conversation and agent tools"

    # Set class-level icon - defer to __init__ to avoid NameError during class definition
    Icon = ""

    def __init__(self):
        """Initialize the AI workbench."""
        try:
            # Reaffirm icon at instance-level (some workflows expect it here too)
            icon_path = os.path.join(
                get_addon_dir(), "resources", "icons", "freecad_ai_addon.svg"
            )
            if os.path.exists(icon_path):
                self.Icon = icon_path
                AIWorkbench.Icon = icon_path  # Set class attribute too
                safe_print(f"AI Workbench: Icon set to {icon_path}")
            else:
                safe_print(f"AI Workbench: Icon not found at {icon_path}")
        except Exception as e:
            try:
                App.Console.PrintError(f"AI Workbench: Icon setup error: {e}\n")
            except Exception:
                pass
        safe_print("AI Workbench: Instance created")

    def Initialize(self):
        """Initialize workbench GUI elements"""
        try:
            safe_print("AI Workbench initializing...")
            # Create basic menu structure
            self.appendMenu("AI Assistant", [])
            safe_print("AI Workbench initialized successfully")
        except (ImportError, AttributeError) as e:
            try:
                App.Console.PrintError(f"AI Workbench initialization failed: {e}\n")
            except Exception:
                pass

    def Activated(self):
        """Called when workbench is activated"""
        safe_print("AI Assistant workbench activated")

    def Deactivated(self):
        """Called when workbench is deactivated"""
        safe_print("AI Assistant workbench deactivated")

    def GetClassName(self):
        """Return the class name for FreeCAD workbench registration"""
        return "Gui::PythonWorkbench"


# Explicitly export AIWorkbench so addon manager can find it
__all__ = ["AIWorkbench"]

# Register the workbench once GUI is available, without relying on module-level Initialize
try:
    if Gui is not None and hasattr(Gui, "addWorkbench"):
        Gui.addWorkbench(AIWorkbench())
        try:
            safe_print("AI Workbench: Registered workbench with FreeCAD")
        except NameError:
            # safe_print might not be available during early import
            print("AI Workbench: Registered workbench with FreeCAD")
    else:
        try:
            safe_print("AI Workbench: GUI not available; skipping registration")
        except NameError:
            print("AI Workbench: GUI not available; skipping registration")
except Exception as e:
    # Don't break import; just log the issue
    try:
        App.Console.PrintError(f"AI Workbench: Registration failed: {e}\n")
    except Exception:
        try:
            print(f"AI Workbench: Registration failed: {e}")
        except Exception:
            pass
