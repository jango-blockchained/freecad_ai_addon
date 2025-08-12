"""
FreeCAD Dockable Conversation Widget

Integration of the conversation widget as a dockable panel in FreeCAD.
"""

import FreeCAD as App
import FreeCADGui as Gui

try:
    from PySide import QtCore, QtGui as QtWidgets  # type: ignore
except Exception:
    try:
        from PySide2 import QtCore, QtWidgets  # type: ignore
    except Exception:
        from PySide6 import QtCore, QtWidgets  # type: ignore

from freecad_ai_addon.ui.enhanced_conversation_widget import EnhancedConversationWidget
from freecad_ai_addon.integration.context_providers import FreeCADContextProvider
from freecad_ai_addon.core.provider_manager import get_provider_manager
from freecad_ai_addon.utils.logging import get_logger

logger = get_logger("freecad_conversation_dock")


class FreeCADConversationDock(QtWidgets.QDockWidget):
    """Dockable conversation widget for FreeCAD"""

    def __init__(self, parent=None):
        super().__init__("AI Assistant", parent)
        self.setObjectName("AI_Conversation_Dock")

        # Create main widget
        self.conversation_widget = EnhancedConversationWidget()
        self.setWidget(self.conversation_widget)

        # Set up context provider
        self.context_provider = FreeCADContextProvider()

        # Connect signals
        self._connect_signals()

        # Configure dock
        self._configure_dock()

        logger.info("FreeCAD conversation dock initialized")

    @property
    def _conv_widget(self):
        """Helper property to access the underlying conversation widget"""
        return self.conversation_widget.get_conversation_widget()

    def _configure_dock(self):
        """Configure dock widget properties"""
        # Allow docking on left and right sides
        self.setAllowedAreas(
            QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea
        )

        # Set minimum and preferred sizes
        self.setMinimumWidth(300)
        self.setMinimumHeight(400)
        self.resize(400, 600)

        # Set dock features
        self.setFeatures(
            QtWidgets.QDockWidget.DockWidgetMovable
            | QtWidgets.QDockWidget.DockWidgetFloatable
            | QtWidgets.QDockWidget.DockWidgetClosable
        )

    def _connect_signals(self):
        """Connect conversation widget signals"""
        # Get the underlying conversation widget from enhanced widget
        self._conv_widget.message_sent.connect(self._handle_user_message)

        # Connect to FreeCAD selection changes
        try:
            from freecad_ai_addon.integration.freecad_integration import (
                setup_selection_observer,
            )

            setup_selection_observer(self._on_selection_changed)
        except ImportError:
            logger.warning("FreeCAD integration not available")

    def _handle_user_message(self, text: str, attachments: list):
        """Handle user message from conversation widget"""
        try:
            # Add context information
            context = self.context_provider.get_current_context()

            # Create enhanced message with context
            enhanced_message = self._create_enhanced_message(text, context)

            # Send to AI provider
            self._send_to_ai_provider(enhanced_message, attachments)

        except Exception as e:
            logger.error("Error handling user message: %s", str(e))
            self._conv_widget.add_error_message(f"Error processing message: {str(e)}")

    def _create_enhanced_message(self, user_text: str, context: dict) -> str:
        """Create enhanced message with FreeCAD context"""
        enhanced_parts = [user_text]

        # Add document context if available
        if context.get("active_document"):
            doc_info = context["active_document"]
            enhanced_parts.append(
                f"\n\n**Current FreeCAD Context:**\n"
                f"- Document: {doc_info.get('name', 'Unknown')}\n"
                f"- Objects: {len(doc_info.get('objects', []))}\n"
            )

        # Add selection context
        if context.get("selection"):
            selection_info = context["selection"]
            if selection_info.get("objects"):
                enhanced_parts.append(
                    f"- Selected: {', '.join(selection_info['objects'])}\n"
                )

        # Add workspace context
        if context.get("workbench"):
            enhanced_parts.append(f"- Active Workbench: {context['workbench']}\n")

        return "".join(enhanced_parts)

    async def _send_to_ai_provider(self, message: str, attachments: list):
        """Send message to AI provider and handle response"""
        try:
            provider_manager = get_provider_manager()

            # Get active provider
            active_providers = provider_manager.get_active_providers()
            if not active_providers:
                self._conv_widget.add_error_message(
                    "No AI providers are configured. "
                    "Please set up a provider in the settings."
                )
                return

            # Use first active provider
            provider_name = active_providers[0]
            provider = provider_manager.get_provider(provider_name)

            if not provider:
                self._conv_widget.add_error_message(
                    f"Provider {provider_name} not available."
                )
                return

            # Send message and get response
            response = await provider.send_message(message, attachments)

            # Add response to conversation
            self._conv_widget.add_assistant_message(response, provider=provider_name)

        except Exception as e:
            logger.error("Error sending to AI provider: %s", str(e))
            self._conv_widget.add_error_message(
                f"Error communicating with AI provider: {str(e)}"
            )

    def _on_selection_changed(self, selection_info: dict):
        """Handle FreeCAD selection changes"""
        try:
            # Optionally show selection context in conversation
            if selection_info.get("objects"):
                # Context message could be used for system notifications
                # For now, just log the selection change
                logger.debug("Selection changed: %s", selection_info["objects"])

        except Exception as e:
            logger.error("Error handling selection change: %s", str(e))

    def show_welcome_message(self):
        """Show welcome message when dock is first opened"""
        welcome_msg = (
            "Welcome to the **FreeCAD AI Assistant**!\n\n"
            "I can help you with:\n"
            "- Creating and modifying 3D models\n"
            "- Analyzing your designs\n"
            "- Suggesting improvements\n"
            "- Answering FreeCAD questions\n"
            "- Automating repetitive tasks\n\n"
            "Just type your question or request below!"
        )
        self._conv_widget.add_system_message(welcome_msg)

    def clear_conversation(self):
        """Clear the conversation and show welcome message"""
        self._conv_widget.conversation_area.clear_messages()
        self.show_welcome_message()

    def get_conversation_widget(self) -> EnhancedConversationWidget:
        """Get the underlying conversation widget"""
        return self.conversation_widget


