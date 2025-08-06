"""
Base Agent Class for FreeCAD AI Addon Agent Framework.
Defines the common interface and functionality for all specialized agents.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import logging

try:
    import FreeCAD as App
    import FreeCADGui as Gui
except ImportError:
    # Mock for testing outside FreeCAD
    App = None
    Gui = None

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Status of task execution"""
    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskType(Enum):
    """Types of tasks agents can handle"""
    GEOMETRY_CREATION = "geometry_creation"
    GEOMETRY_MODIFICATION = "geometry_modification"
    SKETCH_CREATION = "sketch_creation"
    SKETCH_MODIFICATION = "sketch_modification"
    ANALYSIS = "analysis"
    VALIDATION = "validation"
    OPTIMIZATION = "optimization"


@dataclass
class TaskResult:
    """Result of task execution"""
    status: TaskStatus
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_objects: Optional[List[str]] = None
    modified_objects: Optional[List[str]] = None
    execution_time: Optional[float] = None


@dataclass
class AgentTask:
    """Task definition for agents"""
    id: str
    task_type: TaskType
    description: str
    parameters: Dict[str, Any]
    context: Dict[str, Any]
    priority: int = 1
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


class BaseAgent(ABC):
    """
    Base class for all FreeCAD AI agents.
    
    Provides common functionality and defines the interface
    that all specialized agents must implement.
    """
    
    def __init__(self, name: str, agent_type: str):
        """
        Initialize the base agent.
        
        Args:
            name: Human-readable name of the agent
            agent_type: Type identifier for the agent
        """
        self.name = name
        self.agent_type = agent_type
        self.capabilities = []
        self.current_task = None
        self.task_history = []
        self.logger = logging.getLogger(f"{__name__}.{name}")
        
    @abstractmethod
    def can_handle_task(self, task: AgentTask) -> bool:
        """
        Determine if this agent can handle the given task.
        
        Args:
            task: The task to evaluate
            
        Returns:
            True if agent can handle the task, False otherwise
        """
        pass
    
    @abstractmethod
    def execute_task(self, task: AgentTask) -> TaskResult:
        """
        Execute the given task.
        
        Args:
            task: The task to execute
            
        Returns:
            Result of task execution
        """
        pass
    
    @abstractmethod
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """
        Validate task parameters before execution.
        
        Args:
            parameters: Task parameters to validate
            
        Returns:
            True if parameters are valid, False otherwise
        """
        pass
    
    def get_capabilities(self) -> List[TaskType]:
        """
        Get list of task types this agent can handle.
        
        Returns:
            List of supported task types
        """
        return self.capabilities.copy()
    
    def get_current_task(self) -> Optional[AgentTask]:
        """
        Get the currently executing task.
        
        Returns:
            Current task or None if no task is running
        """
        return self.current_task
    
    def get_task_history(self) -> List[Dict[str, Any]]:
        """
        Get history of executed tasks.
        
        Returns:
            List of task execution records
        """
        return self.task_history.copy()
    
    def pre_execute_validation(self, task: AgentTask) -> bool:
        """
        Perform validation before task execution.
        
        Args:
            task: Task to validate
            
        Returns:
            True if task can be executed safely
        """
        if not self.can_handle_task(task):
            self.logger.error(f"Agent {self.name} cannot handle task {task.id}")
            return False
            
        if not self.validate_parameters(task.parameters):
            self.logger.error(f"Invalid parameters for task {task.id}")
            return False
            
        # Check FreeCAD availability
        if App is None:
            self.logger.error("FreeCAD not available")
            return False
            
        # Check if document is available for geometry operations
        if task.task_type in [TaskType.GEOMETRY_CREATION, TaskType.GEOMETRY_MODIFICATION]:
            if not App.ActiveDocument:
                self.logger.error("No active FreeCAD document for geometry operations")
                return False
                
        return True
    
    def post_execute_cleanup(self, task: AgentTask, result: TaskResult):
        """
        Perform cleanup after task execution.
        
        Args:
            task: Executed task
            result: Task execution result
        """
        # Record task in history
        self.task_history.append({
            "task_id": task.id,
            "task_type": task.task_type.value,
            "status": result.status.value,
            "execution_time": result.execution_time,
            "timestamp": self._get_timestamp()
        })
        
        # Clear current task
        self.current_task = None
        
        # Trigger FreeCAD recompute if objects were created/modified
        if result.status == TaskStatus.COMPLETED and App and App.ActiveDocument:
            if result.created_objects or result.modified_objects:
                App.ActiveDocument.recompute()
                
        self.logger.info(f"Task {task.id} completed with status: {result.status.value}")
    
    def execute_with_safety(self, task: AgentTask) -> TaskResult:
        """
        Execute task with safety checks and error handling.
        
        Args:
            task: Task to execute
            
        Returns:
            Task execution result
        """
        import time
        start_time = time.time()
        
        try:
            # Pre-execution validation
            if not self.pre_execute_validation(task):
                return TaskResult(
                    status=TaskStatus.FAILED,
                    error_message="Pre-execution validation failed"
                )
            
            # Set current task
            self.current_task = task
            self.logger.info(f"Starting task {task.id}: {task.description}")
            
            # Execute the task
            result = self.execute_task(task)
            result.execution_time = time.time() - start_time
            
            # Post-execution cleanup
            self.post_execute_cleanup(task, result)
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Task {task.id} failed with exception: {str(e)}")
            
            result = TaskResult(
                status=TaskStatus.FAILED,
                error_message=str(e),
                execution_time=execution_time
            )
            
            self.post_execute_cleanup(task, result)
            return result
    
    def _get_timestamp(self) -> str:
        """Get current timestamp as ISO string"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def __str__(self) -> str:
        return f"{self.name} ({self.agent_type})"
    
    def __repr__(self) -> str:
        return f"BaseAgent(name='{self.name}', type='{self.agent_type}')"
