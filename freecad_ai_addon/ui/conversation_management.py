"""
Conversation Management UI

Provides UI components for managing conversation history, templates,
and sharing functionality.
"""

from typing import Dict, Any
from datetime import datetime

from PySide6 import QtCore
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QTextEdit, QComboBox,
    QDialog, QDialogButtonBox, QLineEdit, QGroupBox,
    QSplitter, QMessageBox, QFileDialog
)

from freecad_ai_addon.ui.conversation_persistence import (
    get_conversation_persistence
)
from freecad_ai_addon.utils.logging import get_logger

logger = get_logger('conversation_management')


class ConversationHistoryDialog(QDialog):
    """Dialog for browsing and managing conversation history"""

    conversation_selected = Signal(str)  # conversation_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self.persistence = get_conversation_persistence()
        self.conversations = []

        self._setup_ui()
        self._load_conversations()

    def _setup_ui(self):
        """Set up the dialog UI"""
        self.setWindowTitle("Conversation History")
        self.setMinimumSize(800, 600)

        layout = QVBoxLayout(self)

        # Search and filter controls
        search_group = QGroupBox("Search & Filter")
        search_layout = QHBoxLayout(search_group)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search conversations...")
        self.search_edit.textChanged.connect(self._filter_conversations)
        search_layout.addWidget(QLabel("Search:"))
        search_layout.addWidget(self.search_edit)

        self.date_filter = QComboBox()
        self.date_filter.addItems([
            "All Time", "Today", "This Week", "This Month"
        ])
        self.date_filter.currentTextChanged.connect(self._filter_conversations)
        search_layout.addWidget(QLabel("Date:"))
        search_layout.addWidget(self.date_filter)

        layout.addWidget(search_group)

        # Main content area
        splitter = QSplitter(QtCore.Qt.Horizontal)

        # Conversation list
        list_widget = QWidget()
        list_layout = QVBoxLayout(list_widget)

        list_layout.addWidget(QLabel("Conversations:"))
        self.conversation_list = QListWidget()
        self.conversation_list.itemSelectionChanged.connect(
            self._on_conversation_selected
        )
        list_layout.addWidget(self.conversation_list)

        # List controls
        list_controls = QHBoxLayout()

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self._load_conversations)
        list_controls.addWidget(self.refresh_btn)

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self._delete_selected)
        self.delete_btn.setEnabled(False)
        list_controls.addWidget(self.delete_btn)

        list_controls.addStretch()
        list_layout.addLayout(list_controls)

        splitter.addWidget(list_widget)

        # Preview area
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)

        preview_layout.addWidget(QLabel("Preview:"))
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        preview_layout.addWidget(self.preview_text)

        # Preview controls
        preview_controls = QHBoxLayout()

        self.export_btn = QPushButton("Export...")
        self.export_btn.clicked.connect(self._export_conversation)
        self.export_btn.setEnabled(False)
        preview_controls.addWidget(self.export_btn)

        self.load_btn = QPushButton("Load Conversation")
        self.load_btn.clicked.connect(self._load_selected_conversation)
        self.load_btn.setEnabled(False)
        preview_controls.addWidget(self.load_btn)

        preview_controls.addStretch()
        preview_layout.addLayout(preview_controls)

        splitter.addWidget(preview_widget)
        splitter.setSizes([300, 500])

        layout.addWidget(splitter)

        # Dialog buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Close,
            QtCore.Qt.Horizontal
        )
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _load_conversations(self):
        """Load conversations from persistence"""
        try:
            self.conversations = self.persistence.list_conversations()
            self._update_conversation_list()
            logger.info(f"Loaded {len(self.conversations)} conversations")
        except Exception as e:
            logger.error(f"Failed to load conversations: {e}")
            QMessageBox.critical(
                self, "Error", f"Failed to load conversations: {e}"
            )

    def _update_conversation_list(self):
        """Update the conversation list display"""
        self.conversation_list.clear()

        for conv in self.conversations:
            item = QListWidgetItem()

            # Format display text
            created_at = conv.get("created_at", "Unknown")
            if created_at != "Unknown":
                try:
                    dt = datetime.fromisoformat(
                        created_at.replace('Z', '+00:00'))
                    created_str = dt.strftime("%Y-%m-%d %H:%M")
                except (ValueError, AttributeError):
                    created_str = (created_at[:16]
                                   if len(created_at) > 16
                                   else created_at)
            else:
                created_str = "Unknown"

            message_count = conv.get("message_count", 0)
            preview = conv.get("last_message_preview", "")
            if len(preview) > 50:
                preview = preview[:50] + "..."

            display_text = f"{created_str} ({message_count} messages)\n{preview}"
            item.setText(display_text)
            item.setData(QtCore.Qt.UserRole, conv["id"])

            self.conversation_list.addItem(item)

    def _filter_conversations(self):
        """Filter conversations based on search criteria"""
        search_text = self.search_edit.text().lower()
        date_filter = self.date_filter.currentText()

        # Apply filters
        filtered_conversations = []

        for conv in self.conversations:
            # Text search
            if search_text:
                preview = conv.get("last_message_preview", "").lower()
                if search_text not in preview:
                    continue

            # Date filter
            if date_filter != "All Time":
                created_at = conv.get("created_at")
                if created_at and not self._matches_date_filter(
                        created_at, date_filter):
                    continue

            filtered_conversations.append(conv)

        # Update display
        self.conversations = filtered_conversations
        self._update_conversation_list()

    def _matches_date_filter(self, created_at: str, filter_type: str) -> bool:
        """Check if conversation matches date filter"""
        try:
            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            now = datetime.now()

            if filter_type == "Today":
                return dt.date() == now.date()
            elif filter_type == "This Week":
                return (now - dt).days <= 7
            elif filter_type == "This Month":
                return (now.year == dt.year and now.month == dt.month)

        except Exception:
            pass

        return False

    def _on_conversation_selected(self):
        """Handle conversation selection"""
        current_item = self.conversation_list.currentItem()
        if not current_item:
            self.preview_text.clear()
            self.delete_btn.setEnabled(False)
            self.export_btn.setEnabled(False)
            self.load_btn.setEnabled(False)
            return

        conversation_id = current_item.data(QtCore.Qt.UserRole)

        # Load and preview conversation
        conversation = self.persistence.load_conversation(conversation_id)
        if conversation:
            self._show_conversation_preview(conversation)
            self.delete_btn.setEnabled(True)
            self.export_btn.setEnabled(True)
            self.load_btn.setEnabled(True)

    def _show_conversation_preview(self, conversation: Dict[str, Any]):
        """Show conversation preview"""
        preview_lines = []

        # Header
        preview_lines.append(f"ID: {conversation.get('id', 'Unknown')}")
        preview_lines.append(f"Created: {conversation.get('created_at', 'Unknown')}")
        preview_lines.append(f"Messages: {len(conversation.get('messages', []))}")
        preview_lines.append("-" * 40)

        # Messages preview
        messages = conversation.get("messages", [])
        for i, msg in enumerate(messages[:5]):  # Show first 5 messages
            msg_type = msg.get("type", "unknown")
            content = msg.get("content", "")

            # Truncate long messages
            if len(content) > 200:
                content = content[:200] + "..."

            preview_lines.append(f"[{i+1}] {msg_type.upper()}:")
            preview_lines.append(content)
            preview_lines.append("")

        if len(messages) > 5:
            preview_lines.append(f"... and {len(messages) - 5} more messages")

        self.preview_text.setPlainText("\n".join(preview_lines))

    def _delete_selected(self):
        """Delete selected conversation"""
        current_item = self.conversation_list.currentItem()
        if not current_item:
            return

        conversation_id = current_item.data(QtCore.Qt.UserRole)

        # Confirm deletion
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to delete conversation {conversation_id}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if self.persistence.delete_conversation(conversation_id):
                self._load_conversations()  # Refresh list
                QMessageBox.information(
                    self, "Deleted", "Conversation deleted successfully."
                )
            else:
                QMessageBox.critical(
                    self, "Error", "Failed to delete conversation."
                )

    def _export_conversation(self):
        """Export selected conversation"""
        current_item = self.conversation_list.currentItem()
        if not current_item:
            return

        conversation_id = current_item.data(QtCore.Qt.UserRole)

        # Choose export format
        format_dialog = QDialog(self)
        format_dialog.setWindowTitle("Export Format")
        layout = QVBoxLayout(format_dialog)

        layout.addWidget(QLabel("Choose export format:"))

        format_combo = QComboBox()
        format_combo.addItems(["Markdown", "JSON", "Plain Text"])
        layout.addWidget(format_combo)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(format_dialog.accept)
        buttons.rejected.connect(format_dialog.reject)
        layout.addWidget(buttons)

        if format_dialog.exec() == QDialog.Accepted:
            export_format = format_combo.currentText().lower().replace(" ", "_")

            # Get export content
            content = self.persistence.export_conversation(
                conversation_id, export_format
            )

            if content:
                # Choose save location
                file_extension = {
                    "markdown": "md",
                    "json": "json",
                    "plain_text": "txt"
                }[export_format]

                filename, _ = QFileDialog.getSaveFileName(
                    self,
                    "Export Conversation",
                    f"conversation_{conversation_id}.{file_extension}",
                    f"{export_format.title()} files (*.{file_extension})"
                )

                if filename:
                    try:
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(content)
                        QMessageBox.information(
                            self, "Exported", f"Conversation exported to {filename}"
                        )
                    except Exception as e:
                        QMessageBox.critical(
                            self, "Error", f"Failed to export: {e}"
                        )

    def _load_selected_conversation(self):
        """Load selected conversation into main interface"""
        current_item = self.conversation_list.currentItem()
        if not current_item:
            return

        conversation_id = current_item.data(QtCore.Qt.UserRole)
        self.conversation_selected.emit(conversation_id)
        self.accept()


