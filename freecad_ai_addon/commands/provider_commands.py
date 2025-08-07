"""
Commands for Provider Management in FreeCAD AI Addon

Provides FreeCAD commands for managing AI providers and credentials.
"""

import FreeCADGui as Gui
from freecad_ai_addon.ui.provider_management import EnhancedProviderManagerDialog
from freecad_ai_addon.ui.security_dialogs import APIKeyInputDialog
from freecad_ai_addon.utils.logging import get_logger

logger = get_logger("commands")


class ProviderManagerCommand:
    """Command to open the provider management dialog"""

    def GetResources(self):
        """Return command resources"""
        return {
            "Pixmap": "ai_provider_settings.svg",
            "MenuText": "Manage AI Providers",
            "ToolTip": "Configure API keys and settings for AI providers",
        }

    def IsActive(self):
        """Command is always active"""
        return True

    def Activated(self):
        """Execute the command"""
        try:
            dialog = EnhancedProviderManagerDialog()
            dialog.exec()
        except Exception as e:
            logger.error("Failed to open provider manager: %s", str(e))
            Gui.SendMsgToActiveView("Failed to open provider manager")


class AddOpenAIProviderCommand:
    """Command to quickly add OpenAI provider"""

    def GetResources(self):
        """Return command resources"""
        return {
            "Pixmap": "ai_openai.svg",
            "MenuText": "Add OpenAI",
            "ToolTip": "Configure OpenAI API access",
        }

    def IsActive(self):
        """Command is always active"""
        return True

    def Activated(self):
        """Execute the command"""
        try:
            dialog = APIKeyInputDialog("openai")
            dialog.exec()
        except Exception as e:
            logger.error("Failed to open OpenAI configuration: %s", str(e))
            Gui.SendMsgToActiveView("Failed to open OpenAI configuration")


class AddAnthropicProviderCommand:
    """Command to quickly add Anthropic provider"""

    def GetResources(self):
        """Return command resources"""
        return {
            "Pixmap": "ai_anthropic.svg",
            "MenuText": "Add Anthropic",
            "ToolTip": "Configure Anthropic API access",
        }

    def IsActive(self):
        """Command is always active"""
        return True

    def Activated(self):
        """Execute the command"""
        try:
            dialog = APIKeyInputDialog("anthropic")
            dialog.exec()
        except Exception as e:
            logger.error("Failed to open Anthropic configuration: %s", str(e))
            Gui.SendMsgToActiveView("Failed to open Anthropic configuration")


class AddOllamaProviderCommand:
    """Command to quickly add Ollama provider"""

    def GetResources(self):
        """Return command resources"""
        return {
            "Pixmap": "ai_ollama.svg",
            "MenuText": "Add Ollama",
            "ToolTip": "Configure local Ollama access",
        }

    def IsActive(self):
        """Command is always active"""
        return True

    def Activated(self):
        """Execute the command"""
        try:
            dialog = APIKeyInputDialog("ollama")
            dialog.exec()
        except Exception as e:
            logger.error("Failed to open Ollama configuration: %s", str(e))
            Gui.SendMsgToActiveView("Failed to open Ollama configuration")


# Register commands
Gui.addCommand("AI_ProviderManager", ProviderManagerCommand())
Gui.addCommand("AI_AddOpenAI", AddOpenAIProviderCommand())
Gui.addCommand("AI_AddAnthropic", AddAnthropicProviderCommand())
Gui.addCommand("AI_AddOllama", AddOllamaProviderCommand())
