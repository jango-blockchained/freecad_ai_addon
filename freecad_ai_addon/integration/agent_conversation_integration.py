"""
Agent Framework Conversation Integration

Integrates the AI Agent Framework with the conversation widget to enable
autonomous FreeCAD operations through natural language interactions.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

from PySide6.QtCore import QObject, Signal, QTimer, QThread
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QProgressBar, QCheckBox, QComboBox,
    QGroupBox, QMessageBox
)

from freecad_ai_addon.ui.conversation_widget import (
    ConversationWidget, ChatMessage, MessageType
)
from freecad_ai_addon.agent.agent_framework import AIAgentFramework
from freecad_ai_addon.agent.base_agent import TaskStatus, TaskResult
from freecad_ai_addon.utils.logging import get_logger

logger = get_logger('agent_conversation_integration')


class AgentMode(Enum):
    """Agent operation modes"""
    DISABLED = "disabled"
    INTERACTIVE = "interactive"  # Ask before each action
    SEMI_AUTONOMOUS = "semi_autonomous"  # Ask for critical actions only
    AUTONOMOUS = "autonomous"  # Full autonomy with safety checks


@dataclass
class AgentControlSettings:
    """Settings for agent control and behavior"""
    mode: AgentMode = AgentMode.INTERACTIVE
    auto_approve_safe_operations: bool = True
    require_confirmation_for_modifications: bool = True
    max_operations_per_task: int = 50
    timeout_seconds: int = 300
    enable_safety_validation: bool = True
    preferred_agents: List[str] = None


class AgentExecutionThread(QThread):
    """Thread for executing agent tasks without blocking UI"""
    
    task_started = Signal(str)  # task_id
    task_progress = Signal(str, str, int)  # task_id, operation, progress
    task_completed = Signal(str, object)  # task_id, result
    task_failed = Signal(str, str)  # task_id, error_message
    operation_pending = Signal(str, str, dict)  # task_id, operation, details

    def __init__(self, framework: AIAgentFramework, task_text: str,
                 settings: AgentControlSettings):
        super().__init__()
        self.framework = framework
        self.task_text = task_text
        self.settings = settings
        self.task_id = f"task_{datetime.now().timestamp()}"
        self.should_stop = False
        self.pending_approval = False
        self.approval_result = None
        
    def run(self):
        """Execute the agent task"""
        try:
            self.task_started.emit(self.task_id)
            
            # Execute the task with progress reporting
            result = asyncio.run(self._execute_with_monitoring())
            
            if not self.should_stop:
                self.task_completed.emit(self.task_id, result)
                
        except Exception as e:
            logger.error(f"Agent execution failed: {e}")
            self.task_failed.emit(self.task_id, str(e))
    
    async def _execute_with_monitoring(self):
        """Execute task with progress monitoring"""
        # Set up progress callback
        def progress_callback(operation: str, progress: int):
            if not self.should_stop:
                self.task_progress.emit(self.task_id, operation, progress)
        
        # Set up approval callback for interactive mode
        def approval_callback(operation: str, details: dict) -> bool:
            if self.settings.mode == AgentMode.AUTONOMOUS:
                return True
            elif self.settings.mode == AgentMode.DISABLED:
                return False
            
            # For interactive and semi-autonomous modes
            is_safe = details.get('is_safe', False)
            is_modification = details.get('modifies_model', False)
            
            # Auto-approve safe operations if enabled
            auto_approve = (
                self.settings.auto_approve_safe_operations and is_safe and
                not (is_modification and
                     self.settings.require_confirmation_for_modifications)
            )
            if auto_approve:
                return True
            
            # Request approval through signal
            self.operation_pending.emit(self.task_id, operation, details)
            
            # Wait for approval
            self.pending_approval = True
            while self.pending_approval and not self.should_stop:
                self.msleep(100)
            
            return self.approval_result if not self.should_stop else False
        
        # Execute the task
        result = await self.framework.execute_autonomous_task(
            self.task_text,
            progress_callback=progress_callback,
            approval_callback=approval_callback,
            max_operations=self.settings.max_operations_per_task,
            timeout=self.settings.timeout_seconds
        )
        
        return result
    
    def stop_execution(self):
        """Stop the agent execution"""
        self.should_stop = True
        if self.pending_approval:
            self.approval_result = False
            self.pending_approval = False
    
    def approve_operation(self, approved: bool):
        """Approve or reject a pending operation"""
        if self.pending_approval:
            self.approval_result = approved
            self.pending_approval = False


class AgentControlPanel(QWidget):
    """Control panel for agent operations"""
    
    mode_changed = Signal(object)  # AgentMode
    settings_changed = Signal(object)  # AgentControlSettings
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = AgentControlSettings()
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Set up the control panel UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Agent Mode Selection
        mode_group = QGroupBox("Agent Mode")
        mode_layout = QVBoxLayout(mode_group)
        
        self.mode_combo = QComboBox()
        for mode in AgentMode:
            self.mode_combo.addItem(mode.value.replace('_', ' ').title(), mode)
        self.mode_combo.setCurrentText("Interactive")
        mode_layout.addWidget(self.mode_combo)
        
        layout.addWidget(mode_group)
        
        # Safety Settings
        safety_group = QGroupBox("Safety Settings")
        safety_layout = QVBoxLayout(safety_group)
        
        self.auto_approve_cb = QCheckBox("Auto-approve safe operations")
        self.auto_approve_cb.setChecked(True)
        safety_layout.addWidget(self.auto_approve_cb)
        
        self.confirm_modifications_cb = QCheckBox(
            "Confirm model modifications"
        )
        self.confirm_modifications_cb.setChecked(True)
        safety_layout.addWidget(self.confirm_modifications_cb)
        
        self.enable_safety_cb = QCheckBox("Enable safety validation")
        self.enable_safety_cb.setChecked(True)
        safety_layout.addWidget(self.enable_safety_cb)
        
        layout.addWidget(safety_group)
        
        # Execution Limits
        limits_group = QGroupBox("Execution Limits")
        limits_layout = QVBoxLayout(limits_group)
        
        # Max operations
        max_ops_layout = QHBoxLayout()
        max_ops_layout.addWidget(QLabel("Max operations per task:"))
        self.max_ops_combo = QComboBox()
        for limit in [10, 25, 50, 100, 200]:
            self.max_ops_combo.addItem(str(limit), limit)
        self.max_ops_combo.setCurrentText("50")
        max_ops_layout.addWidget(self.max_ops_combo)
        limits_layout.addLayout(max_ops_layout)
        
        # Timeout
        timeout_layout = QHBoxLayout()
        timeout_layout.addWidget(QLabel("Timeout (seconds):"))
        self.timeout_combo = QComboBox()
        for timeout in [60, 120, 300, 600, 1200]:
            self.timeout_combo.addItem(f"{timeout}s", timeout)
        self.timeout_combo.setCurrentText("300s")
        timeout_layout.addWidget(self.timeout_combo)
        limits_layout.addLayout(timeout_layout)
        
        layout.addWidget(limits_group)
        
        layout.addStretch()
    
    def _connect_signals(self):
        """Connect UI signals"""
        self.mode_combo.currentIndexChanged.connect(self._update_settings)
        self.auto_approve_cb.toggled.connect(self._update_settings)
        self.confirm_modifications_cb.toggled.connect(self._update_settings)
        self.enable_safety_cb.toggled.connect(self._update_settings)
        self.max_ops_combo.currentIndexChanged.connect(self._update_settings)
        self.timeout_combo.currentIndexChanged.connect(self._update_settings)
    
    def _update_settings(self):
        """Update settings from UI"""
        self.settings.mode = self.mode_combo.currentData()
        self.settings.auto_approve_safe_operations = (
            self.auto_approve_cb.isChecked()
        )
        self.settings.require_confirmation_for_modifications = (
            self.confirm_modifications_cb.isChecked()
        )
        self.settings.enable_safety_validation = (
            self.enable_safety_cb.isChecked()
        )
        self.settings.max_operations_per_task = (
            self.max_ops_combo.currentData()
        )
        self.settings.timeout_seconds = self.timeout_combo.currentData()
        
        self.mode_changed.emit(self.settings.mode)
        self.settings_changed.emit(self.settings)
    
    def get_settings(self) -> AgentControlSettings:
        """Get current settings"""
        return self.settings
    
    def set_settings(self, settings: AgentControlSettings):
        """Set control panel settings"""
        self.settings = settings
        
        # Update UI
        for i in range(self.mode_combo.count()):
            if self.mode_combo.itemData(i) == settings.mode:
                self.mode_combo.setCurrentIndex(i)
                break
        
        self.auto_approve_cb.setChecked(settings.auto_approve_safe_operations)
        self.confirm_modifications_cb.setChecked(
            settings.require_confirmation_for_modifications
        )
        self.enable_safety_cb.setChecked(settings.enable_safety_validation)

        # Update combo boxes
        self.max_ops_combo.setCurrentText(
            str(settings.max_operations_per_task)
        )
        self.timeout_combo.setCurrentText(f"{settings.timeout_seconds}s")


class AgentStatusPanel(QWidget):
    """Status panel showing agent execution progress"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_task_id: Optional[str] = None
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the status panel UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Status header
        self.status_label = QLabel("Agent Status: Idle")
        self.status_label.setStyleSheet("font-weight: bold; color: #666;")
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Current operation
        self.operation_label = QLabel("")
        self.operation_label.setStyleSheet("color: #444; font-size: 11px;")
        self.operation_label.setVisible(False)
        layout.addWidget(self.operation_label)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        self.stop_button.setVisible(False)
        button_layout.addWidget(self.stop_button)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        layout.addStretch()
    
    def show_task_started(self, task_id: str):
        """Show that a task has started"""
        self.current_task_id = task_id
        self.status_label.setText("Agent Status: Executing")
        self.status_label.setStyleSheet("font-weight: bold; color: #4caf50;")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.operation_label.setVisible(True)
        self.stop_button.setVisible(True)
    
    def update_progress(self, task_id: str, operation: str, progress: int):
        """Update task progress"""
        if task_id == self.current_task_id:
            self.progress_bar.setValue(progress)
            self.operation_label.setText(f"Current: {operation}")
    
    def show_task_completed(self, task_id: str):
        """Show that a task has completed"""
        if task_id == self.current_task_id:
            self.status_label.setText("Agent Status: Completed")
            self.status_label.setStyleSheet(
                "font-weight: bold; color: #2196f3;"
            )
            self.progress_bar.setValue(100)
            self.operation_label.setText("Task completed successfully")
            
            # Hide after delay
            QTimer.singleShot(3000, self._reset_status)
    
    def show_task_failed(self, task_id: str, error: str):
        """Show that a task has failed"""
        if task_id == self.current_task_id:
            self.status_label.setText("Agent Status: Failed")
            self.status_label.setStyleSheet(
                "font-weight: bold; color: #f44336;"
            )
            self.operation_label.setText(f"Error: {error}")
            
            # Hide after delay
            QTimer.singleShot(5000, self._reset_status)
    
    def _reset_status(self):
        """Reset status to idle"""
        self.current_task_id = None
        self.status_label.setText("Agent Status: Idle")
        self.status_label.setStyleSheet("font-weight: bold; color: #666;")
        self.progress_bar.setVisible(False)
        self.operation_label.setVisible(False)
        self.stop_button.setVisible(False)


