"""
Interactive Elements for Conversation Widget

Implements code execution buttons, parameter widgets, preview functionality,
and other interactive elements for the AI conversation interface.
"""

import re
import traceback
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from PySide6 import QtWidgets
from PySide6.QtCore import Signal, QTimer, QThread, pyqtSignal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QSpinBox, QDoubleSpinBox, QComboBox, QCheckBox,
    QTextEdit, QMessageBox, QFrame, QGroupBox
)
from PySide6.QtGui import QFont

try:
    import FreeCAD as App
    import FreeCADGui as Gui
    FREECAD_AVAILABLE = True
except ImportError:
    FREECAD_AVAILABLE = False
    App = None
    Gui = None

from freecad_ai_addon.utils.logging import get_logger

logger = get_logger('interactive_elements')


class CodeExecutionStatus(Enum):
    """Status of code execution"""
    READY = "ready"
    EXECUTING = "executing"
    SUCCESS = "success"
    ERROR = "error"
    PREVIEW = "preview"


@dataclass
class ExecutionResult:
    """Result of code execution"""
    status: CodeExecutionStatus
    output: Optional[str] = None
    error: Optional[str] = None
    created_objects: List[str] = None
    execution_time: float = 0.0

    def __post_init__(self):
        if self.created_objects is None:
            self.created_objects = []


class CodeExecutionWorker(QThread):
    """Worker thread for safe code execution"""
    finished = pyqtSignal(ExecutionResult)
    progress = pyqtSignal(str)

    def __init__(self, code: str, preview_mode: bool = False):
        super().__init__()
        self.code = code
        self.preview_mode = preview_mode
        self.result = ExecutionResult(CodeExecutionStatus.READY)

    def run(self):
        """Execute code in separate thread"""
        if not FREECAD_AVAILABLE:
            self.result = ExecutionResult(
                CodeExecutionStatus.ERROR,
                error="FreeCAD not available"
            )
            self.finished.emit(self.result)
            return

        try:
            import time
            start_time = time.time()

            self.progress.emit("Preparing execution environment...")

            # Create execution context
            exec_globals = {
                'App': App,
                'Gui': Gui,
                '__builtins__': __builtins__,
                'created_objects': []
            }

            # Add object tracking for preview mode
            if self.preview_mode:
                exec_globals['_preview_objects'] = []
                # Monkey patch object creation for tracking
                if App.ActiveDocument:
                    original_add_object = App.ActiveDocument.addObject
                else:
                    original_add_object = None

                def tracked_add_object(*args, **kwargs):
                    if original_add_object:
                        obj = original_add_object(*args, **kwargs)
                        exec_globals['_preview_objects'].append(obj.Name)
                        exec_globals['created_objects'].append(obj.Name)
                        return obj
                    return None

                if App.ActiveDocument:
                    App.ActiveDocument.addObject = tracked_add_object

            self.progress.emit("Executing code...")

            # Execute the code
            exec(self.code, exec_globals)

            # Restore original function if in preview mode
            if (self.preview_mode and App.ActiveDocument and
                    original_add_object):
                App.ActiveDocument.addObject = original_add_object

            # Recompute document
            if App.ActiveDocument:
                App.ActiveDocument.recompute()

            execution_time = time.time() - start_time

            self.result = ExecutionResult(
                CodeExecutionStatus.SUCCESS,
                output=f"Code executed successfully in {execution_time:.2f}s",
                created_objects=exec_globals.get('created_objects', []),
                execution_time=execution_time
            )

            if self.preview_mode:
                self.result.status = CodeExecutionStatus.PREVIEW

        except Exception as e:
            error_msg = f"Execution error: {str(e)}\n{traceback.format_exc()}"
            logger.error(f"Code execution failed: {error_msg}")

            self.result = ExecutionResult(
                CodeExecutionStatus.ERROR,
                error=error_msg
            )

        self.finished.emit(self.result)


