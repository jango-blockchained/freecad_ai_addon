import os
import FreeCAD as App
from ..utils.logging import get_logger

logger = get_logger("workbench")

# Handle GUI import gracefully
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


def _compute_icon_path():
    """Compute absolute path to the workbench icon as robustly as possible."""
    try:
        # Start from this file and ascend to addon root (…/freecad_ai_addon/..)
        # integration/workbench.py -> integration -> freecad_ai_addon -> repo/addon root
        root_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        )
    except Exception:
        root_dir = os.getcwd()

    candidates = [
        os.path.join(root_dir, "resources", "icons", "freecad_ai_addon.svg"),
    ]

    # Also try resolving via FreeCAD's user Mod folder if needed
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


# Compute once at import time so Addon Manager can read class attribute
_ICON_PATH = _compute_icon_path()


class AIWorkbench(BaseWorkbench):
    """AI Workbench class for FreeCAD"""

    MenuText = "AI Assistant"
    ToolTip = "AI-powered design assistant with conversation and agent capabilities"
    # Provide class-level Icon so Addon Manager can discover it without instantiation
    Icon = _ICON_PATH or ""

    def __init__(self):
        """Initialize the AI Workbench"""
        logger.info("Initializing AI Workbench")

        # Set icon path
        self._set_icon_path()

    def _set_icon_path(self):
        """Set the workbench icon path"""
        try:
            # Prefer the precomputed path; fall back to runtime computation
            icon_path = _ICON_PATH
            if not icon_path:
                addon_dir = os.path.dirname(
                    os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
                )
                icon_path = os.path.join(
                    addon_dir, "resources", "icons", "freecad_ai_addon.svg"
                )

            if icon_path and os.path.exists(icon_path):
                self.Icon = icon_path
                # Keep class attribute in sync too
                try:
                    type(self).Icon = icon_path
                except Exception:
                    pass
                logger.info(f"Workbench icon set to: {icon_path}")
            else:
                logger.warning(f"Icon file not found at: {icon_path}")
                # Use a simple text-based fallback
                self.Icon = ""  # Empty string to avoid icon issues
        except Exception as e:
            logger.error(f"Failed to set icon: {e}")
            self.Icon = ""  # Empty string to avoid icon issues

    def Initialize(self):
        """Initialize workbench GUI elements"""
        try:
            logger.info("Setting up AI Workbench GUI")

            # Create toolbars and menus
            self._create_toolbars()
            self._create_menus()
            self._create_dockable_widgets()

            logger.info("AI Workbench initialized successfully")

        except Exception as e:
            logger.error("Failed to initialize AI Workbench: %s", str(e))
            App.Console.PrintError(f"AI Workbench initialization failed: {e}\n")

    def _create_toolbars(self):
        """Create toolbars for the workbench"""
        try:
            # Import and register commands first
            self._register_commands()

            # Main AI toolbar
            self.appendToolbar("AI Assistant", ["AI_OpenChat", "AI_ProviderManager"])

            logger.info("AI toolbars created")
        except Exception as e:
            logger.error("Failed to create toolbars: %s", str(e))

    def _create_menus(self):
        """Create menus for the workbench"""
        try:
            # Main AI menu
            self.appendMenu("AI Assistant", ["AI_OpenChat", "AI_ProviderManager"])

            logger.info("AI menus created")
        except Exception as e:
            logger.error("Failed to create menus: %s", str(e))

    def _register_commands(self):
        """Register FreeCAD commands for the workbench"""
        try:
            # Import and register the commands
            from .commands import OpenChatCommand, ProviderManagerCommand

            # Register commands with FreeCAD
            Gui.addCommand("AI_OpenChat", OpenChatCommand())
            Gui.addCommand("AI_ProviderManager", ProviderManagerCommand())

            logger.info("AI commands registered: AI_OpenChat, AI_ProviderManager")
        except Exception as e:
            logger.error("Failed to register commands: %s", str(e))

    def _create_dockable_widgets(self):
        """Create dockable widgets for the workbench"""
        try:
            # For now, just log that this is where dockable widgets
            # would be created. The actual dock widget will be created
            # when the OpenChat command is executed
            logger.info("Dockable widgets setup completed")
        except Exception as e:
            logger.error("Failed to create dockable widgets: %s", str(e))

    def Activated(self):
        """Called when workbench is activated"""
        logger.info("AI Workbench activated")
        App.Console.PrintMessage("AI Assistant workbench activated\n")

    def Deactivated(self):
        """Called when workbench is deactivated"""
        logger.info("AI Workbench deactivated")

    def ContextMenu(self, recipient):
        """Define context menu for the workbench"""
        # This will be expanded later with context-sensitive options
        pass

    def GetClassName(self):
        """Return the FreeCAD class identifier expected for Python workbenches."""
        return "Gui::PythonWorkbench"
