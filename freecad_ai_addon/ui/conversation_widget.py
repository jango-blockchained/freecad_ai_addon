"""
Conversation Widget for AI Chat Interface

Modern chat interface for FreeCAD AI interactions with markdown rendering,
code highlighting, message history, and advanced features.
"""

import json
import re
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

try:
    from PySide import QtCore as QtCoreCompat  # type: ignore
    from PySide import QtGui as QtWidgetsCompat  # type: ignore

    QtWidgets = QtWidgetsCompat
    QtCore = QtCoreCompat
    Signal = QtCoreCompat.Signal
    QTimer = QtCoreCompat.QTimer
    from PySide.QtGui import (
        QWidget,
        QVBoxLayout,
        QHBoxLayout,
        QTextEdit,
        QPushButton,
        QScrollArea,
        QFrame,
        QSplitter,
        QLabel,
        QFileDialog,
        QToolButton,
        QTextBrowser,
        QMessageBox,
        QFont,
        QColor,
        QSyntaxHighlighter,
        QTextCharFormat,
    )  # type: ignore
except Exception:
    try:
        from PySide2 import QtWidgets, QtCore  # type: ignore
        from PySide2.QtCore import Signal, QTimer  # type: ignore
        from PySide2.QtGui import QFont, QColor, QSyntaxHighlighter, QTextCharFormat  # type: ignore
        from PySide2.QtWidgets import (
            QWidget,
            QVBoxLayout,
            QHBoxLayout,
            QTextEdit,
            QPushButton,
            QScrollArea,
            QFrame,
            QSplitter,
            QLabel,
            QFileDialog,
            QToolButton,
            QTextBrowser,
            QMessageBox,
        )  # type: ignore
    except Exception:
        from PySide6 import QtWidgets, QtCore
        from PySide6.QtCore import Signal, QTimer
        from PySide6.QtGui import QFont, QColor, QSyntaxHighlighter, QTextCharFormat
        from PySide6.QtWidgets import (
            QWidget,
            QVBoxLayout,
            QHBoxLayout,
            QTextEdit,
            QPushButton,
            QScrollArea,
            QFrame,
            QSplitter,
            QLabel,
            QFileDialog,
            QToolButton,
            QTextBrowser,
            QMessageBox,
        )

from freecad_ai_addon.utils.logging import get_logger
from freecad_ai_addon.utils.config import get_config_manager

logger = get_logger("conversation_widget")


class MessageType(Enum):
    """Message types in conversation"""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    ERROR = "error"
    INFO = "info"


@dataclass
class ChatMessage:
    """Chat message data structure"""

    id: str
    type: MessageType
    content: str
    timestamp: datetime
    provider: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    attachments: List[str] = field(default_factory=list)
    thread_id: Optional[str] = None
    parent_id: Optional[str] = None


class MarkdownHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for markdown content"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_highlighting_rules()

    def _setup_highlighting_rules(self):
        """Set up highlighting rules for markdown"""
        self.highlighting_rules = []

        # Headers
        header_format = QTextCharFormat()
        header_format.setForeground(QColor("#2196F3"))
        header_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append((r"^#{1,6} .*", header_format))

        # Bold text
        bold_format = QTextCharFormat()
        bold_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append((r"\*\*([^*]+)\*\*", bold_format))

        # Italic text
        italic_format = QTextCharFormat()
        italic_format.setFontItalic(True)
        self.highlighting_rules.append((r"\*([^*]+)\*", italic_format))

        # Inline code
        code_format = QTextCharFormat()
        code_format.setForeground(QColor("#E91E63"))
        code_format.setBackground(QColor("#F5F5F5"))
        code_format.setFontFamily("Consolas, Monaco, monospace")
        self.highlighting_rules.append((r"`([^`]+)`", code_format))

        # Code blocks
        code_block_format = QTextCharFormat()
        code_block_format.setForeground(QColor("#333333"))
        code_block_format.setBackground(QColor("#F8F8F8"))
        code_block_format.setFontFamily("Consolas, Monaco, monospace")
        self.highlighting_rules.append((r"```[\s\S]*?```", code_block_format))

        # Links
        link_format = QTextCharFormat()
        link_format.setForeground(QColor("#1976D2"))
        link_format.setUnderlineStyle(QTextCharFormat.SingleUnderline)
        self.highlighting_rules.append((r"\[([^\]]+)\]\([^)]+\)", link_format))

        # Lists
        list_format = QTextCharFormat()
        list_format.setForeground(QColor("#4CAF50"))
        self.highlighting_rules.append((r"^[\s]*[-*+] .*", list_format))
        self.highlighting_rules.append((r"^[\s]*\d+\. .*", list_format))

    def highlightBlock(self, text):
        """Apply highlighting to a text block"""
        for pattern, format_obj in self.highlighting_rules:
            expression = re.compile(pattern, re.MULTILINE)
            for match in expression.finditer(text):
                start = match.start()
                length = match.end() - match.start()
                self.setFormat(start, length, format_obj)