class ConversationTemplatesWidget(QWidget):
    """Widget for managing conversation templates"""

    template_selected = Signal(str)  # template_content

    def __init__(self, parent=None):
        super().__init__(parent)
        self.templates = self._get_default_templates()
        self._setup_ui()

    def _setup_ui(self):
        """Set up the templates widget UI"""
        layout = QVBoxLayout(self)

        # Header
        layout.addWidget(QLabel("Conversation Templates"))

        # Template list
        self.template_combo = QComboBox()
        self.template_combo.currentTextChanged.connect(
            self._on_template_selected
        )
        layout.addWidget(self.template_combo)

        # Template preview
        self.template_preview = QTextEdit()
        self.template_preview.setMaximumHeight(200)
        self.template_preview.setReadOnly(True)
        layout.addWidget(self.template_preview)

        # Controls
        controls_layout = QHBoxLayout()

        use_btn = QPushButton("Use Template")
        use_btn.clicked.connect(self._use_template)
        controls_layout.addWidget(use_btn)

        customize_btn = QPushButton("Customize...")
        customize_btn.clicked.connect(self._customize_template)
        controls_layout.addWidget(customize_btn)

        controls_layout.addStretch()
        layout.addLayout(controls_layout)

        # Load templates into combo
        self._load_templates()

    def _get_default_templates(self) -> Dict[str, str]:
        """Get default conversation templates"""
        return {
            "Design Review": """Please review this FreeCAD design for:
1. Structural integrity
2. Manufacturing feasibility
3. Material efficiency
4. Potential improvements

Current design context: {context}""",

            "3D Printing Analysis": """Analyze this part for 3D printing:
1. Check for overhangs requiring supports
2. Verify wall thickness (minimum 1.2mm)
3. Identify potential warping issues
4. Suggest optimal print orientation
5. Recommend infill and layer settings

Part specifications: {context}""",

            "Manufacturing Guidance": """Provide manufacturing guidance for this part:
1. Recommended manufacturing process
2. Material selection advice
3. Tolerance analysis
4. Cost optimization suggestions
5. Quality control checkpoints

Design details: {context}""",

            "Assembly Planning": """Help plan the assembly process for:
1. Component identification and ordering
2. Assembly sequence optimization
3. Required tools and fixtures
4. Potential assembly issues
5. Testing and validation steps

Assembly context: {context}""",

            "Design Optimization": """Optimize this design for:
1. Weight reduction while maintaining strength
2. Material cost minimization
3. Manufacturing simplicity
4. Performance improvement
5. Lifecycle considerations

Current design: {context}"""
        }

    def _load_templates(self):
        """Load templates into the combo box"""
        self.template_combo.clear()
        self.template_combo.addItem("Select a template...")

        for template_name in self.templates.keys():
            self.template_combo.addItem(template_name)

    def _on_template_selected(self):
        """Handle template selection"""
        template_name = self.template_combo.currentText()

        if template_name in self.templates:
            template_content = self.templates[template_name]
            self.template_preview.setPlainText(template_content)
        else:
            self.template_preview.clear()

    def _use_template(self):
        """Use the selected template"""
        template_name = self.template_combo.currentText()

        if template_name in self.templates:
            # Get FreeCAD context
            context = self._get_freecad_context()
            template_content = self.templates[template_name].format(
                context=context
            )
            self.template_selected.emit(template_content)

    def _customize_template(self):
        """Open template customization dialog"""
        template_name = self.template_combo.currentText()

        if template_name not in self.templates:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Customize: {template_name}")
        dialog.setMinimumSize(500, 400)

        layout = QVBoxLayout(dialog)

        layout.addWidget(QLabel("Edit template:"))

        text_edit = QTextEdit()
        text_edit.setPlainText(self.templates[template_name])
        layout.addWidget(text_edit)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec() == QDialog.Accepted:
            customized_content = text_edit.toPlainText()
            # Get context and emit customized template
            context = self._get_freecad_context()
            final_content = customized_content.format(context=context)
            self.template_selected.emit(final_content)

    def _get_freecad_context(self) -> str:
        """Get current FreeCAD context for template"""
        try:
            import FreeCAD as App

            if not App.ActiveDocument:
                return "No active FreeCAD document"

            doc = App.ActiveDocument
            context_parts = [
                f"Document: {doc.Label}",
                f"Objects: {len(doc.Objects)}"
            ]

            # Add object details
            for obj in doc.Objects[:5]:  # First 5 objects
                obj_info = f"- {obj.Label} ({obj.TypeId})"
                if hasattr(obj, 'Shape') and obj.Shape:
                    obj_info += f" - Volume: {obj.Shape.Volume:.2f}"
                context_parts.append(obj_info)

            if len(doc.Objects) > 5:
                context_parts.append(f"... and {len(doc.Objects) - 5} more")

            return "\n".join(context_parts)

        except ImportError:
            return "FreeCAD not available"
        except Exception as e:
            return f"Error getting context: {e}"
