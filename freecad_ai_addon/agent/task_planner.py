"""
Task Planner for FreeCAD AI Addon Agent Framework.
Coordinates multi-step operations and agent communication.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging
import uuid
from datetime import datetime

try:
    import FreeCAD as App
except ImportError:
    App = None

from .base_agent import BaseAgent, AgentTask, TaskResult, TaskStatus, TaskType

logger = logging.getLogger(__name__)


class PlanStatus(Enum):
    """Status of execution plan"""

    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskDependencyType(Enum):
    """Types of task dependencies"""

    SEQUENTIAL = "sequential"  # Must complete before next starts
    PARALLEL = "parallel"  # Can run in parallel
    CONDITIONAL = "conditional"  # Depends on result of previous task


@dataclass
class ExecutionPlan:
    """Plan for executing multiple related tasks"""

    id: str
    description: str
    tasks: List[AgentTask] = field(default_factory=list)
    dependencies: Dict[str, List[str]] = field(default_factory=dict)
    status: PlanStatus = PlanStatus.CREATED
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

    def add_task(self, task: AgentTask, dependencies: Optional[List[str]] = None):
        """Add task to execution plan"""
        self.tasks.append(task)
        if dependencies:
            self.dependencies[task.id] = dependencies

    def get_ready_tasks(self, completed_task_ids: List[str]) -> List[AgentTask]:
        """Get tasks that are ready to execute"""
        ready_tasks = []
        for task in self.tasks:
            if task.id not in completed_task_ids:
                deps = self.dependencies.get(task.id, [])
                if all(dep_id in completed_task_ids for dep_id in deps):
                    ready_tasks.append(task)
        return ready_tasks


class TaskPlanner:
    """
    Coordinates multi-step operations and manages agent communication.

    Handles task decomposition, dependency management, and execution planning
    for complex CAD operations that require multiple agents.
    """

    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.active_plans: Dict[str, ExecutionPlan] = {}
        self.completed_plans: Dict[str, ExecutionPlan] = {}
        self.task_templates = self._initialize_task_templates()
        self.logger = logging.getLogger(f"{__name__}.TaskPlanner")

    def register_agent(self, agent: BaseAgent):
        """Register an agent with the planner"""
        self.agents[agent.agent_type] = agent
        self.logger.info(f"Registered agent: {agent.name}")

    def parse_natural_language_request(
        self, request: str, context: Optional[Dict[str, Any]] = None
    ) -> ExecutionPlan:
        """
        Parse natural language request into execution plan.

        Args:
            request: Natural language description of desired operation
            context: Current FreeCAD context

        Returns:
            ExecutionPlan with decomposed tasks
        """
        self.logger.info(f"Parsing request: {request}")

        plan_id = str(uuid.uuid4())
        plan = ExecutionPlan(id=plan_id, description=request)

        # Analyze request to determine required operations
        operations = self._analyze_request(request, context)

        # Convert operations to agent tasks
        for i, operation in enumerate(operations):
            task_id = f"{plan_id}_task_{i}"

            task = AgentTask(
                id=task_id,
                task_type=operation["task_type"],
                description=operation["description"],
                parameters=operation["parameters"],
                context=context or {},
                priority=operation.get("priority", 1),
                dependencies=operation.get("dependencies", []),
            )

            plan.add_task(task, operation.get("dependencies", []))

        self.active_plans[plan_id] = plan
        return plan

    def execute_plan(self, plan: ExecutionPlan) -> Dict[str, TaskResult]:
        """
        Execute an execution plan.

        Args:
            plan: Plan to execute

        Returns:
            Dictionary mapping task IDs to results
        """
        self.logger.info(f"Executing plan: {plan.description}")

        plan.status = PlanStatus.RUNNING
        plan.started_at = datetime.now()

        completed_task_ids: set[str] = set()
        failed_tasks: set[str] = set()
        processed_task_ids: set[str] = set()  # completed or failed
        task_results: Dict[str, TaskResult] = {}

        try:
            while len(processed_task_ids) < len(plan.tasks):
                # Get tasks ready for execution, excluding already processed/failed ones
                ready_tasks = [
                    t
                    for t in plan.get_ready_tasks(list(completed_task_ids))
                    if t.id not in failed_tasks and t.id not in processed_task_ids
                ]

                if not ready_tasks:
                    if failed_tasks:
                        # No more tasks can be executed due to failures or blocked deps
                        break
                    else:
                        # Circular dependency or other issue
                        raise RuntimeError(
                            "No ready tasks found - possible circular dependency"
                        )

                # Execute ready tasks
                for task in ready_tasks:
                    try:
                        result = self._execute_single_task(task)
                        task_results[task.id] = result
                        processed_task_ids.add(task.id)

                        if result.status == TaskStatus.COMPLETED:
                            completed_task_ids.add(task.id)
                            self.logger.info(f"Task {task.id} completed successfully")
                        else:
                            failed_tasks.add(task.id)
                            self.logger.error(
                                f"Task {task.id} failed: {result.error_message}"
                            )

                            # Check if failure should stop execution
                            if self._is_critical_task(task):
                                raise RuntimeError(f"Critical task {task.id} failed")

                    except Exception as e:
                        self.logger.error(f"Exception in task {task.id}: {str(e)}")
                        task_results[task.id] = TaskResult(
                            status=TaskStatus.FAILED, error_message=str(e)
                        )
                        failed_tasks.add(task.id)
                        processed_task_ids.add(task.id)

            # Determine overall plan status
            if failed_tasks and len(completed_task_ids) < len(plan.tasks):
                plan.status = PlanStatus.FAILED
                plan.error_message = f"Failed tasks: {sorted(failed_tasks)}"
            else:
                plan.status = PlanStatus.COMPLETED

        except Exception as e:
            plan.status = PlanStatus.FAILED
            plan.error_message = str(e)
            self.logger.error(f"Plan execution failed: {str(e)}")

        finally:
            plan.completed_at = datetime.now()

            # Move to completed plans
            if plan.id in self.active_plans:
                del self.active_plans[plan.id]
            self.completed_plans[plan.id] = plan

        return task_results

    def execute_autonomous_task(
        self, description: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, TaskResult]:
        """
        Execute a task autonomously from description.

        Args:
            description: Natural language task description
            context: FreeCAD context

        Returns:
            Task execution results
        """
        plan = self.parse_natural_language_request(description, context)
        return self.execute_plan(plan)

    def get_plan_status(self, plan_id: str) -> Optional[ExecutionPlan]:
        """Get status of execution plan"""
        return self.active_plans.get(plan_id) or self.completed_plans.get(plan_id)

    def cancel_plan(self, plan_id: str) -> bool:
        """Cancel active execution plan"""
        if plan_id in self.active_plans:
            plan = self.active_plans[plan_id]
            plan.status = PlanStatus.CANCELLED
            plan.completed_at = datetime.now()

            del self.active_plans[plan_id]
            self.completed_plans[plan_id] = plan

            self.logger.info(f"Cancelled plan: {plan_id}")
            return True
        return False

    def _execute_single_task(self, task: AgentTask) -> TaskResult:
        """Execute a single task using appropriate agent"""
        # Find suitable agent
        suitable_agents = []
        for agent in self.agents.values():
            if agent.can_handle_task(task):
                suitable_agents.append(agent)

        if not suitable_agents:
            return TaskResult(
                status=TaskStatus.FAILED,
                error_message=f"No agent found for task type: {task.task_type}",
            )

        # Select best agent (for now, just use first suitable)
        agent = suitable_agents[0]

        # Execute task with safety checks
        return agent.execute_with_safety(task)

    def _analyze_request(
        self, request: str, context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Analyze natural language request to extract operations.

        This is a simplified implementation. A real system would use
        more sophisticated NLP and intent recognition.
        """
        request_lower = request.lower()
        operations = []

        # Pattern matching for common requests
        if "create" in request_lower and "box" in request_lower:
            operations.extend(self._parse_create_box_request(request, context))

        elif "create" in request_lower and "cylinder" in request_lower:
            operations.extend(self._parse_create_cylinder_request(request, context))

        elif "create" in request_lower and "sphere" in request_lower:
            operations.extend(self._parse_create_sphere_request(request, context))

        elif "fillet" in request_lower:
            operations.extend(self._parse_fillet_request(request, context))

        elif "chamfer" in request_lower:
            operations.extend(self._parse_chamfer_request(request, context))

        elif "sketch" in request_lower:
            operations.extend(self._parse_sketch_request(request, context))

        elif "analyze" in request_lower:
            operations.extend(self._parse_analysis_request(request, context))

        elif (
            "boolean" in request_lower
            or "union" in request_lower
            or "difference" in request_lower
        ):
            operations.extend(self._parse_boolean_request(request, context))

        else:
            # Fallback: try to match against known templates
            operations.extend(self._match_templates(request, context))

        if not operations:
            # Default fallback - create basic analysis task
            operations.append(
                {
                    "task_type": TaskType.ANALYSIS,
                    "description": f"Analyze request: {request}",
                    "parameters": {
                        "operation": "geometric_properties",
                        "request": request,
                    },
                    "priority": 1,
                }
            )

        return operations

    def _parse_create_box_request(
        self, request: str, context: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Parse box creation request"""
        # Extract dimensions using simple pattern matching
        import re

        # Look for dimension patterns like "10mm", "5 mm", "20x30x40"
        dimension_patterns = [
            r"(\d+(?:\.\d+)?)\s*x\s*(\d+(?:\.\d+)?)\s*x\s*(\d+(?:\.\d+)?)",  # 10x20x30
            r"(\d+(?:\.\d+)?)\s*mm\s*(?:by|x)\s*(\d+(?:\.\d+)?)\s*mm\s*(?:by|x)\s*(\d+(?:\.\d+)?)\s*mm",  # 10mm x 20mm x 30mm
        ]

        dimensions = None
        for pattern in dimension_patterns:
            match = re.search(pattern, request.lower())
            if match:
                dimensions = [
                    float(match.group(1)),
                    float(match.group(2)),
                    float(match.group(3)),
                ]
                break

        # Default dimensions if not found
        if not dimensions:
            # Look for single dimension
            single_dim_match = re.search(r"(\d+(?:\.\d+)?)\s*mm", request.lower())
            if single_dim_match:
                dim = float(single_dim_match.group(1))
                dimensions = [dim, dim, dim]  # Cube
            else:
                dimensions = [10, 10, 10]  # Default 10mm cube

        return [
            {
                "task_type": TaskType.GEOMETRY_CREATION,
                "description": f"Create box with dimensions {dimensions}",
                "parameters": {
                    "operation": "create_box",
                    "length": dimensions[0],
                    "width": dimensions[1],
                    "height": dimensions[2],
                    "name": self._extract_name(request, "Box"),
                },
                "priority": 1,
            }
        ]

    def _parse_create_cylinder_request(
        self, request: str, context: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Parse cylinder creation request"""
        import re

        # Look for radius and height
        radius_match = re.search(r"radius\s*(\d+(?:\.\d+)?)", request.lower())
        height_match = re.search(r"height\s*(\d+(?:\.\d+)?)", request.lower())

        radius = float(radius_match.group(1)) if radius_match else 5.0
        height = float(height_match.group(1)) if height_match else 10.0

        return [
            {
                "task_type": TaskType.GEOMETRY_CREATION,
                "description": f"Create cylinder with radius {radius} and height {height}",
                "parameters": {
                    "operation": "create_cylinder",
                    "radius": radius,
                    "height": height,
                    "name": self._extract_name(request, "Cylinder"),
                },
                "priority": 1,
            }
        ]

    def _parse_create_sphere_request(
        self, request: str, context: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Parse sphere creation request"""
        import re

        # Look for radius
        radius_match = re.search(r"radius\s*(\d+(?:\.\d+)?)", request.lower())

        radius = float(radius_match.group(1)) if radius_match else 5.0

        return [
            {
                "task_type": TaskType.GEOMETRY_CREATION,
                "description": f"Create sphere with radius {radius}",
                "parameters": {
                    "operation": "create_sphere",
                    "radius": radius,
                    "name": self._extract_name(request, "Sphere"),
                },
                "priority": 1,
            }
        ]

    def _parse_fillet_request(
        self, request: str, context: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Parse fillet request"""
        import re

        # Extract radius
        radius_match = re.search(r"(\d+(?:\.\d+)?)\s*mm", request.lower())
        radius = float(radius_match.group(1)) if radius_match else 2.0

        # Get selected object from context
        selected_object = self._get_selected_object(context)

        return [
            {
                "task_type": TaskType.GEOMETRY_MODIFICATION,
                "description": f"Add {radius}mm fillet to {selected_object}",
                "parameters": {
                    "operation": "add_fillet",
                    "object": selected_object,
                    "radius": radius,
                    "name": f"{selected_object}_Fillet",
                },
                "priority": 1,
            }
        ]

    def _parse_chamfer_request(
        self, request: str, context: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Parse chamfer request"""
        import re

        # Extract size
        size_match = re.search(r"(\d+(?:\.\d+)?)\s*mm", request.lower())
        size = float(size_match.group(1)) if size_match else 1.0

        # Get selected object from context
        selected_object = self._get_selected_object(context)

        return [
            {
                "task_type": TaskType.GEOMETRY_MODIFICATION,
                "description": f"Add {size}mm chamfer to {selected_object}",
                "parameters": {
                    "operation": "add_chamfer",
                    "object": selected_object,
                    "radius": size,  # Using radius parameter for chamfer size
                    "name": f"{selected_object}_Chamfer",
                },
                "priority": 1,
            }
        ]

    def _parse_sketch_request(
        self, request: str, context: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Parse sketch creation request"""
        operations = []

        # Create sketch first
        operations.append(
            {
                "task_type": TaskType.SKETCH_CREATION,
                "description": "Create new sketch",
                "parameters": {
                    "operation": "create_sketch",
                    "plane": "XY",  # Default plane
                    "name": self._extract_name(request, "Sketch"),
                },
                "priority": 1,
            }
        )

        # Add geometric elements based on request
        if "rectangle" in request.lower():
            operations.append(
                {
                    "task_type": TaskType.SKETCH_MODIFICATION,
                    "description": "Add rectangle to sketch",
                    "parameters": {
                        "operation": "add_rectangle",
                        "sketch": "Sketch",  # Reference to created sketch
                        "corner1": [0, 0],
                        "corner2": [10, 10],  # Default size
                    },
                    "priority": 2,
                    "dependencies": [
                        operations[0]["task_id"] if "task_id" in operations[0] else None
                    ],
                }
            )

        return operations

    def _parse_analysis_request(
        self, request: str, context: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Parse analysis request"""
        selected_object = self._get_selected_object(context)

        if "3d print" in request.lower() or "printing" in request.lower():
            operation = "printability_analysis"
            description = f"Analyze 3D printability of {selected_object}"
        elif "stress" in request.lower() or "strength" in request.lower():
            operation = "structural_analysis"
            description = f"Analyze structural properties of {selected_object}"
        elif "volume" in request.lower():
            operation = "volume_analysis"
            description = f"Analyze volume of {selected_object}"
        else:
            operation = "geometric_properties"
            description = f"Analyze geometric properties of {selected_object}"

        return [
            {
                "task_type": TaskType.ANALYSIS,
                "description": description,
                "parameters": {"operation": operation, "object": selected_object},
                "priority": 1,
            }
        ]

    def _parse_boolean_request(
        self, request: str, context: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Parse boolean operation request"""
        selected_objects = self._get_selected_objects(context)

        if "union" in request.lower():
            operation = "boolean_union"
        elif "difference" in request.lower():
            operation = "boolean_difference"
        elif "intersection" in request.lower():
            operation = "boolean_intersection"
        else:
            operation = "boolean_union"  # Default

        return [
            {
                "task_type": TaskType.GEOMETRY_MODIFICATION,
                "description": f"Perform {operation} on selected objects",
                "parameters": {
                    "operation": operation,
                    "objects": selected_objects,
                    "name": operation.title(),
                },
                "priority": 1,
            }
        ]

    def _match_templates(
        self, request: str, context: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Match request against predefined templates"""
        # This would contain more sophisticated template matching
        # For now, return empty list
        return []

    def _extract_name(self, request: str, default: str) -> str:
        """Extract object name from request"""
        # Simple name extraction
        # Could be enhanced with more sophisticated parsing
        import re

        name_patterns = [r"name\s+it\s+(\w+)", r"call\s+it\s+(\w+)", r"named\s+(\w+)"]

        for pattern in name_patterns:
            match = re.search(pattern, request.lower())
            if match:
                return match.group(1).title()

        return default

    def _get_selected_object(self, context: Optional[Dict[str, Any]]) -> str:
        """Get selected object from context"""
        if context and "selected_objects" in context:
            selected = context["selected_objects"]
            if selected:
                return selected[0]
        return "Object"  # Default name

    def _get_selected_objects(self, context: Optional[Dict[str, Any]]) -> List[str]:
        """Get all selected objects from context"""
        if context and "selected_objects" in context:
            return context["selected_objects"]
        return ["Object1", "Object2"]  # Default names

    def _is_critical_task(self, task: AgentTask) -> bool:
        """Determine if task is critical for overall plan success"""
        # For now, all tasks are considered critical
        # Could be enhanced with priority-based logic
        return True

    def _initialize_task_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize predefined task templates"""
        return {
            "create_basic_part": {
                "description": "Create basic parametric part",
                "tasks": [
                    {"type": TaskType.SKETCH_CREATION, "operation": "create_sketch"},
                    {
                        "type": TaskType.SKETCH_MODIFICATION,
                        "operation": "add_rectangle",
                    },
                    {"type": TaskType.GEOMETRY_CREATION, "operation": "extrude_sketch"},
                ],
            },
            "analyze_for_printing": {
                "description": "Complete 3D printing analysis",
                "tasks": [
                    {"type": TaskType.ANALYSIS, "operation": "geometric_properties"},
                    {"type": TaskType.ANALYSIS, "operation": "printability_analysis"},
                    {"type": TaskType.ANALYSIS, "operation": "wall_thickness_analysis"},
                ],
            },
        }

    def get_active_plans(self) -> Dict[str, ExecutionPlan]:
        """Get all active execution plans"""
        return self.active_plans.copy()

    def get_completed_plans(self) -> Dict[str, ExecutionPlan]:
        """Get all completed execution plans"""
        return self.completed_plans.copy()

    def get_agent_capabilities(self) -> Dict[str, List[TaskType]]:
        """Get capabilities of all registered agents"""
        capabilities = {}
        for agent_type, agent in self.agents.items():
            capabilities[agent_type] = agent.get_capabilities()
        return capabilities
