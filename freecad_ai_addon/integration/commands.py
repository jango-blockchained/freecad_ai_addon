"""
FreeCAD Commands for AI Workbench

This module contains all FreeCAD command classes for the AI workbench.
"""

import FreeCAD as App
import FreeCADGui as Gui
from PySide6 import QtCore, QtWidgets

from ..utils.logging import get_logger

logger = get_logger('commands')


class OpenChatCommand:
    """Command to open the AI chat interface"""
    
    def GetResources(self):
        """Return command resources (icon, tooltip, etc.)"""
        return {
            'Pixmap': 'freecad_ai_addon_chat.svg',
            'MenuText': 'Open AI Chat',
            'ToolTip': 'Open the AI conversation interface',
            'Accel': 'Ctrl+Shift+A'
        }
    
    def Activated(self):
        """Execute the command"""
        try:
            logger.info("Opening AI Chat interface")
            
            # Get the main window
            main_window = Gui.getMainWindow()
            
            # Check if the dock widget already exists
            dock_widget = main_window.findChild(
                QtWidgets.QDockWidget,
                "AI_Conversation_Dock"
            )
            
            if dock_widget is None:
                # Create new dock widget
                from .freecad_conversation_dock import (
                    FreeCADConversationDock
                )
                
                dock_widget = FreeCADConversationDock(main_window)
                main_window.addDockWidget(
                    QtCore.Qt.RightDockWidgetArea,
                    dock_widget
                )
                logger.info("Created new AI conversation dock widget")
            else:
                logger.info("AI conversation dock widget already exists")
            
            # Show and raise the dock widget
            dock_widget.show()
            dock_widget.raise_()
            dock_widget.activateWindow()
            
        except Exception as e:
            logger.error("Failed to open AI chat: %s", str(e))
            App.Console.PrintError(f"Failed to open AI chat: {e}\n")
    
    def IsActive(self):
        """Return True if the command should be active"""
        return True


class ProviderManagerCommand:
    """Command to open the AI provider manager"""
    
    def GetResources(self):
        """Return command resources"""
        return {
            'Pixmap': 'freecad_ai_addon_settings.svg',
            'MenuText': 'AI Provider Settings',
            'ToolTip': 'Manage AI provider configurations',
            'Accel': 'Ctrl+Shift+P'
        }
    
    def Activated(self):
        """Execute the command"""
        try:
            logger.info("Opening AI Provider Manager")
            
            # For now, just show a message
            from PySide6.QtWidgets import QMessageBox
            
            msg = QMessageBox()
            msg.setWindowTitle("AI Provider Manager")
            msg.setText(
                "AI Provider Manager will be implemented in the next phase."
            )
            msg.setInformativeText(
                "This feature will allow you to configure OpenAI, Anthropic, "
                "and other AI providers."
            )
            msg.exec()
            
        except Exception as e:
            logger.error("Failed to open provider manager: %s", str(e))
            App.Console.PrintError(f"Failed to open provider manager: {e}\n")
    
    def IsActive(self):
        """Return True if the command should be active"""
        return True
