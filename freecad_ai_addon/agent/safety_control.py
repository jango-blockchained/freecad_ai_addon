"""
Agent Safety & Control System for FreeCAD AI Addon.
Provides safety mechanisms, user confirmations, and operation controls.
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime, timedelta

try:
    import FreeCAD as App
    import FreeCADGui as Gui
    from PySide6.QtWidgets import (
        QMessageBox,
        QDialog,
        QVBoxLayout,
        QLabel,
        QPushButton,
        QHBoxLayout,
    )
except ImportError:
    App = None
    Gui = None
    QMessageBox = None
    QDialog = None

from .base_agent import AgentTask

logger = logging.getLogger(__name__)


class SafetyLevel(Enum):
    """Safety levels for operations"""

    LOW = "low"  # Minimal safety checks
    MEDIUM = "medium"  # Standard safety checks
    HIGH = "high"  # Extensive safety checks
    CRITICAL = "critical"  # Maximum safety, user confirmation required


class OperationRisk(Enum):
    """Risk levels for operations"""

    SAFE = "safe"
    LOW_RISK = "low_risk"
    MEDIUM_RISK = "medium_risk"
    HIGH_RISK = "high_risk"
    DESTRUCTIVE = "destructive"


@dataclass
class SafetyConstraint:
    """Definition of a safety constraint"""

    name: str
    description: str
    check_function: Callable[[AgentTask, Dict[str, Any]], bool]
    risk_level: OperationRisk
    user_confirmation_required: bool = False
    auto_fix_available: bool = False
    fix_function: Optional[Callable] = None


@dataclass
class ResourceLimit:
    """Resource usage limits"""

    max_execution_time: float = 300.0  # seconds
    max_memory_usage: float = 1024.0  # MB
    max_objects_created: int = 100
    max_operations_per_minute: int = 60


@dataclass
class SafetyCheckResult:
    """Result of safety check"""

    passed: bool
    risk_level: OperationRisk
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    auto_fixes_available: List[str] = field(default_factory=list)


if QDialog is not None:

    class ConfirmationDialog(QDialog):
        """Dialog for user confirmation of risky operations"""

        def __init__(self, operation_details: Dict[str, Any], parent=None):
            super().__init__(parent)
            self.setWindowTitle("Operation Confirmation Required")
            self.setModal(True)
            self.setMinimumWidth(400)

            self.setup_ui(operation_details)
            self.result = False

        def setup_ui(self, details: Dict[str, Any]):
            """Setup the confirmation dialog UI"""
            layout = QVBoxLayout()

            # Title
            title = QLabel(f"<h3>{details.get('title', 'Confirm Operation')}</h3>")
            layout.addWidget(title)

            # Description
            desc_text = details.get(
                "description", "This operation requires confirmation."
            )
            desc = QLabel(desc_text)
            desc.setWordWrap(True)
            layout.addWidget(desc)

            # Risk level warning
            risk_level = details.get("risk_level", OperationRisk.MEDIUM_RISK)
            if risk_level in [OperationRisk.HIGH_RISK, OperationRisk.DESTRUCTIVE]:
                warning = QLabel(f"⚠️ Risk Level: {risk_level.value.upper()}")
                warning.setStyleSheet("color: red; font-weight: bold;")
                layout.addWidget(warning)

            # Affected objects
            if details.get("affected_objects"):
                obj_label = QLabel("Objects that will be affected:")
                layout.addWidget(obj_label)

                obj_list = QLabel("• " + "\n• ".join(details["affected_objects"]))
                obj_list.setStyleSheet("margin-left: 20px;")
                layout.addWidget(obj_list)

            # Preview button (if available)
            if details.get("preview_available"):
                preview_btn = QPushButton("Preview Changes")
                preview_btn.clicked.connect(self.show_preview)
                layout.addWidget(preview_btn)

            # Button layout
            button_layout = QHBoxLayout()

            confirm_btn = QPushButton("Confirm")
            confirm_btn.clicked.connect(self.accept)
            confirm_btn.setStyleSheet("background-color: #2ecc71; color: white;")

            cancel_btn = QPushButton("Cancel")
            cancel_btn.clicked.connect(self.reject)
            cancel_btn.setStyleSheet("background-color: #e74c3c; color: white;")

            button_layout.addWidget(cancel_btn)
            button_layout.addWidget(confirm_btn)

            layout.addLayout(button_layout)
            self.setLayout(layout)

        def show_preview(self):
            """Show preview of the operation"""
            # This would trigger a preview in FreeCAD
            # For now, just show a message
            QMessageBox.information(
                self,
                "Preview",
                "Preview functionality would show the operation result here.",
            )

        def accept(self):
            """User confirmed the operation"""
            self.result = True
            super().accept()

        def reject(self):
            """User cancelled the operation"""
            self.result = False
            super().reject()

    class ManualOverrideDialog(QDialog):
        """Dialog for manual override controls"""

        def __init__(self, agent_status: Dict[str, Any], parent=None):
            super().__init__(parent)
            self.setWindowTitle("Agent Manual Override")
            self.setModal(True)
            self.setup_ui(agent_status)

            self.action = None

        def setup_ui(self, status: Dict[str, Any]):
            """Setup manual override UI"""
            layout = QVBoxLayout()

            # Status info
            title = QLabel("<h3>Agent Override Control</h3>")
            layout.addWidget(title)

            status_text = f"Current Status: {status.get('status', 'Unknown')}"
            status_label = QLabel(status_text)
            layout.addWidget(status_label)

            if status.get("current_operation"):
                op_text = f"Current Operation: {status['current_operation']}"
                op_label = QLabel(op_text)
                layout.addWidget(op_label)

            # Control buttons
            button_layout = QVBoxLayout()

            pause_btn = QPushButton("Pause Agent")
            pause_btn.clicked.connect(lambda: self.set_action("pause"))
            button_layout.addWidget(pause_btn)

            stop_btn = QPushButton("Stop Current Operation")
            stop_btn.clicked.connect(lambda: self.set_action("stop"))
            button_layout.addWidget(stop_btn)

            approve_btn = QPushButton("Approve Next Step")
            approve_btn.clicked.connect(lambda: self.set_action("approve"))
            button_layout.addWidget(approve_btn)

            manual_btn = QPushButton("Take Manual Control")
            manual_btn.clicked.connect(lambda: self.set_action("manual"))
            button_layout.addWidget(manual_btn)

            cancel_btn = QPushButton("Cancel")
            cancel_btn.clicked.connect(self.reject)
            button_layout.addWidget(cancel_btn)

            layout.addLayout(button_layout)
            self.setLayout(layout)

        def set_action(self, action: str):
            """Set the override action and close dialog"""
            self.action = action
            self.accept()

else:
    # Dummy classes when Qt is not available
    class ConfirmationDialog:
        def __init__(self, operation_details: Dict[str, Any], parent=None):
            self.result = False

        def exec(self):
            return False

    class ManualOverrideDialog:
        def __init__(self, agent_status: Dict[str, Any], parent=None):
            self.action = None

        def exec(self):
            return False


class AgentSafetyController:
    """
    Comprehensive safety control system for AI agents.

    Provides operation validation, user confirmations, resource limits,
    rollback capabilities, and manual override controls.
    """

    def __init__(self, safety_level: SafetyLevel = SafetyLevel.MEDIUM):
        self.safety_level = safety_level
        self.resource_limits = ResourceLimit()
        self.safety_constraints = self._initialize_safety_constraints()

        # State tracking
        self.active_operations = {}
        self.operation_history = []
        self.rollback_states = {}
        self.paused = False
        self.manual_control = False

        # Resource monitoring
        self.operations_count = 0
        self.operations_start_time = datetime.now()

        self.logger = logging.getLogger(f"{__name__}.AgentSafetyController")

    def validate_operation(
        self, task: AgentTask, context: Dict[str, Any] = None
    ) -> SafetyCheckResult:
        """
        Validate operation against safety constraints.

        Args:
            task: Task to validate
            context: Current context

        Returns:
            Safety check result
        """
        result = SafetyCheckResult(passed=True, risk_level=OperationRisk.SAFE)

        context = context or {}

        # Check each safety constraint
        for constraint in self.safety_constraints:
            try:
                if not constraint.check_function(task, context):
                    result.passed = False

                    if constraint.risk_level.value in ["high_risk", "destructive"]:
                        result.errors.append(
                            f"Safety constraint failed: {constraint.description}"
                        )
                        result.risk_level = constraint.risk_level
                    else:
                        result.warnings.append(f"Warning: {constraint.description}")

                        # Update risk level if higher
                        if self._compare_risk_level(
                            constraint.risk_level, result.risk_level
                        ):
                            result.risk_level = constraint.risk_level

                    # Add auto-fix if available
                    if constraint.auto_fix_available:
                        result.auto_fixes_available.append(constraint.name)
                        result.suggestions.append(
                            f"Auto-fix available for: {constraint.name}"
                        )

            except Exception as e:
                self.logger.error(
                    f"Error checking constraint {constraint.name}: {str(e)}"
                )
                result.warnings.append(
                    f"Could not verify constraint: {constraint.name}"
                )

        # Resource limit checks
        self._check_resource_limits(task, context, result)

        return result

    def require_user_confirmation(
        self,
        task: AgentTask,
        safety_result: SafetyCheckResult,
        context: Dict[str, Any] = None,
    ) -> bool:
        """
        Show user confirmation dialog for risky operations.

        Args:
            task: Task requiring confirmation
            safety_result: Result of safety check
            context: Operation context

        Returns:
            True if user confirmed, False if cancelled
        """
        if not Gui or QDialog is None:
            # No GUI available, auto-deny risky operations or critical level operations
            if (
                safety_result.risk_level
                in [OperationRisk.HIGH_RISK, OperationRisk.DESTRUCTIVE]
                or self.safety_level == SafetyLevel.CRITICAL
            ):
                self.logger.warning("Operation denied - no GUI for confirmation")
                return False
            return True

        # Determine if confirmation is needed
        needs_confirmation = (
            safety_result.risk_level
            in [OperationRisk.HIGH_RISK, OperationRisk.DESTRUCTIVE]
            or self.safety_level == SafetyLevel.CRITICAL
            or bool(safety_result.errors)
        )

        if not needs_confirmation:
            return True

        # Prepare dialog details
        affected_objects = self._get_affected_objects(task, context)

        dialog_details = {
            "title": f"Confirm {task.task_type.value} Operation",
            "description": (
                f"Operation: {task.description}\n\n"
                f"Risk Level: {safety_result.risk_level.value}\n\n"
                + "\n".join(safety_result.warnings + safety_result.errors)
            ),
            "risk_level": safety_result.risk_level,
            "affected_objects": affected_objects,
            "preview_available": self._preview_available(task),
        }

        # Show confirmation dialog
        dialog = ConfirmationDialog(dialog_details)
        dialog.exec()

        confirmed = dialog.result
        self.logger.info(
            f"User {'confirmed' if confirmed else 'cancelled'} operation: {task.description}"
        )

        return confirmed

    def create_operation_preview(
        self, task: AgentTask, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Create a preview of the operation without executing it.

        Args:
            task: Task to preview
            context: Current context

        Returns:
            Preview information
        """
        preview = {
            "task_id": task.id,
            "operation": task.task_type.value,
            "description": task.description,
            "parameters": task.parameters,
            "preview_mode": True,
            "timestamp": datetime.now().isoformat(),
        }

        # Add specific preview information based on task type
        if task.task_type.value in ["box", "cylinder", "sphere"]:
            preview["preview_objects"] = [
                f"Preview_{task.parameters.get('name', 'Object')}"
            ]
            preview["geometry_info"] = self._calculate_geometry_preview(task)

        elif task.task_type.value.startswith("boolean_"):
            preview["affected_objects"] = task.parameters.get("objects", [])
            preview["operation_type"] = task.task_type.value

        elif task.task_type.value in ["add_fillet", "add_chamfer"]:
            preview["modified_object"] = task.parameters.get("obj_name")
            preview["feature_size"] = task.parameters.get("size", 0)

        return preview

    def setup_rollback_point(
        self, operation_id: str, context: Dict[str, Any] = None
    ) -> str:
        """
        Create a rollback point before executing operation.

        Args:
            operation_id: Unique operation identifier
            context: Current FreeCAD context

        Returns:
            Rollback point ID
        """
        rollback_id = f"rollback_{operation_id}_{int(datetime.now().timestamp())}"

        if App and App.ActiveDocument:
            # Capture current document state
            doc = App.ActiveDocument
            rollback_state = {
                "rollback_id": rollback_id,
                "operation_id": operation_id,
                "timestamp": datetime.now(),
                "object_count": len(doc.Objects),
                "object_names": [obj.Name for obj in doc.Objects],
                "document_name": doc.Name,
            }

            # Store detailed object information for critical operations
            if self.safety_level in [SafetyLevel.HIGH, SafetyLevel.CRITICAL]:
                rollback_state["object_details"] = {}
                for obj in doc.Objects:
                    try:
                        rollback_state["object_details"][obj.Name] = {
                            "type": obj.TypeId,
                            "label": obj.Label,
                            "placement": (
                                str(obj.Placement)
                                if hasattr(obj, "Placement")
                                else None
                            ),
                        }
                    except Exception:
                        pass  # Skip objects that can't be serialized

            self.rollback_states[rollback_id] = rollback_state
            self.logger.info(f"Created rollback point: {rollback_id}")

        return rollback_id

    def execute_rollback(self, rollback_id: str) -> bool:
        """
        Rollback to a previous state.

        Args:
            rollback_id: ID of rollback point

        Returns:
            True if rollback successful
        """
        if rollback_id not in self.rollback_states:
            self.logger.error(f"Rollback point not found: {rollback_id}")
            return False

        if not App or not App.ActiveDocument:
            self.logger.error("No active FreeCAD document for rollback")
            return False

        try:
            rollback_state = self.rollback_states[rollback_id]
            doc = App.ActiveDocument

            # Get current objects
            current_objects = {obj.Name: obj for obj in doc.Objects}
            target_objects = set(rollback_state["object_names"])

            # Remove objects created after rollback point
            objects_to_remove = []
            for obj_name in current_objects:
                if obj_name not in target_objects:
                    objects_to_remove.append(current_objects[obj_name])

            # Remove in reverse dependency order to avoid conflicts
            for obj in reversed(objects_to_remove):
                try:
                    doc.removeObject(obj.Name)
                    self.logger.info(f"Removed object during rollback: {obj.Name}")
                except Exception as e:
                    self.logger.warning(f"Could not remove object {obj.Name}: {str(e)}")

            # Recompute document
            doc.recompute()

            self.logger.info(f"Rollback completed: {rollback_id}")
            return True

        except Exception as e:
            self.logger.error(f"Rollback failed: {str(e)}")
            return False

    def check_resource_limits(self, task: AgentTask) -> bool:
        """Check if operation would exceed resource limits"""
        # Reset counter if more than a minute has passed
        if datetime.now() - self.operations_start_time > timedelta(minutes=1):
            self.operations_count = 0
            self.operations_start_time = datetime.now()

        # Check operation rate limit
        if self.operations_count >= self.resource_limits.max_operations_per_minute:
            self.logger.warning("Operation rate limit exceeded")
            return False

        # Check object count limit
        if App and App.ActiveDocument:
            try:
                current_objects = len(App.ActiveDocument.Objects)
                if current_objects >= self.resource_limits.max_objects_created:
                    self.logger.warning("Object count limit exceeded")
                    return False
            except (TypeError, AttributeError):
                # Handle case where Objects is mocked or not available
                pass

        return True

    def show_manual_override_dialog(
        self, agent_status: Dict[str, Any]
    ) -> Optional[str]:
        """
        Show manual override control dialog.

        Args:
            agent_status: Current agent status information

        Returns:
            Selected override action or None
        """
        if not Gui or QDialog is None:
            return None

        dialog = ManualOverrideDialog(agent_status)
        dialog.exec()

        return dialog.action

    def pause_agent(self):
        """Pause agent operations"""
        self.paused = True
        self.logger.info("Agent operations paused")

    def resume_agent(self):
        """Resume agent operations"""
        self.paused = False
        self.logger.info("Agent operations resumed")

    def enable_manual_control(self):
        """Enable manual control mode"""
        self.manual_control = True
        self.paused = True
        self.logger.info("Manual control mode enabled")

    def disable_manual_control(self):
        """Disable manual control mode"""
        self.manual_control = False
        self.paused = False
        self.logger.info("Manual control mode disabled")

    def is_operation_allowed(self) -> bool:
        """Check if operations are currently allowed"""
        return not self.paused and not self.manual_control

    def _initialize_safety_constraints(self) -> List[SafetyConstraint]:
        """Initialize safety constraints"""
        constraints = []

        # Document existence check
        constraints.append(
            SafetyConstraint(
                name="document_exists",
                description="Active FreeCAD document required",
                check_function=lambda task, ctx: App is not None
                and App.ActiveDocument is not None,
                risk_level=OperationRisk.MEDIUM_RISK,
            )
        )

        # Object existence check for operations that modify objects
        def check_object_exists(task: AgentTask, context: Dict[str, Any]) -> bool:
            if task.task_type.value in [
                "add_fillet",
                "add_chamfer",
                "boolean_union",
                "boolean_difference",
            ]:
                obj_name = task.parameters.get("obj_name") or task.parameters.get(
                    "objects", []
                )
                if isinstance(obj_name, str):
                    return App.ActiveDocument.getObject(obj_name) is not None
                elif isinstance(obj_name, list):
                    return all(
                        App.ActiveDocument.getObject(name) is not None
                        for name in obj_name
                    )
            return True

        constraints.append(
            SafetyConstraint(
                name="object_exists",
                description="Target objects must exist",
                check_function=check_object_exists,
                risk_level=OperationRisk.HIGH_RISK,
            )
        )

        # Destructive operation check
        def check_destructive_operation(
            task: AgentTask, context: Dict[str, Any]
        ) -> bool:
            destructive_ops = ["boolean_difference", "remove_object", "clear_document"]

            # Check task type
            if task.task_type.value in destructive_ops:
                return False

            # Check operation in parameters
            operation = task.parameters.get("operation", "")
            if operation in destructive_ops:
                return False

            # Check description for destructive operations
            description_lower = task.description.lower()
            if any(op.replace("_", " ") in description_lower for op in destructive_ops):
                return False

            return True

        constraints.append(
            SafetyConstraint(
                name="destructive_operation",
                description="Destructive operation detected",
                check_function=check_destructive_operation,
                risk_level=OperationRisk.DESTRUCTIVE,
                user_confirmation_required=True,
            )
        )

        # Parameter validation
        def check_valid_parameters(task: AgentTask, context: Dict[str, Any]) -> bool:
            params = task.parameters

            # Check for required parameters based on task type
            if task.task_type.value == "box":
                return all(key in params for key in ["length", "width", "height"])
            elif task.task_type.value == "cylinder":
                return all(key in params for key in ["radius", "height"])
            elif task.task_type.value == "sphere":
                return "radius" in params

            return True

        constraints.append(
            SafetyConstraint(
                name="valid_parameters",
                description="Required parameters missing",
                check_function=check_valid_parameters,
                risk_level=OperationRisk.MEDIUM_RISK,
            )
        )

        return constraints

    def _check_resource_limits(
        self, task: AgentTask, context: Dict[str, Any], result: SafetyCheckResult
    ):
        """Check resource limits and update result"""
        if not self.check_resource_limits(task):
            result.passed = False
            result.errors.append("Resource limits exceeded")
            result.risk_level = OperationRisk.HIGH_RISK

    def _get_affected_objects(
        self, task: AgentTask, context: Dict[str, Any]
    ) -> List[str]:
        """Get list of objects that will be affected by the operation"""
        affected = []

        if task.task_type.value in ["add_fillet", "add_chamfer"]:
            obj_name = task.parameters.get("obj_name")
            if obj_name:
                affected.append(obj_name)

        elif task.task_type.value.startswith("boolean_"):
            objects = task.parameters.get("objects", [])
            affected.extend(objects)

        elif task.task_type.value in ["remove_object"]:
            obj_name = task.parameters.get("obj_name")
            if obj_name:
                affected.append(obj_name)

        return affected

    def _preview_available(self, task: AgentTask) -> bool:
        """Check if preview is available for this task type"""
        preview_supported = [
            "box",
            "cylinder",
            "sphere",
            "cone",
            "torus",
            "boolean_union",
            "boolean_difference",
            "boolean_intersection",
            "add_fillet",
            "add_chamfer",
        ]
        return task.task_type.value in preview_supported

    def _calculate_geometry_preview(self, task: AgentTask) -> Dict[str, Any]:
        """Calculate preview information for geometry operations"""
        if task.task_type.value == "box":
            params = task.parameters
            volume = (
                params.get("length", 0)
                * params.get("width", 0)
                * params.get("height", 0)
            )
            return {"volume": volume, "type": "box"}

        elif task.task_type.value == "cylinder":
            params = task.parameters
            radius = params.get("radius", 0)
            height = params.get("height", 0)
            volume = 3.14159 * radius * radius * height
            return {"volume": volume, "type": "cylinder"}

        elif task.task_type.value == "sphere":
            params = task.parameters
            radius = params.get("radius", 0)
            volume = (4 / 3) * 3.14159 * radius * radius * radius
            return {"volume": volume, "type": "sphere"}

        return {}

    def _compare_risk_level(self, level1: OperationRisk, level2: OperationRisk) -> bool:
        """Compare risk levels, return True if level1 is higher than level2"""
        risk_order = {
            OperationRisk.SAFE: 0,
            OperationRisk.LOW_RISK: 1,
            OperationRisk.MEDIUM_RISK: 2,
            OperationRisk.HIGH_RISK: 3,
            OperationRisk.DESTRUCTIVE: 4,
        }
        return risk_order[level1] > risk_order[level2]

    def get_safety_status(self) -> Dict[str, Any]:
        """Get current safety controller status"""
        return {
            "safety_level": self.safety_level.value,
            "paused": self.paused,
            "manual_control": self.manual_control,
            "active_operations": len(self.active_operations),
            "rollback_points": len(self.rollback_states),
            "operations_count": self.operations_count,
            "resource_limits": {
                "max_execution_time": self.resource_limits.max_execution_time,
                "max_memory_usage": self.resource_limits.max_memory_usage,
                "max_objects_created": self.resource_limits.max_objects_created,
                "max_operations_per_minute": self.resource_limits.max_operations_per_minute,
            },
        }
