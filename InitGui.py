"""
FreeCAD AI Addon - GUI Initialization (InitGui.py)

Best-practice implementation of a Python workbench:
- Keep the workbench class in InitGui.py (GUI-only entrypoint)
- Set MenuText, ToolTip, and Icon as class attrs for Addon Manager
- Compute icon path dynamically relative to this file with robust fallbacks
- Keep Initialize lightweight; register toolbars/menus on demand
- Support headless mode by guarding FreeCADGui imports
"""

import os
import sys

# Then import FreeCAD modules (guarded to allow import outside FreeCAD)
try:
    import FreeCAD as App
except ImportError:  # Allow tests/imports without FreeCAD

    class _DummyConsole:
        def PrintMessage(self, msg):
            try:
                print(msg, end="" if msg.endswith("\n") else "")
            except Exception:
                pass

        def PrintError(self, msg):
            try:
                print(msg, end="" if msg.endswith("\n") else "")
            except Exception:
                pass

    class _DummyApp:
        Console = _DummyConsole()

        @staticmethod
        def getUserAppDataDir():
            # Typical FreeCAD user dir fallback
            return os.path.expanduser("~/.FreeCAD/")

    App = _DummyApp()

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
                try:
                    App.Console.PrintMessage(
                        f"AI Workbench: Found addon at {addon_path}, real path: {real_path}\n"
                    )
                except Exception:
                    pass
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
                try:
                    App.Console.PrintMessage(
                        f"AI Workbench: Checking {path} -> {real_path}\n"
                    )
                except Exception:
                    pass
                if os.path.exists(os.path.join(real_path, "package.xml")):
                    try:
                        App.Console.PrintMessage(
                            f"AI Workbench: Found package.xml in {real_path}\n"
                        )
                    except Exception:
                        pass
                    return real_path

        # Final fallback - use current working directory
        try:
            App.Console.PrintMessage(
                "AI Workbench: Using current working directory as fallback\n"
            )
        except Exception:
            pass
    return os.getcwd()


"""Resolve addon directory and add to sys.path for probing."""
addon_dir = get_addon_dir()
if addon_dir and addon_dir not in sys.path:
    sys.path.insert(0, addon_dir)

# Inform about initialization progress (mirroring example style)
try:
    App.Console.PrintMessage("FreeCAD AI Addon: Starting initialization...\n")
    App.Console.PrintMessage(f"FreeCAD AI Addon: Addon directory: {addon_dir}\n")
except Exception:
    # In non-FreeCAD environments, skip noisy output
    pass


def _compute_icon_path() -> str:
    """Compute absolute path to the workbench icon robustly.

    Best practice: external SVG referenced via dynamic path.
    """
    try:
        base = get_addon_dir()
    except Exception:
        base = os.getcwd()

    candidates = [
        os.path.join(base, "resources", "icons", "freecad_ai_addon.svg"),
    ]

    # Also try user Mod folder resolution if needed
    try:
        user_mod = os.path.join(App.getUserAppDataDir(), "Mod", "freecad_ai_addon")
        candidates.append(
            os.path.join(user_mod, "resources", "icons", "freecad_ai_addon.svg")
        )
    except Exception:
        pass

    for p in candidates:
        if p and os.path.exists(p):
            return os.path.realpath(p)
    return ""


# Precompute icon path once at import time for use in class attribute
_ICON_PATH = _compute_icon_path()


