"""
AI Workbench for FreeCAD

Provides the main workbench interface for the AI Addon.
"""

import FreeCADGui as Gui
import FreeCAD as App
from freecad_ai_addon.utils.logging import get_logger

logger = get_logger('workbench')


class AIWorkbench(Gui.Workbench):
    """AI Workbench class for FreeCAD"""

    MenuText = "AI Assistant"
    ToolTip = "AI-powered design assistant with conversation and agent capabilities"
    Icon = """
        /* Simple SVG icon placeholder - will be replaced with actual icon */
        <svg width="16" height="16" xmlns="http://www.w3.org/2000/svg">
            <circle cx="8" cy="8" r="6" fill="#3498db"/>
            <text x="8" y="12" text-anchor="middle" fill="white" font-size="10">AI</text>
        </svg>
    """

    def __init__(self):
        """Initialize the AI Workbench"""
        logger.info("Initializing AI Workbench")

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
            # Main AI toolbar
            self.appendToolbar("AI Assistant", [
                "AI_OpenChat",
                "AI_AgentMode",
                "separator",
                "AI_ProviderManager"
            ])

            # Provider setup toolbar
            self.appendToolbar("AI Providers", [
                "AI_AddOpenAI",
                "AI_AddAnthropic",
                "AI_AddOllama"
            ])

            logger.info("AI toolbars created")
        except Exception as e:
            logger.error("Failed to create toolbars: %s", str(e))

    def _create_menus(self):
        """Create menus for the workbench"""
        try:
            # Main AI menu
            self.appendMenu("AI Assistant", ["AI_OpenChat", "AI_AgentMode"])

            # Provider management submenu
            self.appendMenu(["AI Assistant", "Providers"], [
                "AI_ProviderManager",
                "separator",
                "AI_AddOpenAI",
                "AI_AddAnthropic",
                "AI_AddOllama"
            ])

            logger.info("AI menus created")
        except Exception as e:
            logger.error("Failed to create menus: %s", str(e))

    def _create_dockable_widgets(self):
        """Create dockable widgets for the workbench"""
        try:
            # Import and register conversation dock commands
            from freecad_ai_addon.integration.freecad_conversation_dock import (
                register_freecad_commands
            )
            register_freecad_commands()

            logger.info("Dockable widgets and commands registered")
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
