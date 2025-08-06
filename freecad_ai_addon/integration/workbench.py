import os
import FreeCADGui as Gui
import FreeCAD as App
from ..utils.logging import get_logger

logger = get_logger('workbench')


class AIWorkbench(Gui.Workbench):
    """AI Workbench class for FreeCAD"""

    MenuText = "AI Assistant"
    ToolTip = "AI-powered design assistant with conversation and agent capabilities"
    
    def __init__(self):
        """Initialize the AI Workbench"""
        logger.info("Initializing AI Workbench")
        
        # Set icon path
        self._set_icon_path()

    def _set_icon_path(self):
        """Set the workbench icon path"""
        try:
            # Get the addon directory
            addon_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            icon_path = os.path.join(addon_dir, "resources", "icons", "freecad_ai_addon.svg")
            
            if os.path.exists(icon_path):
                self.Icon = icon_path
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
            App.Console.PrintError(
                f"AI Workbench initialization failed: {e}\n")

    def _create_toolbars(self):
        """Create toolbars for the workbench"""
        try:
            # Import and register commands first
            self._register_commands()
            
            # Main AI toolbar
            self.appendToolbar("AI Assistant", [
                "AI_OpenChat"
            ])

            logger.info("AI toolbars created")
        except Exception as e:
            logger.error("Failed to create toolbars: %s", str(e))

    def _create_menus(self):
        """Create menus for the workbench"""
        try:
            # Main AI menu
            self.appendMenu("AI Assistant", ["AI_OpenChat"])

            logger.info("AI menus created")
        except Exception as e:
            logger.error("Failed to create menus: %s", str(e))

    def _register_commands(self):
        """Register FreeCAD commands for the workbench"""
        try:
            # Import and register the basic chat command
            from .commands import OpenChatCommand
            
            # Register commands with FreeCAD
            Gui.addCommand('AI_OpenChat', OpenChatCommand())
            
            logger.info("AI commands registered")
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
        """Return the class name"""
        return "AIWorkbench"


# Register commands that will be available in the workbench
def register_commands():
    """Register FreeCAD commands for the AI workbench"""
    try:
        # Import command classes (will be created later)
        # from freecad_ai_addon.integration.commands import (
        #     OpenChatCommand,
        #     AgentModeCommand,
        #     SettingsCommand
        # )

        # For now, create placeholder commands
        logger.info("AI commands registration prepared")

    except Exception as e:
        logger.error("Failed to register commands: %s", str(e))