class MessageWidget(QFrame):
    """Widget for displaying a single chat message"""

    def __init__(self, message: ChatMessage, parent=None):
        super().__init__(parent)
        self.message = message
        self._setup_ui()
        self._apply_styling()

    def _setup_ui(self):
        """Set up the message UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(5)

        # Header with metadata
        header_layout = QHBoxLayout()

        # Message type indicator
        type_label = QLabel(self._get_type_display())
        type_label.setFont(QFont("", 9, QFont.Bold))
        header_layout.addWidget(type_label)

        # Provider info
        if self.message.provider:
            provider_label = QLabel(f"via {self.message.provider}")
            provider_label.setFont(QFont("", 8))
            provider_label.setStyleSheet("color: #666;")
            header_layout.addWidget(provider_label)

        # Timestamp
        timestamp_label = QLabel(self.message.timestamp.strftime("%H:%M:%S"))
        timestamp_label.setFont(QFont("", 8))
        timestamp_label.setStyleSheet("color: #888;")
        header_layout.addStretch()
        header_layout.addWidget(timestamp_label)

        layout.addLayout(header_layout)

        # Message content
        content_widget = QTextBrowser()
        content_widget.setOpenExternalLinks(True)
        content_widget.setMinimumHeight(50)
        content_widget.setMaximumHeight(400)

        # Apply markdown highlighting for assistant messages
        if self.message.type == MessageType.ASSISTANT:
            self.highlighter = MarkdownHighlighter(content_widget.document())

        # Set content based on message type
        if self.message.type in [MessageType.ASSISTANT, MessageType.SYSTEM]:
            content_widget.setMarkdown(self.message.content)
        else:
            content_widget.setPlainText(self.message.content)

        layout.addWidget(content_widget)

        # Add interactive elements for assistant messages with code
        if (
            self.message.type == MessageType.ASSISTANT
            and self._contains_executable_code(self.message.content)
        ):
            self._add_interactive_elements(layout)

        # Attachments
        if self.message.attachments:
            self._add_attachments(layout)

    def _get_type_display(self) -> str:
        """Get display text for message type"""
        type_map = {
            MessageType.USER: "You",
            MessageType.ASSISTANT: "AI Assistant",
            MessageType.SYSTEM: "System",
            MessageType.ERROR: "Error",
            MessageType.INFO: "Info",
        }
        return type_map.get(self.message.type, "Unknown")

    def _apply_styling(self):
        """Apply styling based on message type"""
        base_style = """
            QFrame {
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                background-color: #FFFFFF;
                margin: 2px;
            }
        """

        if self.message.type == MessageType.USER:
            self.setStyleSheet(
                base_style
                + """
                QFrame {
                    background-color: #E3F2FD;
                    border-color: #2196F3;
                }
            """
            )
        elif self.message.type == MessageType.ASSISTANT:
            self.setStyleSheet(
                base_style
                + """
                QFrame {
                    background-color: #F1F8E9;
                    border-color: #4CAF50;
                }
            """
            )
        elif self.message.type == MessageType.ERROR:
            self.setStyleSheet(
                base_style
                + """
                QFrame {
                    background-color: #FFEBEE;
                    border-color: #F44336;
                }
            """
            )
        else:
            self.setStyleSheet(base_style)

    def _add_attachments(self, layout):
        """Add attachment display to the message"""
        attachments_frame = QFrame()
        attachments_layout = QHBoxLayout(attachments_frame)

        for attachment in self.message.attachments:
            attachment_label = QLabel(f"📎 {attachment}")
            attachment_label.setStyleSheet("color: #1976D2;")
            attachments_layout.addWidget(attachment_label)

        layout.addWidget(attachments_frame)

    def _contains_executable_code(self, content: str) -> bool:
        """Check if message content contains executable Python/FreeCAD code"""
        import re

        # Look for code blocks with FreeCAD-specific content
        code_pattern = r"```(?:python|py)?\n(.*?)\n```"
        matches = re.findall(code_pattern, content, re.DOTALL)

        for code in matches:
            if "App." in code or "Gui." in code or "FreeCAD" in code:
                return True
        return False

    def _add_interactive_elements(self, layout):
        """Add interactive elements for code execution"""
        try:
            from freecad_ai_addon.ui.interactive_elements import (
                create_interactive_message_widget,
            )

            interactive_widget = create_interactive_message_widget(self.message.content)
            layout.addWidget(interactive_widget)

        except ImportError as e:
            logger.warning(f"Could not import interactive elements: {e}")
            # Fallback to basic implementation
            self._add_basic_code_buttons(layout)

    def _add_basic_code_buttons(self, layout):
        """Add basic code execution buttons as fallback"""
        # Extract code blocks
        import re

        code_pattern = r"```(?:python|py)?\n(.*?)\n```"
        matches = re.findall(code_pattern, self.message.content, re.DOTALL)

        for i, code in enumerate(matches):
            if "App." in code or "Gui." in code:
                button_frame = QFrame()
                button_layout = QHBoxLayout(button_frame)

                execute_btn = QPushButton(f"Execute Code Block {i+1}")
                execute_btn.setStyleSheet(
                    """
                    QPushButton {
                        background-color: #4CAF50;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 6px 12px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #45a049;
                    }
                """
                )

                copy_btn = QPushButton("Copy")
                copy_btn.setStyleSheet(
                    """
                    QPushButton {
                        background-color: #2196F3;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 6px 12px;
                    }
                """
                )

                # Connect signals with lambda to capture code
                execute_btn.clicked.connect(
                    lambda checked, c=code: self._execute_code(c)
                )
                copy_btn.clicked.connect(lambda checked, c=code: self._copy_code(c))

                button_layout.addWidget(execute_btn)
                button_layout.addWidget(copy_btn)
                button_layout.addStretch()

                layout.addWidget(button_frame)

    def _execute_code(self, code: str):
        """Execute code block"""
        try:
            import FreeCAD as App
            import FreeCADGui as Gui

            if not App.ActiveDocument:
                App.newDocument("AI_Generated")

            # Execute the code
            exec(code, {"App": App, "Gui": Gui})

            # Show success message briefly
            self.sender().setText("✓ Executed")
            self.sender().setStyleSheet(
                self.sender().styleSheet().replace("#4CAF50", "#2196F3")
            )

            # Reset after 3 seconds
            QTimer.singleShot(3000, lambda: self._reset_execute_button())

        except ImportError:
            QMessageBox.warning(
                self, "FreeCAD Required", "FreeCAD is required for code execution"
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Execution Error", f"Error executing code: {str(e)}"
            )

    def _copy_code(self, code: str):
        """Copy code to clipboard"""
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(code)

        # Show feedback
        self.sender().setText("✓ Copied")
        QTimer.singleShot(2000, lambda: self.sender().setText("Copy"))

    def _reset_execute_button(self):
        """Reset execute button appearance"""
        # Find execute buttons and reset them
        for button in self.findChildren(QPushButton):
            text = button.text()
            if "Execute Code Block" in text or text == "✓ Executed":
                new_text = text.replace("✓ Executed", "Execute Code Block")
                button.setText(new_text)
                button.setStyleSheet(button.styleSheet().replace("#2196F3", "#4CAF50"))


class ConversationArea(QScrollArea):
    """Scrollable area for displaying conversation messages"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.messages: List[ChatMessage] = []
        self._setup_ui()

    def _setup_ui(self):
        """Set up the conversation area UI"""
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

        # Container widget
        self.container = QWidget()
        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)
        self.layout.addStretch()  # Push messages to top

        self.setWidget(self.container)

    def add_message(self, message: ChatMessage):
        """Add a message to the conversation"""
        self.messages.append(message)

        # Create message widget
        message_widget = MessageWidget(message)

        # Insert before the stretch
        self.layout.insertWidget(self.layout.count() - 1, message_widget)

        # Scroll to bottom
        QTimer.singleShot(100, self._scroll_to_bottom)

    def clear_messages(self):
        """Clear all messages from the conversation"""
        self.messages.clear()

        # Remove all widgets except stretch
        for i in reversed(range(self.layout.count() - 1)):
            item = self.layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()

    def _scroll_to_bottom(self):
        """Scroll to the bottom of the conversation"""
        scrollbar = self.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())