class AIWorkbench(BaseWorkbench):
    """AI Workbench class for FreeCAD (defined in InitGui.py per best-practice)."""

    # Metadata for Addon Manager / Workbench selector
    MenuText = "AI Assistant"
    ToolTip = "AI-powered design assistant with conversation and agent tools"
    # Provide class-level icon for Addon Manager discovery
    # Use dynamically computed path instead of hardcoded one
    Icon = _ICON_PATH

    def __init__(self):
        # Use dynamically computed icon path
        icon_path = _ICON_PATH
        if icon_path and os.path.exists(icon_path):
            try:
                self.Icon = icon_path
                type(self).Icon = icon_path  # keep class attr synced
            except Exception:
                self.Icon = icon_path
        safe_print("AI Workbench: Instance created")

    def Initialize(self):
        """Initialize workbench GUI elements (keep minimal)."""
        try:
            safe_print("AI Workbench initializing…")
            # Register/append minimal UI only if GUI is available
            if Gui is not None and hasattr(self, "appendToolbar"):
                # Register commands lazily to avoid heavy imports at startup
                try:
                    from freecad_ai_addon.integration.commands import (
                        OpenChatCommand,
                    )

                    # Also import manufacturing command so it registers itself (side-effect import)
                    from freecad_ai_addon.commands import (
                        manufacturing_commands as _mfg_cmds,
                    )  # noqa: F401

                    if hasattr(Gui, "addCommand"):
                        Gui.addCommand("AI_OpenChat", OpenChatCommand())
                    self.appendToolbar(
                        "AI Assistant",
                        ["AI_OpenChat", "AI_ShowManufacturingAdvice"],
                    )
                    self.appendMenu(
                        "AI Assistant",
                        ["AI_OpenChat", "AI_ShowManufacturingAdvice"],
                    )
                except Exception:
                    # Fall back to an empty menu/toolbar if commands unavailable
                    self.appendMenu("AI Assistant", [])
            else:
                safe_print("AI Workbench initialized (console/headless mode)")
        except Exception as init_error:
            try:
                App.Console.PrintError(
                    f"AI Workbench initialization failed: {init_error}\n"
                )
            except Exception:
                pass

    def Activated(self):
        safe_print("AI Assistant workbench activated")

    def Deactivated(self):
        safe_print("AI Assistant workbench deactivated")

    def GetClassName(self):
        return "Gui::PythonWorkbench"


__all__ = ["AIWorkbench"]

# Addon metadata (optional)
__version__ = "0.7.11"
__title__ = "FreeCAD AI"
__author__ = "jango-blockchained"
__url__ = "https://github.com/jango-blockchained/mcp-freecad"

# Register the workbench with robust error handling (like the example)
try:
    if Gui is not None and hasattr(Gui, "addWorkbench") and "AIWorkbench" in globals():
        # Try to list existing workbenches (optional)
        try:
            if hasattr(Gui, "listWorkbenches"):
                existing = list(Gui.listWorkbenches().keys())
                App.Console.PrintMessage(
                    f"FreeCAD AI Addon: Existing workbenches: {existing}\n"
                )
        except Exception as e:
            try:
                App.Console.PrintWarning(
                    f"FreeCAD AI Addon: Could not list existing workbenches: {e}\n"
                )
            except Exception:
                pass

        # Create workbench instance
        try:
            _wb = AIWorkbench()
            App.Console.PrintMessage(
                "FreeCAD AI Addon: Workbench instance created successfully\n"
            )
        except Exception as e:
            App.Console.PrintError(
                f"FreeCAD AI Addon: Failed to create workbench instance: {e}\n"
            )
            _wb = None

        # Register if instance available
        if _wb is not None:
            try:
                Gui.addWorkbench(_wb)
                App.Console.PrintMessage(
                    "FreeCAD AI Addon: Workbench registered successfully\n"
                )
            except KeyError as ke:
                # Some FreeCAD versions raise KeyError if already exists
                if "already" in str(ke).lower():
                    try:
                        App.Console.PrintWarning(
                            f"FreeCAD AI Addon: Workbench already registered, skipping: {ke}\n"
                        )
                    except Exception:
                        pass
                else:
                    App.Console.PrintError(
                        f"FreeCAD AI Addon: Workbench registration KeyError: {ke}\n"
                    )
            except AttributeError as ae:
                App.Console.PrintError(
                    f"FreeCAD AI Addon: FreeCADGui.addWorkbench not available: {ae}\n"
                )
            except Exception as e:
                App.Console.PrintError(
                    f"FreeCAD AI Addon: Workbench registration failed: {e}\n"
                )
    else:
        # GUI not available or class missing
        if Gui is None:
            safe_print("AI Workbench: GUI not available; skipping registration")
        else:
            safe_print(
                "AI Workbench: AIWorkbench class not available at import time; skipping registration"
            )
except Exception as e:
    # Do not break addon import
    try:
        App.Console.PrintError(
            f"FreeCAD AI Addon: Initialization error during registration: {e}\n"
        )
    except Exception:
        pass
