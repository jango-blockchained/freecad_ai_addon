"""
FreeCAD AI Addon - GUI Initialization Module

This module handles the initialization of the AI Workbench and related GUI
components when FreeCAD starts with a GUI interface.
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


# Import the full-featured workbench from the integration module
try:
    from freecad_ai_addon.integration.workbench import (
        AIWorkbench as IntegratedAIWorkbench,
    )

    # Use the integrated workbench with full functionality
    AIWorkbench = IntegratedAIWorkbench
    safe_print("AI Workbench: Using integrated workbench with full functionality")
    # Ensure class-level Icon is present for Addon Manager handle acquisition
    try:
        if not getattr(AIWorkbench, "Icon", ""):
            # Compute a conservative default icon path relative to this file
            base_dir = os.path.dirname(os.path.realpath(__file__))
            candidate = os.path.join(
                base_dir, "resources", "icons", "freecad_ai_addon.svg"
            )
            if os.path.exists(candidate):
                AIWorkbench.Icon = candidate
    except Exception:
        pass
except ImportError as e:
    safe_print(
        f"AI Workbench: Could not import integrated workbench ({e}), using fallback"
    )

    # Fallback to basic workbench if integration fails
    class AIWorkbench(BaseWorkbench):
        """AI Workbench class for FreeCAD (fallback)"""

        # Basic workbench metadata
        MenuText = "AI Assistant"
        ToolTip = "AI-powered design assistant with conversation and agent tools"

        # Set class-level icon - defer to __init__ to avoid NameError during class definition
        Icon = ""

        def __init__(self):
            """Initialize the AI workbench."""

            # Local safe printer that doesn't depend on a global symbol existing yet
            def _sp(msg: str):
                # Try module-level safe_print if available
                try:
                    _gp = globals().get("safe_print")
                    if callable(_gp):
                        _gp(msg)
                        return
                except (NameError, AttributeError):
                    # Fall through to basic printing
                    pass
                # Fallbacks
                if "App" in globals() and hasattr(App, "Console"):
                    try:
                        App.Console.PrintMessage(f"{msg}\n")
                        return
                    except (AttributeError, TypeError):
                        # Fall back to print
                        pass
                print(msg)

            # Compute icon path without relying on a global helper during early import
            try:
                base_dir = None
                try:
                    base_dir = os.path.dirname(os.path.realpath(__file__))
                except NameError:
                    # When __file__ is not available in FreeCAD context, use App data dir
                    try:
                        user_data_dir = App.getUserAppDataDir()
                        candidate = os.path.join(
                            user_data_dir, "Mod", "freecad_ai_addon"
                        )
                        if os.path.exists(candidate):
                            base_dir = os.path.realpath(candidate)
                    except (AttributeError, NameError, TypeError):
                        base_dir = None

                if not base_dir:
                    # Final fallback: try common locations
                    for p in [
                        os.path.join(
                            os.path.expanduser("~"),
                            ".local",
                            "share",
                            "FreeCAD",
                            "Mod",
                            "freecad_ai_addon",
                        ),
                        os.path.join(
                            "/usr", "share", "freecad", "Mod", "freecad_ai_addon"
                        ),
                        os.path.join(
                            os.path.expanduser("~"),
                            ".FreeCAD",
                            "Mod",
                            "freecad_ai_addon",
                        ),
                    ]:
                        if os.path.exists(p):
                            base_dir = os.path.realpath(p)
                            break

                # Build icon path and set both instance and class attributes
                icon_path = os.path.join(
                    base_dir or os.getcwd(),
                    "resources",
                    "icons",
                    "freecad_ai_addon.svg",
                )
                if os.path.exists(icon_path):
                    self.Icon = icon_path
                    AIWorkbench.Icon = icon_path
                    _sp(f"AI Workbench: Icon set to {icon_path}")
                else:
                    _sp(f"AI Workbench: Icon not found at {icon_path}")
            except (OSError, RuntimeError, ValueError, TypeError) as icon_error:
                try:
                    App.Console.PrintError(
                        f"AI Workbench: Icon setup error: {icon_error}\n"
                    )
                except (AttributeError, NameError):
                    # As a last resort, write to stdout
                    print(f"AI Workbench: Icon setup error: {icon_error}")
            _sp("AI Workbench: Instance created")

        def Initialize(self):
            """Initialize workbench GUI elements"""
            try:
                safe_print("AI Workbench initializing...")
                # Only try to create menus if we have GUI capabilities
                if hasattr(self, "appendMenu"):
                    self.appendMenu("AI Assistant", [])
                    safe_print("AI Workbench initialized successfully (fallback mode)")
                else:
                    safe_print(
                        "AI Workbench initialized successfully (console mode - no GUI)"
                    )
            except (ImportError, AttributeError) as init_error:
                try:
                    App.Console.PrintError(
                        f"AI Workbench initialization failed: {init_error}\n"
                    )
                except (AttributeError, NameError, TypeError):
                    pass

        def Activated(self):
            """Called when workbench is activated"""
            safe_print("AI Assistant workbench activated (fallback mode)")

        def Deactivated(self):
            """Called when workbench is deactivated"""
            safe_print("AI Assistant workbench deactivated (fallback mode)")

        def GetClassName(self):
            """Return the class name for FreeCAD workbench registration"""
            return "Gui::PythonWorkbench"


# Explicitly export AIWorkbench so addon manager can find it
__all__ = ["AIWorkbench"]

# Register the workbench once GUI is available, without relying on module-level Initialize
try:
    cls = globals().get("AIWorkbench")
    if Gui is not None and hasattr(Gui, "addWorkbench") and cls is not None:
        Gui.addWorkbench(cls())
        # Log registration without hard dependency on safe_print symbol
        try:
            _gp = globals().get("safe_print")
            if callable(_gp):
                _gp("AI Workbench: Registered workbench with FreeCAD")
            else:
                raise NameError("safe_print unavailable")
        except (NameError, AttributeError, TypeError):
            if hasattr(App, "Console"):
                try:
                    App.Console.PrintMessage(
                        "AI Workbench: Registered workbench with FreeCAD\n"
                    )
                except (AttributeError, TypeError):
                    print("AI Workbench: Registered workbench with FreeCAD")
            else:
                print("AI Workbench: Registered workbench with FreeCAD")
    elif Gui is not None and hasattr(Gui, "addWorkbench") and cls is None:
        # Class not available yet; skip registration but keep import successful
        try:
            _gp = globals().get("safe_print")
            if callable(_gp):
                _gp(
                    "AI Workbench: AIWorkbench class not available at import time; skipping registration"
                )
            else:
                raise NameError("safe_print unavailable")
        except (NameError, AttributeError, TypeError):
            print(
                "AI Workbench: AIWorkbench class not available at import time; skipping registration"
            )
    else:
        try:
            _gp = globals().get("safe_print")
            if callable(_gp):
                _gp("AI Workbench: GUI not available; skipping registration")
            else:
                raise NameError("safe_print unavailable")
        except (NameError, AttributeError, TypeError):
            print("AI Workbench: GUI not available; skipping registration")
except (RuntimeError, TypeError, ValueError, OSError) as e:
    # Don't break import; just log the issue
    try:
        App.Console.PrintError(f"AI Workbench: Registration failed: {e}\n")
    except (AttributeError, NameError):
        print(f"AI Workbench: Registration failed: {e}")