class MessageInputArea(QWidget):
    """Input area for typing and sending messages"""

    message_sent = Signal(str, list)  # message_text, attachments

    def __init__(self, parent=None):
        super().__init__(parent)
        self.attachments: List[str] = []
        self._setup_ui()

    def _setup_ui(self):
        """Set up the input area UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Input controls
        input_layout = QHBoxLayout()

        # Attachment button
        self.attach_button = QToolButton()
        self.attach_button.setText("📎")
        self.attach_button.setToolTip("Attach files")
        self.attach_button.clicked.connect(self._attach_files)
        input_layout.addWidget(self.attach_button)

        # Text input
        self.text_input = QTextEdit()
        self.text_input.setMaximumHeight(100)
        self.text_input.setMinimumHeight(40)
        self.text_input.setPlaceholderText(
            "Type your message here... (Shift+Enter for new line)"
        )
        self.text_input.installEventFilter(self)
        input_layout.addWidget(self.text_input)

        # Send button
        self.send_button = QPushButton("Send")
        self.send_button.setMinimumWidth(80)
        self.send_button.clicked.connect(self._send_message)
        input_layout.addWidget(self.send_button)

        layout.addLayout(input_layout)

        # Attachments display
        self.attachments_frame = QFrame()
        self.attachments_layout = QHBoxLayout(self.attachments_frame)
        self.attachments_frame.hide()
        layout.addWidget(self.attachments_frame)

    def eventFilter(self, obj, event):
        """Handle keyboard events for text input"""
        if obj == self.text_input and event.type() == QtCore.QEvent.KeyPress:
            if (
                event.key() == QtCore.Qt.Key_Return
                or event.key() == QtCore.Qt.Key_Enter
            ):
                if event.modifiers() == QtCore.Qt.ShiftModifier:
                    # Shift+Enter: insert new line
                    return False
                else:
                    # Enter: send message
                    self._send_message()
                    return True
        return False

    def _attach_files(self):
        """Open file dialog to attach files"""
        files, _ = QFileDialog.getOpenFileNames(
            self, "Attach Files", "", "All Files (*)"
        )

        for file_path in files:
            if file_path not in self.attachments:
                self.attachments.append(file_path)

        self._update_attachments_display()

    def _update_attachments_display(self):
        """Update the attachments display"""
        # Clear existing attachments
        for i in reversed(range(self.attachments_layout.count())):
            item = self.attachments_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()

        # Add attachment labels
        for attachment in self.attachments:
            filename = attachment.split("/")[-1]
            label = QLabel(f"📎 {filename}")
            label.setStyleSheet("color: #1976D2; padding: 2px;")

            # Remove button
            remove_btn = QPushButton("×")
            remove_btn.setMaximumSize(20, 20)
            remove_btn.clicked.connect(
                lambda checked, f=attachment: self._remove_attachment(f)
            )

            container = QWidget()
            container_layout = QHBoxLayout(container)
            container_layout.setContentsMargins(0, 0, 0, 0)
            container_layout.addWidget(label)
            container_layout.addWidget(remove_btn)

            self.attachments_layout.addWidget(container)

        # Show/hide attachments frame
        if self.attachments:
            self.attachments_frame.show()
        else:
            self.attachments_frame.hide()

    def _remove_attachment(self, file_path: str):
        """Remove an attachment"""
        if file_path in self.attachments:
            self.attachments.remove(file_path)
            self._update_attachments_display()

    def _send_message(self):
        """Send the current message"""
        text = self.text_input.toPlainText().strip()
        if text:
            self.message_sent.emit(text, self.attachments.copy())
            self.text_input.clear()
            self.attachments.clear()
            self._update_attachments_display()

    def clear_input(self):
        """Clear the input area"""
        self.text_input.clear()
        self.attachments.clear()
        self._update_attachments_display()


class ConversationWidget(QWidget):
    """Main conversation widget combining all chat components"""

    message_sent = Signal(str, list)  # message_text, attachments

    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_manager = get_config_manager()
        self._setup_ui()
        self._connect_signals()

        logger.info("Conversation widget initialized")

    def _generate_message_id(self) -> str:
        """Generate unique message ID"""
        timestamp = datetime.now().timestamp()
        message_count = len(self.conversation_area.messages)
        return f"msg_{message_count}_{timestamp}"

    def _setup_ui(self):
        """Set up the main UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toolbar
        toolbar = self._create_toolbar()
        layout.addWidget(toolbar)

        # Main content area
        splitter = QSplitter(QtCore.Qt.Vertical)

        # Conversation area
        self.conversation_area = ConversationArea()
        splitter.addWidget(self.conversation_area)

        # Input area
        self.input_area = MessageInputArea()
        splitter.addWidget(self.input_area)

        # Set splitter proportions
        splitter.setSizes([400, 100])
        layout.addWidget(splitter)

    def _create_toolbar(self) -> QWidget:
        """Create the conversation toolbar"""
        toolbar = QWidget()
        toolbar.setMaximumHeight(40)
        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(5, 5, 5, 5)

        # Title
        title_label = QLabel("AI Assistant")
        title_label.setFont(QFont("", 10, QFont.Bold))
        layout.addWidget(title_label)

        layout.addStretch()

        # Search button
        search_btn = QPushButton("🔍")
        search_btn.setMaximumSize(30, 30)
        search_btn.setToolTip("Search messages")
        search_btn.clicked.connect(self._show_search)
        layout.addWidget(search_btn)

        # Clear button
        clear_btn = QPushButton("🗑")
        clear_btn.setMaximumSize(30, 30)
        clear_btn.setToolTip("Clear conversation")
        clear_btn.clicked.connect(self._clear_conversation)
        layout.addWidget(clear_btn)

        # Export button
        export_btn = QPushButton("💾")
        export_btn.setMaximumSize(30, 30)
        export_btn.setToolTip("Export conversation")
        export_btn.clicked.connect(self._export_conversation)
        layout.addWidget(export_btn)

        # Tools menu (Sketch/Geometry quick actions)
        tools_btn = QToolButton()
        tools_btn.setText("🛠")
        tools_btn.setToolTip("Quick CAD tools")
        tools_btn.setPopupMode(QToolButton.InstantPopup)

        try:
            from PySide6.QtWidgets import QMenu  # type: ignore
        except Exception:  # PySide2 fallback
            from PySide2.QtWidgets import QMenu  # type: ignore

        tools_menu = QMenu(tools_btn)

        # Geometry submenu
        geom_menu = tools_menu.addMenu("Geometry")
        action_create_box = geom_menu.addAction("Create Box…")
        action_create_box.triggered.connect(self._quick_create_box)

        # Sketch submenu
        sketch_menu = tools_menu.addMenu("Sketch")
        action_add_slot = sketch_menu.addAction("Add Slot…")
        action_add_slot.triggered.connect(self._quick_add_slot)

        action_rect_pattern = sketch_menu.addAction("Rectangular Pattern…")
        action_rect_pattern.triggered.connect(self._quick_rectangular_pattern)

        action_polar_pattern = sketch_menu.addAction("Polar Pattern…")
        action_polar_pattern.triggered.connect(self._quick_polar_pattern)

        action_linear_pattern = sketch_menu.addAction("Linear Pattern…")
        action_linear_pattern.triggered.connect(self._quick_linear_pattern)

        # Constraints submenu
        constraints_menu = tools_menu.addMenu("Constraints")
        action_coincident = constraints_menu.addAction("Add Coincident…")
        action_coincident.triggered.connect(self._quick_add_coincident)

        action_angle = constraints_menu.addAction("Add Angle…")
        action_angle.triggered.connect(self._quick_add_angle)

        tools_btn.setMenu(tools_menu)
        layout.addWidget(tools_btn)

        return toolbar

    def _connect_signals(self):
        """Connect internal signals"""
        self.input_area.message_sent.connect(self._handle_message_sent)

    def _handle_message_sent(self, text: str, attachments: List[str]):
        """Handle message sent from input area"""
        # Create user message
        message = ChatMessage(
            id=self._generate_message_id(),
            type=MessageType.USER,
            content=text,
            timestamp=datetime.now(),
            attachments=attachments,
        )

        # Add to conversation
        self.add_message(message)

        # Emit signal for external handling
        self.message_sent.emit(text, attachments)

    def add_message(self, message: ChatMessage):
        """Add a message to the conversation"""
        self.conversation_area.add_message(message)

    def add_user_message(
        self, text: str, attachments: Optional[List[str]] = None
    ) -> ChatMessage:
        """Add a user message to the conversation"""
        message = ChatMessage(
            id=self._generate_message_id(),
            type=MessageType.USER,
            content=text,
            timestamp=datetime.now(),
            attachments=attachments or [],
        )
        self.add_message(message)
        return message

    def add_assistant_message(
        self, text: str, provider: Optional[str] = None
    ) -> ChatMessage:
        """Add an assistant message to the conversation"""
        message = ChatMessage(
            id=self._generate_message_id(),
            type=MessageType.ASSISTANT,
            content=text,
            timestamp=datetime.now(),
            provider=provider,
        )
        self.add_message(message)
        return message

    def add_system_message(self, text: str) -> ChatMessage:
        """Add a system message to the conversation"""
        message = ChatMessage(
            id=self._generate_message_id(),
            type=MessageType.SYSTEM,
            content=text,
            timestamp=datetime.now(),
        )
        self.add_message(message)
        return message

    def add_error_message(self, text: str) -> ChatMessage:
        """Add an error message to the conversation"""
        message = ChatMessage(
            id=self._generate_message_id(),
            type=MessageType.ERROR,
            content=text,
            timestamp=datetime.now(),
        )
        self.add_message(message)
        return message

    def _show_search(self):
        """Show search dialog"""
        from PySide6.QtWidgets import QInputDialog

        search_text, ok = QInputDialog.getText(
            self, "Search Messages", "Enter search term:"
        )

        if ok and search_text.strip():
            self._search_messages(search_text.strip())

    def _search_messages(self, search_term: str):
        """Search for messages containing the search term"""
        found_count = 0
        search_term_lower = search_term.lower()

        # Highlight matching messages and count them
        for message in self.conversation_area.messages:
            if search_term_lower in message.content.lower():
                found_count += 1

        # Show search results
        if found_count > 0:
            self.add_system_message(
                f"Found {found_count} message(s) containing '{search_term}'"
            )
        else:
            self.add_system_message(f"No messages found containing '{search_term}'")

    def _clear_conversation(self):
        """Clear the conversation after confirmation"""
        reply = QtWidgets.QMessageBox.question(
            self,
            "Clear Conversation",
            "Are you sure you want to clear the entire conversation?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No,
        )

        if reply == QtWidgets.QMessageBox.Yes:
            self.conversation_area.clear_messages()
            self.add_system_message("Conversation cleared.")

    def _export_conversation(self):
        """Export conversation to file"""
        if not self.conversation_area.messages:
            QtWidgets.QMessageBox.information(self, "Export", "No messages to export.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Conversation",
            f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON Files (*.json);;Text Files (*.txt)",
        )

        if file_path:
            try:
                if file_path.endswith(".json"):
                    self._export_as_json(file_path)
                else:
                    self._export_as_text(file_path)

                QtWidgets.QMessageBox.information(
                    self, "Export", f"Conversation exported to {file_path}"
                )
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self, "Export Error", f"Failed to export: {str(e)}"
                )

    def _export_as_json(self, file_path: str):
        """Export conversation as JSON"""
        data = []
        for message in self.conversation_area.messages:
            data.append(
                {
                    "id": message.id,
                    "type": message.type.value,
                    "content": message.content,
                    "timestamp": message.timestamp.isoformat(),
                    "provider": message.provider,
                    "metadata": message.metadata,
                    "attachments": message.attachments,
                }
            )

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _export_as_text(self, file_path: str):
        """Export conversation as plain text"""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("FreeCAD AI Conversation Export\n")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"Generated: {timestamp}\n")
            f.write("=" * 50 + "\n\n")

            for message in self.conversation_area.messages:
                f.write(f"[{message.timestamp.strftime('%H:%M:%S')}] ")
                f.write(f"{message.type.value.upper()}")
                if message.provider:
                    f.write(f" (via {message.provider})")
                f.write(":\n")
                f.write(f"{message.content}\n")
                if message.attachments:
                    f.write(f"Attachments: {', '.join(message.attachments)}\n")
                f.write("\n")

    # ==============================
    # Quick CAD Tools (Geometry)
    # ==============================

    def _quick_create_box(self):
        """Prompt for dimensions and create a box via ActionLibrary."""
        try:
            from PySide6.QtWidgets import QInputDialog  # type: ignore
        except Exception:
            from PySide2.QtWidgets import QInputDialog  # type: ignore

        try:
            from freecad_ai_addon.agent.action_library import ActionLibrary
        except Exception as e:
            self.add_error_message(f"ActionLibrary unavailable: {e}")
            return

        # Gather parameters
        length, ok1 = QInputDialog.getDouble(
            self, "Create Box", "Length (mm):", 50.0, 0.01
        )
        if not ok1:
            return
        width, ok2 = QInputDialog.getDouble(
            self, "Create Box", "Width (mm):", 30.0, 0.01
        )
        if not ok2:
            return
        height, ok3 = QInputDialog.getDouble(
            self, "Create Box", "Height (mm):", 20.0, 0.01
        )
        if not ok3:
            return

        try:
            lib = ActionLibrary()
            result = lib.execute_operation(
                "box",
                {
                    "length": length,
                    "width": width,
                    "height": height,
                    "name": "BoxFromUI",
                },
            )
            status = result.get("status")
            if status == "success":
                self.add_system_message(
                    f"Created box: {result['result'].get('object_name', 'Box')} ({length}×{width}×{height})"
                )
            else:
                self.add_error_message(
                    f"Box creation failed: {result.get('error', 'Unknown error')}"
                )
        except Exception as e:
            self.add_error_message(f"Box creation error: {e}")

    # ==============================
    # Quick CAD Tools (Sketch)
    # ==============================

    def _quick_add_slot(self):
        """Prompt and add a slot to a sketch via SketchActionLibrary."""
        try:
            from PySide6.QtWidgets import QInputDialog  # type: ignore
        except Exception:
            from PySide2.QtWidgets import QInputDialog  # type: ignore

        try:
            from freecad_ai_addon.agent.sketch_action_library import SketchActionLibrary
        except Exception as e:
            self.add_error_message(f"SketchActionLibrary unavailable: {e}")
            return

        sketch_name, ok0 = QInputDialog.getText(self, "Add Slot", "Sketch name:")
        if not ok0 or not sketch_name:
            return
        x1, ok1 = QInputDialog.getDouble(self, "Add Slot", "Start X:", 0.0)
        if not ok1:
            return
        y1, ok2 = QInputDialog.getDouble(self, "Add Slot", "Start Y:", 0.0)
        if not ok2:
            return
        x2, ok3 = QInputDialog.getDouble(self, "Add Slot", "End X:", 50.0)
        if not ok3:
            return
        y2, ok4 = QInputDialog.getDouble(self, "Add Slot", "End Y:", 0.0)
        if not ok4:
            return
        width, ok5 = QInputDialog.getDouble(self, "Add Slot", "Width (mm):", 10.0, 0.01)
        if not ok5:
            return

        try:
            lib = SketchActionLibrary()
            result = lib.add_slot(sketch_name, (x1, y1), (x2, y2), width)
            if result.get("geometry_type") == "Slot":
                self.add_system_message(
                    f"Added slot to {sketch_name}: start=({x1},{y1}), end=({x2},{y2}), width={width}"
                )
            else:
                self.add_error_message("Failed to add slot (unexpected result)")
        except Exception as e:
            self.add_error_message(f"Add slot error: {e}")

    def _quick_rectangular_pattern(self):
        try:
            from PySide6.QtWidgets import QInputDialog  # type: ignore
        except Exception:
            from PySide2.QtWidgets import QInputDialog  # type: ignore

        try:
            from freecad_ai_addon.agent.sketch_action_library import SketchActionLibrary
        except Exception as e:
            self.add_error_message(f"SketchActionLibrary unavailable: {e}")
            return

        sketch_name, ok0 = QInputDialog.getText(
            self, "Rectangular Pattern", "Sketch name:"
        )
        if not ok0 or not sketch_name:
            return
        gids_text, ok1 = QInputDialog.getText(
            self, "Rectangular Pattern", "Geometry IDs (comma-separated):"
        )
        if not ok1 or not gids_text.strip():
            return
        rows, ok2 = QInputDialog.getInt(self, "Rectangular Pattern", "Rows:", 2, 1)
        if not ok2:
            return
        cols, ok3 = QInputDialog.getInt(self, "Rectangular Pattern", "Columns:", 3, 1)
        if not ok3:
            return
        row_sp, ok4 = QInputDialog.getDouble(
            self, "Rectangular Pattern", "Row spacing:", 20.0
        )
        if not ok4:
            return
        col_sp, ok5 = QInputDialog.getDouble(
            self, "Rectangular Pattern", "Col spacing:", 20.0
        )
        if not ok5:
            return

        try:
            gids = [int(s.strip()) for s in gids_text.split(",") if s.strip()]
            lib = SketchActionLibrary()
            result = lib.create_rectangular_pattern(
                sketch_name, gids, rows, cols, row_sp, col_sp
            )
            created = len(result.get("created_geometry_ids", []))
            self.add_system_message(
                f"Rectangular pattern created in {sketch_name}: {created} new elements ({rows}x{cols})."
            )
        except Exception as e:
            self.add_error_message(f"Rectangular pattern error: {e}")

    def _quick_polar_pattern(self):
        try:
            from PySide6.QtWidgets import QInputDialog  # type: ignore
        except Exception:
            from PySide2.QtWidgets import QInputDialog  # type: ignore

        try:
            from freecad_ai_addon.agent.sketch_action_library import SketchActionLibrary
        except Exception as e:
            self.add_error_message(f"SketchActionLibrary unavailable: {e}")
            return

        sketch_name, ok0 = QInputDialog.getText(self, "Polar Pattern", "Sketch name:")
        if not ok0 or not sketch_name:
            return
        gids_text, ok1 = QInputDialog.getText(
            self, "Polar Pattern", "Geometry IDs (comma-separated):"
        )
        if not ok1 or not gids_text.strip():
            return
        cx, ok2 = QInputDialog.getDouble(self, "Polar Pattern", "Center X:", 0.0)
        if not ok2:
            return
        cy, ok3 = QInputDialog.getDouble(self, "Polar Pattern", "Center Y:", 0.0)
        if not ok3:
            return
        count, ok4 = QInputDialog.getInt(self, "Polar Pattern", "Count:", 6, 2)
        if not ok4:
            return
        angle, ok5 = QInputDialog.getDouble(
            self, "Polar Pattern", "Total Angle (deg):", 360.0
        )
        if not ok5:
            return

        try:
            gids = [int(s.strip()) for s in gids_text.split(",") if s.strip()]
            lib = SketchActionLibrary()
            result = lib.create_polar_pattern(sketch_name, gids, (cx, cy), count, angle)
            created = len(result.get("created_geometry_ids", []))
            self.add_system_message(
                f"Polar pattern created in {sketch_name}: {created} new elements around ({cx},{cy})."
            )
        except Exception as e:
            self.add_error_message(f"Polar pattern error: {e}")

    def _quick_linear_pattern(self):
        try:
            from PySide6.QtWidgets import QInputDialog  # type: ignore
        except Exception:
            from PySide2.QtWidgets import QInputDialog  # type: ignore

        try:
            from freecad_ai_addon.agent.sketch_action_library import SketchActionLibrary
        except Exception as e:
            self.add_error_message(f"SketchActionLibrary unavailable: {e}")
            return

        sketch_name, ok0 = QInputDialog.getText(self, "Linear Pattern", "Sketch name:")
        if not ok0 or not sketch_name:
            return
        gids_text, ok1 = QInputDialog.getText(
            self, "Linear Pattern", "Geometry IDs (comma-separated):"
        )
        if not ok1 or not gids_text.strip():
            return
        dx, ok2 = QInputDialog.getDouble(self, "Linear Pattern", "Direction X:", 1.0)
        if not ok2:
            return
        dy, ok3 = QInputDialog.getDouble(self, "Linear Pattern", "Direction Y:", 0.0)
        if not ok3:
            return
        count, ok4 = QInputDialog.getInt(self, "Linear Pattern", "Count:", 3, 2)
        if not ok4:
            return
        spacing, ok5 = QInputDialog.getDouble(self, "Linear Pattern", "Spacing:", 20.0)
        if not ok5:
            return

        try:
            gids = [int(s.strip()) for s in gids_text.split(",") if s.strip()]
            lib = SketchActionLibrary()
            result = lib.create_linear_pattern(
                sketch_name, gids, (dx, dy), count, spacing
            )
            created = len(result.get("created_geometry_ids", []))
            self.add_system_message(
                f"Linear pattern created in {sketch_name}: {created} new elements along ({dx},{dy})."
            )
        except Exception as e:
            self.add_error_message(f"Linear pattern error: {e}")

    def _quick_add_coincident(self):
        """Prompt for two geometry refs and add a coincident constraint."""
        try:
            from PySide6.QtWidgets import QInputDialog  # type: ignore
        except Exception:
            from PySide2.QtWidgets import QInputDialog  # type: ignore

        try:
            from freecad_ai_addon.agent.sketch_action_library import SketchActionLibrary
        except Exception as e:
            self.add_error_message(f"SketchActionLibrary unavailable: {e}")
            return

        sketch_name, ok0 = QInputDialog.getText(self, "Add Coincident", "Sketch name:")
        if not ok0 or not sketch_name:
            return

        gid1, ok1 = QInputDialog.getInt(self, "Add Coincident", "Geometry 1 ID:", 0, 0)
        if not ok1:
            return
        pos1, ok2 = QInputDialog.getInt(
            self,
            "Add Coincident",
            "Point on Geometry 1 (1=start,2=end,3=center):",
            1,
            1,
            3,
        )
        if not ok2:
            return
        gid2, ok3 = QInputDialog.getInt(self, "Add Coincident", "Geometry 2 ID:", 1, 0)
        if not ok3:
            return
        pos2, ok4 = QInputDialog.getInt(
            self,
            "Add Coincident",
            "Point on Geometry 2 (1=start,2=end,3=center):",
            1,
            1,
            3,
        )
        if not ok4:
            return

        try:
            lib = SketchActionLibrary()
            result = lib.add_coincident_constraint(sketch_name, gid1, pos1, gid2, pos2)
            cid = result.get("constraint_id")
            if cid is not None:
                self.add_system_message(
                    f"Coincident added in {sketch_name}: g{gid1}@{pos1} ↔ g{gid2}@{pos2} (id {cid})"
                )
            else:
                self.add_error_message("Failed to add coincident constraint")
        except Exception as e:
            self.add_error_message(f"Add coincident error: {e}")

    def _quick_add_angle(self):
        """Prompt for two lines and add an angle constraint."""
        try:
            from PySide6.QtWidgets import QInputDialog  # type: ignore
        except Exception:
            from PySide2.QtWidgets import QInputDialog  # type: ignore

        try:
            from freecad_ai_addon.agent.sketch_action_library import SketchActionLibrary
        except Exception as e:
            self.add_error_message(f"SketchActionLibrary unavailable: {e}")
            return

        sketch_name, ok0 = QInputDialog.getText(self, "Add Angle", "Sketch name:")
        if not ok0 or not sketch_name:
            return
        gid1, ok1 = QInputDialog.getInt(self, "Add Angle", "Line 1 Geometry ID:", 0, 0)
        if not ok1:
            return
        gid2, ok2 = QInputDialog.getInt(self, "Add Angle", "Line 2 Geometry ID:", 1, 0)
        if not ok2:
            return
        angle, ok3 = QInputDialog.getDouble(self, "Add Angle", "Angle (degrees):", 90.0)
        if not ok3:
            return

        try:
            lib = SketchActionLibrary()
            result = lib.add_angle_constraint(sketch_name, gid1, gid2, angle)
            cid = result.get("constraint_id")
            if cid is not None:
                self.add_system_message(
                    f"Angle constraint added in {sketch_name}: lines {gid1},{gid2} = {angle}° (id {cid})"
                )
            else:
                self.add_error_message("Failed to add angle constraint")
        except Exception as e:
            self.add_error_message(f"Add angle error: {e}")

    def get_conversation_history(self) -> List[ChatMessage]:
        """Get the current conversation history"""
        return self.conversation_area.messages.copy()

    def load_conversation(self, messages: List[Dict]):
        """Load conversation from saved data"""
        self.conversation_area.clear_messages()

        for msg_data in messages:
            try:
                message = ChatMessage(
                    id=msg_data["id"],
                    type=MessageType(msg_data["type"]),
                    content=msg_data["content"],
                    timestamp=datetime.fromisoformat(msg_data["timestamp"]),
                    provider=msg_data.get("provider"),
                    metadata=msg_data.get("metadata", {}),
                    attachments=msg_data.get("attachments", []),
                )
                self.add_message(message)
            except Exception as e:
                logger.error(f"Failed to load message: {e}")
                continue
