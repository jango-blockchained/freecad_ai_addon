"""
FreeCAD AI Addon - GUI Initialization (InitGui.py)

Robust, test-friendly initialization of the AI Assistant workbench.
Works both inside FreeCAD GUI and in headless/test environments.
"""

from __future__ import annotations

import os
import sys

# --- FreeCAD import guards -------------------------------------------------
try:  # Try to import real FreeCAD modules
    import FreeCAD as App  # type: ignore

    try:
        import FreeCADGui as Gui  # type: ignore
    except ImportError:
        Gui = None  # type: ignore
except Exception:  # Not running inside FreeCAD or GUI
    # Minimal dummies so tests can import this module safely
    class _DummyConsole:
        def PrintMessage(self, msg):
            print(msg)

        def PrintError(self, msg):
            print(f"ERROR: {msg}")

        def PrintWarning(self, msg):
            print(f"WARNING: {msg}")

    class _DummyApp:  # Mimic App subset used here
        Console = _DummyConsole()

        @staticmethod
        def getUserAppDataDir():
            # Reasonable default; FreeCAD changes this per platform
            return os.path.expanduser("~/.FreeCAD/")

    App = _DummyApp()  # type: ignore
    Gui = None  # type: ignore

# Determine a base workbench class that doesn't explode in headless mode
if Gui is not None and hasattr(Gui, "Workbench"):
    BaseWorkbench = Gui.Workbench  # type: ignore[attr-defined]
else:

    class BaseWorkbench(object):  # Fallback for tests/headless
        def __init__(self):
            pass


# --- Utilities --------------------------------------------------------------
def safe_print(message: str) -> None:
    """Print a message via FreeCAD console if available, else stdout."""
    try:
        App.Console.PrintMessage(f"{message}\n")  # type: ignore[attr-defined]
    except Exception:
        print(message)


def get_addon_dir() -> str:
    """Resolve the addon root directory robustly.

    Search order:
    1) This file's directory (repo installation)
    2) FreeCAD user Mod path (Addon Manager installs)
    3) Current working directory (last resort)
    """
    # 1) Resolve from this file
    try:
        here = os.path.dirname(os.path.realpath(__file__))
        return here
    except Exception:
        pass

    # 2) Resolve from FreeCAD user Mod dir
    try:
        user_mod_path = os.path.join(
            App.getUserAppDataDir(), "Mod", "freecad_ai_addon"  # type: ignore[attr-defined]
        )
        if os.path.exists(user_mod_path):
            return os.path.realpath(user_mod_path)
    except Exception:
        pass

    # 3) Fallback
    return os.getcwd()


def _addon_root() -> str:
    """Alias for addon root; kept for compatibility with other modules."""
    return get_addon_dir()


def _compute_icon_path() -> str:
    """Compute absolute path to the workbench icon.

    Returns empty string if not found (contract: Icon must be a string).
    """
    candidates = []
    try:
        # Primary: resources/icons next to this file (repo layout)
        base = _addon_root()
        icon_path = os.path.join(base, "resources", "icons", "freecad_ai_addon.svg")
        candidates.append(icon_path)
    except Exception:
        pass  # Silently continue

    # Also try FreeCAD user Mod installation location
    try:
        user_mod = os.path.join(App.getUserAppDataDir(), "Mod", "freecad_ai_addon")  # type: ignore[attr-defined]
        icon_path = os.path.join(user_mod, "resources", "icons", "freecad_ai_addon.svg")
        candidates.append(icon_path)
    except Exception:
        pass  # Silently continue

    for p in candidates:
        try:
            if p and os.path.exists(p):
                real_path = os.path.realpath(p)
                return real_path
        except Exception:
            continue
    # Contract with tests: Icon must be str, may be empty
    return ""


# Ensure addon directory is importable (useful for tests or direct runs)
_ADDON_DIR = get_addon_dir()
if _ADDON_DIR not in sys.path:
    sys.path.insert(0, _ADDON_DIR)

safe_print("FreeCAD AI Addon: Initializing InitGui.py ...")
safe_print(f"FreeCAD AI Addon: Addon directory resolved to: {_ADDON_DIR}")


# Pre-compute icon path once so metadata tools and tests can read it
_ICON_PATH = ""  # Initialize with default value first
try:
    _ICON_PATH = _compute_icon_path()
    if _ICON_PATH:
        safe_print(f"FreeCAD AI Addon: Icon path set to: {_ICON_PATH}")
    else:
        safe_print("FreeCAD AI Addon: No icon file found, using empty icon")
except Exception as e:
    try:
        safe_print(f"FreeCAD AI Addon: Warning - Could not compute icon path: {e}")
    except Exception:
        pass  # Even safe_print failed, but _ICON_PATH is still defined as ""