class FreeCADConversationCommand:
    """Command to show/hide the conversation dock"""

    def GetResources(self):
        """Return command resources"""
        return {
            "Pixmap": "freecad_ai_addon.svg",
            "MenuText": "AI Chat",
            "ToolTip": "Open AI conversation interface",
            "Accel": "Ctrl+Shift+A",
        }

    def IsActive(self):
        """Return True if command should be active"""
        return True

    def Activated(self):
        """Execute the command"""
        try:
            # Get main window
            main_window = Gui.getMainWindow()

            # Check if dock already exists
            dock = main_window.findChild(
                FreeCADConversationDock, "AI_Conversation_Dock"
            )

            if dock is None:
                # Create new dock
                dock = FreeCADConversationDock(main_window)
                main_window.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)
                dock.show_welcome_message()

                logger.info("AI conversation dock created and added")
            else:
                # Toggle visibility
                if dock.isVisible():
                    dock.hide()
                else:
                    dock.show()
                    dock.raise_()

                logger.info("AI conversation dock visibility toggled")

        except Exception as e:
            logger.error("Error activating conversation command: %s", str(e))
            App.Console.PrintError(f"Failed to open AI chat: {e}\n")


class FreeCADAgentModeCommand:
    """Command to activate AI agent mode"""

    def GetResources(self):
        """Return command resources"""
        return {
            "Pixmap": "freecad_ai_addon.svg",
            "MenuText": "AI Agent Mode",
            "ToolTip": "Activate autonomous AI agent for FreeCAD operations",
            "Accel": "Ctrl+Shift+G",
        }

    def IsActive(self):
        """Return True if command should be active"""
        return True

    def Activated(self):
        """Execute the command"""
        try:
            # Get conversation dock
            main_window = Gui.getMainWindow()
            dock = main_window.findChild(
                FreeCADConversationDock, "AI_Conversation_Dock"
            )

            if dock is None:
                # Create dock first
                dock = FreeCADConversationDock(main_window)
                main_window.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)

            # Show agent mode activation message
            agent_message = (
                "🤖 **AI Agent Mode Activated**\n\n"
                "The AI agent can now perform autonomous actions in FreeCAD. "
                "Describe what you want to accomplish and I'll break it down "
                "into steps and execute them for you.\n\n"
                "*Note: You'll be asked to confirm potentially "
                "destructive operations.*"
            )
            dock.get_conversation_widget().add_system_message(agent_message)

            dock.show()
            dock.raise_()

            logger.info("AI agent mode activated")

        except Exception as e:
            logger.error("Error activating agent mode: %s", str(e))
            App.Console.PrintError(f"Failed to activate AI agent mode: {e}\n")


# Register commands with FreeCAD
def register_freecad_commands():
    """Register FreeCAD commands"""
    try:
        Gui.addCommand("AI_OpenChat", FreeCADConversationCommand())
        Gui.addCommand("AI_AgentMode", FreeCADAgentModeCommand())

        logger.info("FreeCAD AI commands registered successfully")

    except Exception as e:
        logger.error("Failed to register FreeCAD commands: %s", str(e))


# Utility function to get or create conversation dock
def get_conversation_dock() -> FreeCADConversationDock:
    """Get existing conversation dock or create new one"""
    main_window = Gui.getMainWindow()
    dock = main_window.findChild(FreeCADConversationDock, "AI_Conversation_Dock")

    if dock is None:
        dock = FreeCADConversationDock(main_window)
        main_window.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)
        dock.show_welcome_message()

    return dock