class ExecuteCodeButton(QPushButton):
    """Interactive button for executing AI-generated code"""
    execution_finished = Signal(ExecutionResult)

    def __init__(self, code_content: str, parent=None):
        super().__init__("Execute in FreeCAD", parent)
        self.code = code_content
        self.execution_worker = None
        self.preview_mode = False

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Set up button UI"""
        self.setFont(QFont("", 9, QFont.Bold))
        self.setMinimumHeight(32)
        self.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)

    def _connect_signals(self):
        """Connect button signals"""
        self.clicked.connect(self.execute_code)

    def set_preview_mode(self, preview: bool):
        """Set preview mode for execution"""
        self.preview_mode = preview
        if preview:
            self.setText("Preview Changes")
            self.setStyleSheet(self.styleSheet().replace("#4CAF50", "#FF9800"))
        else:
            self.setText("Execute in FreeCAD")
            self.setStyleSheet(self.styleSheet().replace("#FF9800", "#4CAF50"))

    def execute_code(self):
        """Execute the code"""
        if not FREECAD_AVAILABLE:
            QMessageBox.warning(
                self, "FreeCAD Required",
                "FreeCAD is required for code execution"
            )
            return

        if not App.ActiveDocument:
            # Ask user if they want to create a new document
            reply = QMessageBox.question(
                self, "No Active Document",
                "No FreeCAD document is open. Create a new one?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                App.newDocument("AI_Generated")
            else:
                return

        # Disable button during execution
        self.setEnabled(False)
        text = "Executing..." if not self.preview_mode else "Previewing..."
        self.setText(text)

        # Start execution in worker thread
        self.execution_worker = CodeExecutionWorker(
            self.code, self.preview_mode
        )
        self.execution_worker.finished.connect(self._on_execution_finished)
        self.execution_worker.progress.connect(self._on_progress)
        self.execution_worker.start()

    def _on_progress(self, message: str):
        """Handle progress updates"""
        self.setText(message)

    def _on_execution_finished(self, result: ExecutionResult):
        """Handle execution completion"""
        self.setEnabled(True)

        if result.status == CodeExecutionStatus.SUCCESS:
            self.setText("✓ Executed")
            self.setStyleSheet(self.styleSheet().replace("#4CAF50", "#2196F3"))
        elif result.status == CodeExecutionStatus.PREVIEW:
            self.setText("✓ Previewed")
            self.setStyleSheet(self.styleSheet().replace("#FF9800", "#2196F3"))
        elif result.status == CodeExecutionStatus.ERROR:
            self.setText("✗ Error")
            self.setStyleSheet(self.styleSheet().replace("#4CAF50", "#F44336"))

            # Show error dialog
            QMessageBox.critical(self, "Execution Error", result.error)

        # Emit signal for parent handling
        self.execution_finished.emit(result)

        # Reset button after delay
        QTimer.singleShot(3000, self._reset_button)

    def _reset_button(self):
        """Reset button to initial state"""
        if self.preview_mode:
            self.setText("Preview Changes")
            self.setStyleSheet(self.styleSheet().replace("#2196F3", "#FF9800"))
        else:
            self.setText("Execute in FreeCAD")
            self.setStyleSheet(self.styleSheet().replace("#2196F3", "#4CAF50"))


class ParameterWidget(QWidget):
    """Widget for adjusting parameters with live preview"""
    value_changed = Signal(str, object)  # parameter_name, new_value

    def __init__(self, param_name: str, param_type: str,
                 default_value: Any, range_info: Dict = None, parent=None):
        super().__init__(parent)
        self.param_name = param_name
        self.param_type = param_type
        self.default_value = default_value
        self.range_info = range_info or {}

        self._setup_ui()

    def _setup_ui(self):
        """Set up parameter widget UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Parameter name label
        name_label = QLabel(f"{self.param_name}:")
        name_label.setMinimumWidth(80)
        layout.addWidget(name_label)

        # Create appropriate input widget based on type
        if self.param_type == "float":
            self.input_widget = self._create_float_widget()
        elif self.param_type == "int":
            self.input_widget = self._create_int_widget()
        elif self.param_type == "bool":
            self.input_widget = self._create_bool_widget()
        elif self.param_type == "choice":
            self.input_widget = self._create_choice_widget()
        else:
            self.input_widget = self._create_text_widget()

        layout.addWidget(self.input_widget)
        layout.addStretch()

    def _create_float_widget(self):
        """Create float parameter widget"""
        widget = QDoubleSpinBox()
        widget.setValue(float(self.default_value))

        if "min" in self.range_info:
            widget.setMinimum(self.range_info["min"])
        if "max" in self.range_info:
            widget.setMaximum(self.range_info["max"])
        if "step" in self.range_info:
            widget.setSingleStep(self.range_info["step"])

        widget.valueChanged.connect(
            lambda v: self.value_changed.emit(self.param_name, v)
        )
        return widget

    def _create_int_widget(self):
        """Create integer parameter widget"""
        widget = QSpinBox()
        widget.setValue(int(self.default_value))

        if "min" in self.range_info:
            widget.setMinimum(self.range_info["min"])
        if "max" in self.range_info:
            widget.setMaximum(self.range_info["max"])

        widget.valueChanged.connect(
            lambda v: self.value_changed.emit(self.param_name, v)
        )
        return widget

    def _create_bool_widget(self):
        """Create boolean parameter widget"""
        widget = QCheckBox()
        widget.setChecked(bool(self.default_value))
        widget.stateChanged.connect(
            lambda state: self.value_changed.emit(self.param_name, state == 2)
        )
        return widget

    def _create_choice_widget(self):
        """Create choice parameter widget"""
        widget = QComboBox()
        choices = self.range_info.get("choices", [])
        widget.addItems([str(choice) for choice in choices])

        if self.default_value in choices:
            widget.setCurrentText(str(self.default_value))

        widget.currentTextChanged.connect(
            lambda text: self.value_changed.emit(self.param_name, text)
        )
        return widget

    def _create_text_widget(self):
        """Create text parameter widget"""
        widget = QtWidgets.QLineEdit()
        widget.setText(str(self.default_value))
        widget.textChanged.connect(
            lambda text: self.value_changed.emit(self.param_name, text)
        )
        return widget

    def get_value(self):
        """Get current parameter value"""
        if self.param_type == "float":
            return self.input_widget.value()
        elif self.param_type == "int":
            return self.input_widget.value()
        elif self.param_type == "bool":
            return self.input_widget.isChecked()
        elif self.param_type == "choice":
            return self.input_widget.currentText()
        else:
            return self.input_widget.text()