class AgentConversationIntegration(QObject):
    """Main integration class connecting agents with conversation UI"""
    
    agent_message = Signal(str)  # message for conversation
    approval_requested = Signal(str, str, dict)  # task_id, operation, details
    
    def __init__(self, conversation_widget: ConversationWidget, parent=None):
        super().__init__(parent)
        self.conversation_widget = conversation_widget
        self.agent_framework = AIAgentFramework()
        self.current_thread: Optional[AgentExecutionThread] = None
        self.pending_approvals: Dict[str, AgentExecutionThread] = {}
        
        # Control components
        self.control_panel = AgentControlPanel()
        self.status_panel = AgentStatusPanel()
        
        self._setup_integration()
        
        logger.info("Agent conversation integration initialized")
    
    def _setup_integration(self):
        """Set up the integration between agents and conversation"""
        # Connect conversation widget signals
        self.conversation_widget.message_sent.connect(
            self._handle_user_message
        )
        
        # Connect control panel signals
        self.control_panel.settings_changed.connect(self._on_settings_changed)
        
        # Connect status panel signals
        self.status_panel.stop_button.clicked.connect(self._stop_current_task)
        
        # Initialize agent framework
        asyncio.run(self._initialize_framework())
    
    async def _initialize_framework(self):
        """Initialize the agent framework"""
        try:
            await self.agent_framework.initialize()
            self._add_system_message(
                "Agent framework initialized successfully"
            )
            agents_list = ', '.join(
                self.agent_framework.get_available_agents()
            )
            self._add_system_message(
                f"Available agents: {agents_list}"
            )
        except Exception as e:
            logger.error(f"Failed to initialize agent framework: {e}")
            self._add_error_message(f"Failed to initialize agents: {e}")
    
    def _handle_user_message(self, text: str, attachments: List[str]):
        """Handle user message and potentially trigger agent execution"""
        settings = self.control_panel.get_settings()
        
        # Check if message contains agent request keywords
        agent_keywords = [
            'create', 'make', 'build', 'design', 'model', 'sketch', 'draw',
            'analyze', 'measure', 'calculate', 'modify', 'change', 'update',
            'delete', 'remove', 'move', 'rotate', 'scale', 'copy', 'mirror'
        ]
        
        text_lower = text.lower()
        contains_agent_request = any(
            keyword in text_lower for keyword in agent_keywords
        )

        if settings.mode != AgentMode.DISABLED and contains_agent_request:
            self._execute_agent_task(text, settings)
        else:
            # Pass through to regular AI conversation
            self._add_system_message(
                "Message passed to AI provider (agents disabled)"
            )

    def _execute_agent_task(self, task_text: str,
                            settings: AgentControlSettings):
        """Execute an agent task"""
        if self.current_thread and self.current_thread.isRunning():
            self._add_error_message(
                "Another agent task is already running. "
                "Please wait or stop it first."
            )
            return
        
        # Create and start execution thread
        self.current_thread = AgentExecutionThread(
            self.agent_framework, task_text, settings
        )
        
        # Connect thread signals
        self.current_thread.task_started.connect(self._on_task_started)
        self.current_thread.task_progress.connect(self._on_task_progress)
        self.current_thread.task_completed.connect(self._on_task_completed)
        self.current_thread.task_failed.connect(self._on_task_failed)
        self.current_thread.operation_pending.connect(
            self._on_operation_pending
        )

        # Start execution
        self.current_thread.start()

        self._add_system_message(
            f"Starting agent task in {settings.mode.value} mode..."
        )
    
    def _on_task_started(self, task_id: str):
        """Handle task started"""
        self.status_panel.show_task_started(task_id)
        self._add_system_message("Agent execution started")
    
    def _on_task_progress(self, task_id: str, operation: str, progress: int):
        """Handle task progress update"""
        self.status_panel.update_progress(task_id, operation, progress)
        
        # Add progress message occasionally
        if progress % 25 == 0:  # Every 25%
            self._add_system_message(f"Progress: {operation} ({progress}%)")
    
    def _on_task_completed(self, task_id: str, result: TaskResult):
        """Handle task completion"""
        self.status_panel.show_task_completed(task_id)
        
        # Add result message
        if result.status == TaskStatus.COMPLETED:
            operations_count = len(result.operations_performed)
            self._add_assistant_message(
                f"Task completed successfully!\n\n"
                f"**Operations performed:** {operations_count}\n"
                f"**Result:** {result.result}\n\n"
                f"Details:\n{json.dumps(result.metadata, indent=2)}"
            )
        else:
            self._add_assistant_message(
                f"Task completed with status: {result.status.value}\n"
                f"Result: {result.result}"
            )
    
    def _on_task_failed(self, task_id: str, error: str):
        """Handle task failure"""
        self.status_panel.show_task_failed(task_id, error)
        self._add_error_message(f"Agent task failed: {error}")
    
    def _on_operation_pending(self, task_id: str, operation: str,
                              details: dict):
        """Handle operation pending approval"""
        self.pending_approvals[task_id] = self.current_thread
        
        # Create approval message
        risk_level = "🟡 Medium" if details.get('modifies_model') else "🟢 Low"
        
        approval_msg = (
            f"**Operation Approval Required**\n\n"
            f"**Operation:** {operation}\n"
            f"**Risk Level:** {risk_level}\n"
            f"**Details:** {details.get('description', 'No description')}\n\n"
            f"Do you want to proceed?"
        )
        
        # Add message with approval buttons
        self._add_approval_message(approval_msg, task_id, operation)
    
    def _add_approval_message(self, message: str, task_id: str,
                              operation: str):
        """Add a message that requires approval"""
        # Create chat message
        chat_message = ChatMessage(
            id=f"approval_{task_id}_{datetime.now().timestamp()}",
            type=MessageType.SYSTEM,
            content=message,
            timestamp=datetime.now(),
            metadata={
                'requires_approval': True,
                'task_id': task_id,
                'operation': operation
            }
        )
        
        self.conversation_widget.add_message(chat_message)
        
        # Show approval dialog
        reply = QMessageBox.question(
            self.conversation_widget,
            "Agent Operation Approval",
            f"Agent wants to perform: {operation}\n\nDo you approve?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        approved = reply == QMessageBox.Yes
        
        # Send approval to thread
        if task_id in self.pending_approvals:
            self.pending_approvals[task_id].approve_operation(approved)
            del self.pending_approvals[task_id]
        
        # Add approval result message
        result_msg = "✅ Approved" if approved else "❌ Rejected"
        self._add_system_message(f"Operation {operation}: {result_msg}")
    
    def _stop_current_task(self):
        """Stop the current agent task"""
        if self.current_thread and self.current_thread.isRunning():
            self.current_thread.stop_execution()
            self._add_system_message("Agent task stopped by user")
    
    def _on_settings_changed(self, settings: AgentControlSettings):
        """Handle settings change"""
        self._add_system_message(
            f"Agent mode changed to: {settings.mode.value}"
        )
    
    def _add_system_message(self, text: str):
        """Add a system message to conversation"""
        self.conversation_widget.add_system_message(text)
    
    def _add_assistant_message(self, text: str):
        """Add an assistant message to conversation"""
        self.conversation_widget.add_assistant_message(
            text, provider="AI Agent"
        )
    
    def _add_error_message(self, text: str):
        """Add an error message to conversation"""
        message = ChatMessage(
            id=f"error_{datetime.now().timestamp()}",
            type=MessageType.ERROR,
            content=text,
            timestamp=datetime.now()
        )
        self.conversation_widget.add_message(message)
    
    def get_control_panel(self) -> AgentControlPanel:
        """Get the agent control panel widget"""
        return self.control_panel
    
    def get_status_panel(self) -> AgentStatusPanel:
        """Get the agent status panel widget"""
        return self.status_panel
    
    def is_agent_busy(self) -> bool:
        """Check if agent is currently executing a task"""
        return (self.current_thread is not None and
                self.current_thread.isRunning())

    def get_agent_capabilities(self) -> Dict[str, List[str]]:
        """Get available agent capabilities"""
        return self.agent_framework.get_capabilities()
