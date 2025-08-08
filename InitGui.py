"""
FreeCAD AI Addon - GUI Initialization Module

This module handles the initialization of the AI Workbench and related GUI
components when FreeCAD starts with a GUI interface.
"""

import FreeCAD as App
import FreeCADGui as Gui
import sys
import os

# Initialize WORKBENCH_ICON at module level to ensure it's always defined
WORKBENCH_ICON = ""


def get_addon_dir():
    """
    Get the addon directory in a way that is robust to the FreeCAD execution
    context, including handling symlinks properly.
    """
    try:
        # Try to get the directory from __file__ if available
        return os.path.dirname(__file__)
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


# Get the addon directory and set up icon path early
addon_dir = get_addon_dir()
if addon_dir and addon_dir not in sys.path:
    sys.path.insert(0, addon_dir)

# Try to set up the icon path before defining the workbench class
try:
    App.Console.PrintMessage(
        f"AI Workbench: Addon directory resolved to: {addon_dir}\n"
    )

    icon_path = os.path.join(
        addon_dir,
        "resources",
        "icons",
        "freecad_ai_addon.svg",
    )
    App.Console.PrintMessage(f"AI Workbench: Checking icon at: {icon_path}\n")

    if os.path.exists(icon_path):
        WORKBENCH_ICON = icon_path
        App.Console.PrintMessage(f"AI Workbench: Icon found at: {icon_path}\n")
    else:
        App.Console.PrintError(f"AI Workbench: Icon file not found at: {icon_path}\n")
        # List what's actually in the directory for debugging
        if os.path.exists(addon_dir):
            try:
                contents = os.listdir(addon_dir)
                App.Console.PrintMessage(
                    f"AI Workbench: Contents of {addon_dir}: {contents}\n"
                )
                # Also try to list icons directory contents
                icons_dir = os.path.join(addon_dir, "resources", "icons")
                if os.path.exists(icons_dir):
                    icons_contents = os.listdir(icons_dir)
                    App.Console.PrintMessage(
                        f"AI Workbench: Icons directory contents: {icons_contents}\n"
                    )
            except OSError as e:
                App.Console.PrintError(
                    f"AI Workbench: Could not list directory {addon_dir}: {e}\n"
                )
except (OSError, AttributeError, NameError) as e:
    App.Console.PrintError(f"AI Workbench: Icon setup error: {e}\n")


class AIWorkbench(Gui.Workbench):
    """AI Workbench class for FreeCAD"""

    MenuText = "AI Assistant"
    ToolTip = "AI-powered design assistant with conversation and agent tools"

    def __init__(self):
        """Initialize the AI workbench."""
        # Set icon in __init__ to avoid module-level scoping issues
        self.Icon = WORKBENCH_ICON
        App.Console.PrintMessage("AI Workbench: Instance created\n")

    def Initialize(self):
        """Initialize workbench GUI elements"""
        try:
            App.Console.PrintMessage("AI Workbench initializing...\n")

            # Create basic menu structure
            self.appendMenu("AI Assistant", [])

            App.Console.PrintMessage("AI Workbench initialized successfully\n")

        except (ImportError, AttributeError) as e:
            App.Console.PrintError(f"AI Workbench initialization failed: {e}\n")

    def Activated(self):
        """Called when workbench is activated"""
        App.Console.PrintMessage("AI Assistant workbench activated\n")

    def Deactivated(self):
        """Called when workbench is deactivated"""
        App.Console.PrintMessage("AI Assistant workbench deactivated\n")

    def GetClassName(self):
        """Return the class name for FreeCAD workbench registration"""
        return "Gui::PythonWorkbench"


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