class InteractiveCodeBlock(QFrame):
    """Interactive code block with execution and parameter controls"""

    def __init__(self, code: str, parameters: Dict = None, parent=None):
        super().__init__(parent)
        self.code = code
        self.parameters = parameters or {}
        self.current_values = {}

        self._setup_ui()
        self._extract_parameters()

    def _setup_ui(self):
        """Set up interactive code block UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # Code display
        code_display = QTextEdit()
        code_display.setPlainText(self.code)
        code_display.setMaximumHeight(200)
        code_display.setFont(QFont("Consolas, Monaco, monospace", 9))
        code_display.setStyleSheet("""
            QTextEdit {
                background-color: #f8f8f8;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        layout.addWidget(code_display)

        # Parameters section
        if self.parameters:
            params_group = QGroupBox("Parameters")
            params_layout = QVBoxLayout(params_group)

            self.param_widgets = {}
            for param_name, param_info in self.parameters.items():
                param_widget = ParameterWidget(
                    param_name,
                    param_info.get("type", "str"),
                    param_info.get("default", ""),
                    param_info.get("range", {})
                )
                param_widget.value_changed.connect(self._on_parameter_changed)
                params_layout.addWidget(param_widget)
                self.param_widgets[param_name] = param_widget

            layout.addWidget(params_group)

        # Action buttons
        button_layout = QHBoxLayout()

        self.preview_button = ExecuteCodeButton(
            self._get_parameterized_code())
        self.preview_button.set_preview_mode(True)
        self.preview_button.execution_finished.connect(
            self._on_preview_finished)

        self.execute_button = ExecuteCodeButton(
            self._get_parameterized_code())
        self.execute_button.execution_finished.connect(
            self._on_execution_finished)
        button_layout.addWidget(self.execute_button)

        copy_button = QPushButton("Copy Code")
        copy_button.clicked.connect(self._copy_code)
        button_layout.addWidget(copy_button)

        explain_button = QPushButton("Explain")
        explain_button.clicked.connect(self._explain_code)
        button_layout.addWidget(explain_button)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Status indicator
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.status_label)

    def _extract_parameters(self):
        """Extract parameters from code comments or docstrings"""
        # Look for parameter hints in comments
        param_pattern = (r'#\s*@param\s+(\w+):\s*(\w+)\s*=\s*([^,\n]+)'
                         r'(?:,\s*range=\((.*?)\))?')
        matches = re.findall(param_pattern, self.code)

        for match in matches:
            param_name, param_type, default_value, range_str = match

            # Parse range information
            range_info = {}
            if range_str:
                try:
                    range_info = eval(f"dict({range_str})")
                except (ValueError, SyntaxError):
                    pass

            self.parameters[param_name] = {
                "type": param_type,
                "default": default_value,
                "range": range_info
            }

    def _on_parameter_changed(self, param_name: str, value: Any):
        """Handle parameter value change"""
        self.current_values[param_name] = value

        # Update code in buttons
        new_code = self._get_parameterized_code()
        self.preview_button.code = new_code
        self.execute_button.code = new_code

        self.status_label.setText(f"Parameter {param_name} updated")

    def _get_parameterized_code(self):
        """Get code with current parameter values substituted"""
        code = self.code

        for param_name, value in self.current_values.items():
            # Replace parameter placeholders in code
            if isinstance(value, str):
                code = code.replace(f"{{{param_name}}}", f'"{value}"')
            else:
                code = code.replace(f"{{{param_name}}}", str(value))

        return code

    def _copy_code(self):
        """Copy parameterized code to clipboard"""
        code = self._get_parameterized_code()
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(code)
        self.status_label.setText("Code copied to clipboard")

    def _explain_code(self):
        """Request code explanation (placeholder for AI integration)"""
        self.status_label.setText("Code explanation requested...")
        # TODO: Integrate with AI provider for code explanation

    def _on_preview_finished(self, result: ExecutionResult):
        """Handle preview execution completion"""
        if result.status == CodeExecutionStatus.PREVIEW:
            objects_count = len(result.created_objects)
            self.status_label.setText(
                f"Preview completed ({objects_count} objects)")
        else:
            self.status_label.setText("Preview failed")

    def _on_execution_finished(self, result: ExecutionResult):
        """Handle execution completion"""
        if result.status == CodeExecutionStatus.SUCCESS:
            exec_time = result.execution_time
            self.status_label.setText(
                f"Executed successfully ({exec_time:.2f}s)")
        else:
            self.status_label.setText("Execution failed")


