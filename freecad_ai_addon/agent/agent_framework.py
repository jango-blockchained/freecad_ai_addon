"""
AI Agent Framework for FreeCAD AI Addon.
Main coordination system for multi-agent autonomous operations.
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

try:
    import FreeCAD as App
    import FreeCADGui as Gui
except ImportError:
    App = None
    Gui = None

from .base_agent import AgentTask, TaskResult, TaskStatus
from .geometry_agent import GeometryAgent
from .sketch_agent import SketchAgent
from .analysis_agent import AnalysisAgent
from .task_planner import TaskPlanner, ExecutionPlan

logger = logging.getLogger(__name__)


class AIAgentFramework:
    """
    Main AI Agent Framework for autonomous FreeCAD operations.

    Coordinates multiple specialized agents to perform complex
    CAD operations through natural language instructions.
    """

    def __init__(self):
        """Initialize the agent framework"""
        self.logger = logging.getLogger(f"{__name__}.AIAgentFramework")

        # Initialize agents
        self.geometry_agent = GeometryAgent()
        self.sketch_agent = SketchAgent()
        self.analysis_agent = AnalysisAgent()

        # Initialize task planner
        self.task_planner = TaskPlanner()

        # Register agents with planner
        self.task_planner.register_agent(self.geometry_agent)
        self.task_planner.register_agent(self.sketch_agent)
        self.task_planner.register_agent(self.analysis_agent)

        # Framework state
        self.is_initialized = True
        self.execution_history = []
        self.current_context = {}

        self.logger.info("AI Agent Framework initialized successfully")

    def execute_autonomous_task(
        self,
        description: str,
        context: Dict[str, Any] = None,
        preview_mode: bool = False,
    ) -> Dict[str, Any]:
        """
        Execute a complex task autonomously from natural language description.

        Args:
            description: Natural language task description
            context: Current FreeCAD context (document, selection, etc.)
            preview_mode: If True, don't actually execute, just plan

        Returns:
            Execution results with status, created objects, and details
        """
        self.logger.info(f"Executing autonomous task: {description}")

        # Update current context
        if context:
            self.current_context.update(context)
        else:
            # Get current FreeCAD context if not provided
            context = self._get_current_freecad_context()
            self.current_context = context

        try:
            # Create execution plan
            plan = self.task_planner.parse_natural_language_request(
                description, context
            )

            if preview_mode:
                return self._create_preview_result(plan, description)

            # Execute the plan
            task_results = self.task_planner.execute_plan(plan)

            # Compile overall result
            result = self._compile_execution_result(plan, task_results, description)

            # Record in history
            self.execution_history.append(
                {
                    "timestamp": datetime.now(),
                    "description": description,
                    "plan_id": plan.id,
                    "status": result["status"],
                    "task_count": len(plan.tasks),
                }
            )

            return result

        except Exception as e:
            self.logger.error(f"Autonomous task execution failed: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "description": description,
                "timestamp": datetime.now().isoformat(),
            }

    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get comprehensive overview of framework capabilities.

        Returns:
            Dictionary describing all available capabilities
        """
        agent_capabilities = self.task_planner.get_agent_capabilities()

        # Compile supported operations
        supported_operations = {
            "geometry_operations": [
                "create_box",
                "create_cylinder",
                "create_sphere",
                "create_cone",
                "create_torus",
                "boolean_union",
                "boolean_difference",
                "boolean_intersection",
                "add_fillet",
                "add_chamfer",
                "mirror_object",
                "array_linear",
                "array_polar",
                "scale_object",
                "rotate_object",
                "translate_object",
            ],
            "sketch_operations": [
                "create_sketch",
                "add_line",
                "add_rectangle",
                "add_circle",
                "add_arc",
                "add_point",
                "add_constraint_horizontal",
                "add_constraint_vertical",
                "add_constraint_parallel",
                "add_constraint_perpendicular",
                "add_constraint_equal",
                "add_constraint_coincident",
                "add_constraint_distance",
                "add_constraint_radius",
                "add_constraint_angle",
                "close_sketch",
                "fully_constrain",
            ],
            "analysis_operations": [
                "geometric_properties",
                "mass_properties",
                "mesh_analysis",
                "printability_analysis",
                "structural_analysis",
                "validate_geometry",
                "check_intersections",
                "measure_distance",
                "measure_angle",
                "surface_area_analysis",
                "volume_analysis",
                "cross_section_analysis",
                "draft_angle_analysis",
                "undercut_analysis",
                "wall_thickness_analysis",
            ],
        }

        # Common task patterns
        common_patterns = [
            "Create a {dimensions} box/cube",
            "Create a cylinder with radius {value} and height {value}",
            "Add {size} fillet/chamfer to selected object",
            "Analyze this part for 3D printing",
            "Create a sketch with rectangle/circle",
            "Perform boolean union/difference on selected objects",
            "Measure distance between points/objects",
            "Validate geometry for manufacturing",
        ]

        return {
            "agent_capabilities": agent_capabilities,
            "supported_operations": supported_operations,
            "common_patterns": common_patterns,
            "natural_language_examples": [
                "Create a 10x20x30mm box",
                "Add 2mm fillets to all edges",
                "Analyze this bracket for 3D printing",
                "Create a sketch with a 50mm circle",
                "Boolean union the selected objects",
                "Measure the distance between these points",
            ],
            "framework_info": {
                "version": "1.0.0",
                "agents_count": len(self.task_planner.agents),
                "is_initialized": self.is_initialized,
                "freecad_available": App is not None,
            },
        }

    def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get history of executed tasks"""
        return self.execution_history.copy()

    def get_current_context(self) -> Dict[str, Any]:
        """Get current FreeCAD context"""
        return self._get_current_freecad_context()

    def validate_request(self, description: str) -> Dict[str, Any]:
        """
        Validate if a request can be handled by the framework.

        Args:
            description: Natural language task description

        Returns:
            Validation result with feasibility assessment
        """
        try:
            # Try to parse the request
            context = self._get_current_freecad_context()
            plan = self.task_planner.parse_natural_language_request(
                description, context
            )

            # Check if agents can handle all tasks
            unhandleable_tasks = []
            for task in plan.tasks:
                suitable_agents = [
                    agent
                    for agent in self.task_planner.agents.values()
                    if agent.can_handle_task(task)
                ]
                if not suitable_agents:
                    unhandleable_tasks.append(task)

            if unhandleable_tasks:
                return {
                    "feasible": False,
                    "reason": "Some tasks cannot be handled by available agents",
                    "unhandleable_tasks": [
                        {"type": task.task_type.value, "description": task.description}
                        for task in unhandleable_tasks
                    ],
                    "task_count": len(plan.tasks),
                }

            return {
                "feasible": True,
                "task_count": len(plan.tasks),
                "estimated_duration": len(plan.tasks) * 2,  # Rough estimate
                "required_agents": list(
                    set(
                        agent.agent_type
                        for agent in self.task_planner.agents.values()
                        for task in plan.tasks
                        if agent.can_handle_task(task)
                    )
                ),
                "plan_preview": [
                    {
                        "task_type": task.task_type.value,
                        "description": task.description,
                        "parameters": task.parameters,
                    }
                    for task in plan.tasks
                ],
            }

        except Exception as e:
            return {
                "feasible": False,
                "reason": f"Request parsing failed: {str(e)}",
                "error": str(e),
            }

    def get_plan_status(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Get status of execution plan"""
        plan = self.task_planner.get_plan_status(plan_id)
        if not plan:
            return None

        return {
            "plan_id": plan.id,
            "description": plan.description,
            "status": plan.status.value,
            "task_count": len(plan.tasks),
            "created_at": plan.created_at.isoformat(),
            "started_at": plan.started_at.isoformat() if plan.started_at else None,
            "completed_at": (
                plan.completed_at.isoformat() if plan.completed_at else None
            ),
            "error_message": plan.error_message,
        }

    def cancel_execution(self, plan_id: str) -> bool:
        """Cancel active execution plan"""
        return self.task_planner.cancel_plan(plan_id)

    def _get_current_freecad_context(self) -> Dict[str, Any]:
        """Extract current FreeCAD context"""
        context = {
            "timestamp": datetime.now().isoformat(),
            "freecad_available": App is not None,
        }

        if App is None:
            return context

        # Document information
        if App.ActiveDocument:
            doc = App.ActiveDocument
            context["document"] = {
                "name": doc.Name,
                "object_count": len(doc.Objects),
                "objects": [obj.Name for obj in doc.Objects[:10]],  # Limit to first 10
            }

            # Selected objects
            if Gui:
                selection = Gui.Selection.getSelection()
                context["selected_objects"] = [obj.Name for obj in selection]

                # Selected sub-elements
                selection_ex = Gui.Selection.getSelectionEx()
                if selection_ex:
                    context["selected_sub_elements"] = [
                        {"object": sel.Object.Name, "sub_names": sel.SubElementNames}
                        for sel in selection_ex
                    ]

            # Current workbench
            if Gui:
                context["active_workbench"] = Gui.activeWorkbench().name()
        else:
            context["document"] = None
            context["selected_objects"] = []

        return context

    def _create_preview_result(
        self, plan: ExecutionPlan, description: str
    ) -> Dict[str, Any]:
        """Create preview result without execution"""
        return {
            "status": "preview",
            "description": description,
            "plan_id": plan.id,
            "task_count": len(plan.tasks),
            "tasks_preview": [
                {
                    "task_type": task.task_type.value,
                    "description": task.description,
                    "parameters": task.parameters,
                    "estimated_agent": self._get_task_agent_type(task),
                }
                for task in plan.tasks
            ],
            "estimated_execution_time": len(plan.tasks) * 2,  # seconds
            "timestamp": datetime.now().isoformat(),
        }

    def _compile_execution_result(
        self, plan: ExecutionPlan, task_results: Dict[str, TaskResult], description: str
    ) -> Dict[str, Any]:
        """Compile overall execution result"""
        # Count successful and failed tasks
        successful_tasks = sum(
            1
            for result in task_results.values()
            if result.status == TaskStatus.COMPLETED
        )
        failed_tasks = len(task_results) - successful_tasks

        # Collect created and modified objects
        created_objects = []
        modified_objects = []

        for result in task_results.values():
            if result.created_objects:
                created_objects.extend(result.created_objects)
            if result.modified_objects:
                modified_objects.extend(result.modified_objects)

        # Determine overall status
        if failed_tasks == 0:
            status = "completed"
        elif successful_tasks > 0:
            status = "partial_success"
        else:
            status = "failed"

        # Compile detailed results
        detailed_results = []
        for task in plan.tasks:
            result = task_results.get(task.id)
            if result:
                detailed_results.append(
                    {
                        "task_id": task.id,
                        "task_type": task.task_type.value,
                        "description": task.description,
                        "status": result.status.value,
                        "execution_time": result.execution_time,
                        "error_message": result.error_message,
                        "created_objects": result.created_objects,
                        "modified_objects": result.modified_objects,
                    }
                )

        return {
            "status": status,
            "description": description,
            "plan_id": plan.id,
            "execution_summary": {
                "total_tasks": len(plan.tasks),
                "successful_tasks": successful_tasks,
                "failed_tasks": failed_tasks,
                "execution_time": (
                    (plan.completed_at - plan.started_at).total_seconds()
                    if plan.completed_at and plan.started_at
                    else 0
                ),
            },
            "created_objects": list(set(created_objects)),  # Remove duplicates
            "modified_objects": list(set(modified_objects)),
            "detailed_results": detailed_results,
            "timestamp": datetime.now().isoformat(),
        }

    def _get_task_agent_type(self, task: AgentTask) -> str:
        """Determine which agent would handle a task"""
        for agent in self.task_planner.agents.values():
            if agent.can_handle_task(task):
                return agent.agent_type
        return "unknown"

    def get_framework_status(self) -> Dict[str, Any]:
        """Get overall framework status"""
        return {
            "is_initialized": self.is_initialized,
            "freecad_available": App is not None,
            "agents": {
                agent_type: {
                    "name": agent.name,
                    "capabilities": [cap.value for cap in agent.get_capabilities()],
                    "current_task": (
                        agent.get_current_task().id
                        if agent.get_current_task()
                        else None
                    ),
                    "task_history_count": len(agent.get_task_history()),
                }
                for agent_type, agent in self.task_planner.agents.items()
            },
            "active_plans": len(self.task_planner.get_active_plans()),
            "completed_plans": len(self.task_planner.get_completed_plans()),
            "execution_history_count": len(self.execution_history),
            "current_context": self.current_context,
        }

    def shutdown(self):
        """Shutdown the agent framework"""
        self.logger.info("Shutting down AI Agent Framework")

        # Cancel any active plans
        for plan_id in list(self.task_planner.get_active_plans().keys()):
            self.task_planner.cancel_plan(plan_id)

        self.is_initialized = False
        self.logger.info("AI Agent Framework shutdown complete")