# --- Workbench --------------------------------------------------------------
class AIWorkbench(BaseWorkbench):
    """AI-powered design assistant workbench."""

    # Class-level metadata used by FreeCAD and tests
    MenuText = "AI Assistant"
    ToolTip = "AI-powered design assistant with conversation and agent tools"
    # Keep class-level Icon a plain string to avoid any NameError during import
    Icon = ""

    def __init__(self):
        super().__init__()
        # Keep instance and class Icon in sync
        try:
            # Avoid direct NameError if globals are altered during FreeCAD import
            icon_path = globals().get("_ICON_PATH", "")
            if not isinstance(icon_path, str):
                icon_path = ""
            if not icon_path:
                try:
                    icon_path = _compute_icon_path()
                except Exception:
                    icon_path = ""
            self.Icon = icon_path or ""
        except Exception:
            self.Icon = ""
        try:
            # Also update the class attribute at runtime for Addon Manager discovery
            type(self).Icon = self.Icon
        except Exception:
            pass

    # Robust print helper that doesn't depend on module-level symbols
    def _print(self, message: str) -> None:
        try:
            sp = globals().get("safe_print")
            if callable(sp):
                sp(message)
                return
        except Exception:
            pass
        # Fallbacks if safe_print is unavailable
        try:
            App.Console.PrintMessage(f"{message}\n")  # type: ignore[attr-defined]
        except Exception:
            try:
                print(message)
            except Exception:
                pass

    # Lifecycle methods (GUI-safe; no-ops in tests)
    def Initialize(self) -> None:
        """Set up toolbars, menus, and register commands when GUI is available."""
        self._print("AI Workbench: Initializing GUI ...")
        # Import and register commands lazily to avoid issues outside GUI
        try:
            if Gui is None or not hasattr(Gui, "addCommand"):
                return  # Nothing to register headlessly

            registered_commands = []  # collect only successfully registered commands

            # Core AI commands
            try:
                from freecad_ai_addon.integration.commands import (
                    OpenChatCommand,
                    ProviderManagerCommand,
                )

                Gui.addCommand("AI_OpenChat", OpenChatCommand())
                registered_commands.append("AI_OpenChat")
                Gui.addCommand("AI_ProviderManager", ProviderManagerCommand())
                registered_commands.append("AI_ProviderManager")
            except Exception as e:
                self._print(f"AI Workbench: Failed to register core commands: {e}")

            # Manufacturing command self-registers on import when GUI is present
            try:
                import freecad_ai_addon.commands.manufacturing_commands  # noqa: F401

                # If FreeCAD exposes listCommands, include only if present
                try:
                    if hasattr(Gui, "listCommands"):
                        if "AI_ShowManufacturingAdvice" in Gui.listCommands():
                            registered_commands.append("AI_ShowManufacturingAdvice")
                    else:
                        # Optimistically include; toolbar/menu creation will still work
                        registered_commands.append("AI_ShowManufacturingAdvice")
                except Exception:
                    pass
            except Exception as e:
                self._print(f"AI Workbench: Failed to load manufacturing commands: {e}")

            # Build toolbar/menu only with commands that actually exist
            commands = registered_commands
            try:
                if commands:
                    if hasattr(self, "appendToolbar"):
                        self.appendToolbar("AI Assistant", commands)
                    if hasattr(self, "appendMenu"):
                        self.appendMenu("AI Assistant", commands)
                else:
                    self._print(
                        "AI Workbench: No commands registered; skipping toolbars/menus"
                    )
            except Exception as e:
                self._print(f"AI Workbench: Failed to create toolbars/menus: {e}")
        except Exception as e:
            self._print(f"AI Workbench: Initialize failed: {e}")

    def Activated(self) -> None:
        self._print("AI Assistant workbench activated.")

    def Deactivated(self) -> None:
        self._print("AI Assistant workbench deactivated.")

    def GetClassName(self) -> str:
        return "Gui::PythonWorkbench"


# Export symbol for tests and FreeCAD discovery
globals()["AIWorkbench"] = AIWorkbench


# --- Workbench Registration -------------------------------------------------
try:
    if Gui is not None and hasattr(Gui, "addWorkbench"):
        safe_print("AI Workbench: Registering workbench ...")
        # FreeCAD expects the class, not an instance
        Gui.addWorkbench(AIWorkbench)
        safe_print("AI Workbench: Registration successful.")
    else:
        safe_print("AI Workbench: GUI not available, skipping registration.")
except Exception as e:
    safe_print(f"AI Workbench: Failed to register workbench: {e}")


# --- Addon metadata ---------------------------------------------------------
__version__ = "0.9.0"
__title__ = "FreeCAD AI"
__author__ = "jango-blockchained"
__url__ = "https://github.com/jango-blockchained/mcp-freecad"