class ConfirmationDialog(QMessageBox):
    """Enhanced confirmation dialog for destructive operations"""

    def __init__(self, operation: str, affected_objects: List[str],
                 parent=None):
        super().__init__(parent)
        self.operation = operation
        self.affected_objects = affected_objects

        self._setup_dialog()

    def _setup_dialog(self):
        """Set up confirmation dialog"""
        self.setWindowTitle("Confirm Operation")
        self.setIcon(QMessageBox.Question)

        # Main message
        message = f"This will {self.operation}."
        if self.affected_objects:
            message += f"\n\nAffected objects ({len(self.affected_objects)}):"
            for obj in self.affected_objects[:5]:  # Show first 5
                message += f"\n• {obj}"
            if len(self.affected_objects) > 5:
                message += f"\n• ... and {len(self.affected_objects) - 5} more"

        self.setText(message)
        self.setInformativeText("Do you want to continue?")

        # Custom buttons
        self.addButton("Preview First", QMessageBox.ActionRole)
        self.addButton("Yes, Continue", QMessageBox.YesRole)
        self.addButton("Cancel", QMessageBox.NoRole)

        self.setDefaultButton(self.button(QMessageBox.NoRole))


def extract_code_blocks(text: str) -> List[Dict[str, str]]:
    """Extract code blocks from markdown text"""
    code_blocks = []

    # Pattern for fenced code blocks
    pattern = r'```(\w+)?\n(.*?)\n```'
    matches = re.findall(pattern, text, re.DOTALL)

    for language, code in matches:
        is_python = language.lower() in ['python', 'py', '']
        has_freecad = 'App.' in code or 'Gui.' in code
        if is_python and has_freecad:
            code_blocks.append({
                'language': language or 'python',
                'code': code.strip(),
                'executable': True
            })
        else:
            code_blocks.append({
                'language': language or 'text',
                'code': code.strip(),
                'executable': False
            })

    return code_blocks


def create_interactive_message_widget(message_text: str) -> QWidget:
    """Create interactive message widget with code execution buttons"""
    widget = QWidget()
    layout = QVBoxLayout(widget)

    # Extract and process code blocks
    code_blocks = extract_code_blocks(message_text)

    # Add text content (simplified markdown rendering)
    text_parts = re.split(r'```\w*\n.*?\n```', message_text, flags=re.DOTALL)

    for i, text_part in enumerate(text_parts):
        if text_part.strip():
            text_label = QLabel(text_part.strip())
            text_label.setWordWrap(True)
            layout.addWidget(text_label)

        # Add interactive code block if available
        if i < len(code_blocks) and code_blocks[i]['executable']:
            interactive_block = InteractiveCodeBlock(code_blocks[i]['code'])
            layout.addWidget(interactive_block)

    return widget
