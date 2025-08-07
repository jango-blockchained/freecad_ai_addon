"""
Enhanced Conversation Widget with Agent Integration

Extends the base conversation widget to include agent control panels
and seamless integration with the AI Agent Framework.
"""

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QTabWidget,
    QFrame,
    QLabel,
)

from freecad_ai_addon.ui.conversation_widget import ConversationWidget
from freecad_ai_addon.integration.agent_conversation_integration import (
    AgentConversationIntegration,
    AgentControlPanel,
    AgentStatusPanel,
)
from freecad_ai_addon.utils.logging import get_logger

logger = get_logger("enhanced_conversation_widget")


class EnhancedConversationWidget(QWidget):
    """
    Enhanced conversation widget with integrated agent controls

    This widget combines the standard conversation interface with
    agent control panels, providing a unified interface for both
    regular AI conversations and autonomous agent operations.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.conversation_widget: Optional[ConversationWidget] = None
        self.agent_integration: Optional[AgentConversationIntegration] = None
        self.control_panel: Optional[AgentControlPanel] = None
        self.status_panel: Optional[AgentStatusPanel] = None

        self._setup_ui()
        self._setup_agent_integration()

        logger.info("Enhanced conversation widget initialized")

    def _setup_ui(self):
        """Set up the enhanced UI layout"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # Main splitter for conversation and controls
        main_splitter = QSplitter(Qt.Horizontal)

        # Left side: Conversation area
        self.conversation_widget = ConversationWidget()
        main_splitter.addWidget(self.conversation_widget)

        # Right side: Agent controls
        controls_widget = self._create_controls_widget()
        main_splitter.addWidget(controls_widget)

        # Set splitter proportions (conversation takes more space)
        main_splitter.setSizes([700, 300])
        main_splitter.setStretchFactor(0, 1)  # Conversation can stretch
        main_splitter.setStretchFactor(1, 0)  # Controls fixed

        layout.addWidget(main_splitter)

    def _create_controls_widget(self) -> QWidget:
        """Create the agent controls widget"""
        controls_widget = QWidget()
        controls_widget.setMinimumWidth(280)
        controls_widget.setMaximumWidth(400)

        layout = QVBoxLayout(controls_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Title
        title_frame = QFrame()
        title_frame.setStyleSheet(
            """
            QFrame {
                background-color: #f0f0f0;
                border-radius: 8px;
                padding: 8px;
            }
        """
        )
        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(8, 8, 8, 8)

        title_label = QLabel("🤖 Agent Controls")
        title_label.setStyleSheet(
            """
            QLabel {
                font-weight: bold;
                font-size: 14px;
                color: #333;
            }
        """
        )
        title_layout.addWidget(title_label)
        title_layout.addStretch()

        layout.addWidget(title_frame)

        # Tabbed interface for different control panels
        tab_widget = QTabWidget()

        # Control Panel Tab
        self.control_panel = AgentControlPanel()
        tab_widget.addTab(self.control_panel, "Settings")

        # Status Panel Tab
        self.status_panel = AgentStatusPanel()
        tab_widget.addTab(self.status_panel, "Status")

        # Agent Info Tab
        info_panel = self._create_info_panel()
        tab_widget.addTab(info_panel, "Info")

        layout.addWidget(tab_widget)

        return controls_widget

    def _create_info_panel(self) -> QWidget:
        """Create the agent information panel"""
        info_widget = QWidget()
        layout = QVBoxLayout(info_widget)
        layout.setContentsMargins(5, 5, 5, 5)

        # Agent capabilities info
        capabilities_label = QLabel(
            """
        <h3>Available Agents</h3>
        <p><b>🔧 Geometry Agent:</b><br/>
        Creates and modifies 3D geometric objects including primitives,
        boolean operations, and transformations.</p>

        <p><b>✏️ Sketch Agent:</b><br/>
        Handles 2D sketching operations, constraints, and geometric
        construction lines.</p>

        <p><b>📊 Analysis Agent:</b><br/>
        Performs geometric analysis, measurements, and validation
        of CAD models.</p>
        
        <h3>Operation Modes</h3>
        <p><b>Interactive:</b> Asks before each operation</p>
        <p><b>Semi-Autonomous:</b> Asks for critical operations only</p>
        <p><b>Autonomous:</b> Full autonomy with safety checks</p>
        
        <h3>Safety Features</h3>
        <p>• Automatic validation of all operations</p>
        <p>• User approval for model modifications</p>
        <p>• Operation rollback capabilities</p>
        <p>• Maximum operation limits</p>
        """
        )

        capabilities_label.setWordWrap(True)
        capabilities_label.setStyleSheet(
            """
            QLabel {
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 12px;
                font-size: 11px;
                line-height: 1.4;
            }
        """
        )

        layout.addWidget(capabilities_label)
        layout.addStretch()

        return info_widget

    def _setup_agent_integration(self):
        """Set up the agent integration"""
        try:
            # Create agent integration
            self.agent_integration = AgentConversationIntegration(
                self.conversation_widget
            )

            # Replace control and status panels with integrated ones
            if self.control_panel:
                self.control_panel.setParent(None)
            if self.status_panel:
                self.status_panel.setParent(None)

            self.control_panel = self.agent_integration.get_control_panel()
            self.status_panel = self.agent_integration.get_status_panel()

            # Update the tabs
            self._update_control_tabs()

            logger.info("Agent integration setup complete")

        except Exception as e:
            logger.error(f"Failed to setup agent integration: {e}")
            self._show_integration_error(str(e))

    def _update_control_tabs(self):
        """Update the control tabs with integrated panels"""
        # Find the tab widget and update tabs
        for child in self.findChildren(QTabWidget):
            if child.count() >= 2:
                # Replace the first two tabs
                child.removeTab(1)  # Remove status tab
                child.removeTab(0)  # Remove control tab

                # Add integrated panels
                child.insertTab(0, self.control_panel, "Settings")
                child.insertTab(1, self.status_panel, "Status")
                break

    def _show_integration_error(self, error: str):
        """Show an error message if integration fails"""
        error_widget = QWidget()
        layout = QVBoxLayout(error_widget)

        error_label = QLabel(
            f"""
        <h3>⚠️ Agent Integration Error</h3>
        <p>Failed to initialize agent framework:</p>
        <p><code>{error}</code></p>
        <p>You can still use the conversation interface normally.</p>
        """
        )
        error_label.setWordWrap(True)
        error_label.setStyleSheet(
            """
            QLabel {
                background-color: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 8px;
                padding: 12px;
                color: #856404;
            }
        """
        )

        layout.addWidget(error_label)
        layout.addStretch()

        # Add error tab
        for child in self.findChildren(QTabWidget):
            if child.count() >= 1:
                child.addTab(error_widget, "⚠️ Error")
                break

    def get_conversation_widget(self) -> ConversationWidget:
        """Get the conversation widget for external access"""
        return self.conversation_widget

    def get_agent_integration(self) -> Optional[AgentConversationIntegration]:
        """Get the agent integration for external access"""
        return self.agent_integration

    def is_agent_mode_enabled(self) -> bool:
        """Check if agent mode is currently enabled"""
        if self.agent_integration:
            return not self.agent_integration.is_agent_busy()
        return False

    def send_message(self, text: str, attachments: list = None):
        """Send a message through the conversation widget"""
        if attachments is None:
            attachments = []
        self.conversation_widget.input_area.text_input.setPlainText(text)
        self.conversation_widget.input_area.attachments = attachments.copy()
        self.conversation_widget.input_area._send_message()

    def add_system_message(self, text: str):
        """Add a system message to the conversation"""
        self.conversation_widget.add_system_message(text)

    def clear_conversation(self):
        """Clear the conversation history"""
        self.conversation_widget.conversation_area.clear_messages()

    def export_conversation(self, file_path: str):
        """Export the conversation to a file"""
        self.conversation_widget._export_conversation_to_file(file_path)

    def load_conversation(self, messages: list):
        """Load a conversation from saved data"""
        self.conversation_widget.load_conversation(messages)

    def get_conversation_history(self):
        """Get the current conversation history"""
        return self.conversation_widget.get_conversation_history()
