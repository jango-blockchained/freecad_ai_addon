"""
Sketch Agent for FreeCAD AI Addon.
Handles sketch creation and modification operations.
"""

from typing import Dict, Any
import logging

try:
    import FreeCAD as App
    import Part
    import Sketcher
except ImportError:
    # Mock for testing outside FreeCAD
    App = None
    Part = None
    Sketcher = None

from .base_agent import BaseAgent, AgentTask, TaskResult, TaskStatus, TaskType
from .sketch_action_library import SketchActionLibrary

logger = logging.getLogger(__name__)


class SketchAgent(BaseAgent):
    """
    Specialized agent for sketch operations in FreeCAD.

    Handles creation and modification of 2D sketches including
    geometric elements and constraints.
    """

    def __init__(self):
        super().__init__("SketchAgent", "sketch")
        self.description = (
            "Specialized agent for 2D sketch creation and constraint management"
        )

        # This agent handles sketch creation and modification tasks
        self.capabilities = [
            TaskType.SKETCH_CREATION,
            TaskType.SKETCH_MODIFICATION,
        ]

        # Initialize sketch action library
        self.sketch_action_library = SketchActionLibrary()

        # Initialize decision engine (will be set by agent framework)
        self.decision_engine = None

        # Register supported operations
        self.supported_operations = {
            "create_sketch": self._create_sketch,
            "add_line": self._add_line,
            "add_rectangle": self._add_rectangle,
            "add_circle": self._add_circle,
            "add_arc": self._add_arc,
            # Constraints
            "add_constraint_horizontal": self._add_constraint_horizontal,
            "add_constraint_vertical": self._add_constraint_vertical,
            "add_constraint_parallel": self._add_constraint_parallel,
            "add_constraint_perpendicular": self._add_constraint_perpendicular
            if hasattr(self, "_add_constraint_perpendicular")
            else (lambda p: {"modified_objects": [p.get("sketch", "Sketch")]}),
            "add_constraint_equal": self._add_constraint_equal
            if hasattr(self, "_add_constraint_equal")
            else (lambda p: {"modified_objects": [p.get("sketch", "Sketch")]}),
            "add_constraint_coincident": self._add_constraint_coincident
            if hasattr(self, "_add_constraint_coincident")
            else (lambda p: {"modified_objects": [p.get("sketch", "Sketch")]}),
            "add_constraint_distance": self._add_constraint_distance
            if hasattr(self, "_add_constraint_distance")
            else (lambda p: {"modified_objects": [p.get("sketch", "Sketch")]}),
            "add_constraint_radius": self._add_constraint_radius
            if hasattr(self, "_add_constraint_radius")
            else (lambda p: {"modified_objects": [p.get("sketch", "Sketch")]}),
            "add_constraint_angle": self._add_constraint_angle
            if hasattr(self, "_add_constraint_angle")
            else (lambda p: {"modified_objects": [p.get("sketch", "Sketch")]}),
        }

        # Constraint type mapping
        self.constraint_types = {
            "horizontal": Sketcher.Constraint if Sketcher else None,
            "vertical": Sketcher.Constraint if Sketcher else None,
            "parallel": Sketcher.Constraint if Sketcher else None,
            "perpendicular": Sketcher.Constraint if Sketcher else None,
            "equal": Sketcher.Constraint if Sketcher else None,
            "coincident": Sketcher.Constraint if Sketcher else None,
            "distance": Sketcher.Constraint if Sketcher else None,
            "radius": Sketcher.Constraint if Sketcher else None,
            "angle": Sketcher.Constraint if Sketcher else None,
        }

    def can_handle_task(self, task: AgentTask) -> bool:
        """Check if this agent can handle the given task."""
        if task.task_type not in self.capabilities:
            return False

        operation = task.parameters.get("operation")
        return operation in self.supported_operations

    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validate task parameters."""
        operation = parameters.get("operation")
        if not operation:
            return False

        if operation not in self.supported_operations:
            return False

        # Validate operation-specific parameters
        if operation == "create_sketch":
            return "plane" in parameters

        elif operation == "add_line":
            required = ["sketch", "start_point", "end_point"]
            return all(param in parameters for param in required)

        elif operation == "add_rectangle":
            required = ["sketch", "corner1", "corner2"]
            return all(param in parameters for param in required)

        elif operation == "add_circle":
            required = ["sketch", "center", "radius"]
            return all(param in parameters for param in required)

        elif operation == "add_arc":
            required = ["sketch", "center", "start_point", "end_point"]
            return all(param in parameters for param in required)

        elif operation.startswith("add_constraint"):
            return "sketch" in parameters

        return True

    def execute_task(self, task: AgentTask) -> TaskResult:
        """Execute the sketch task."""
        operation = task.parameters.get("operation")
        operation_func = self.supported_operations.get(operation)

        if not operation_func:
            return TaskResult(
                status=TaskStatus.FAILED,
                error_message=f"Unsupported operation: {operation}",
            )

        try:
            result = operation_func(task.parameters)
            return TaskResult(
                status=TaskStatus.COMPLETED,
                result_data=result,
                created_objects=result.get("created_objects", []),
                modified_objects=result.get("modified_objects", []),
            )
        except Exception as e:
            return TaskResult(
                status=TaskStatus.FAILED,
                error_message=f"Operation {operation} failed: {str(e)}",
            )

    def _create_sketch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new sketch on specified plane."""
        plane = params["plane"]  # 'XY', 'XZ', 'YZ', or custom
        name = params.get("name", "Sketch")

        doc = App.ActiveDocument
        sketch = doc.addObject("Sketcher::SketchObject", name)

        # Set sketch plane
        if plane == "XY":
            sketch.Support = []
            sketch.MapMode = "FlatFace"
        elif plane == "XZ":
            sketch.Support = []
            sketch.MapMode = "FlatFace"
            sketch.Placement.Rotation = App.Rotation(App.Vector(1, 0, 0), 90)
        elif plane == "YZ":
            sketch.Support = []
            sketch.MapMode = "FlatFace"
            sketch.Placement.Rotation = App.Rotation(App.Vector(0, 1, 0), 90)

        return {
            "created_objects": [sketch.Name],
            "sketch": sketch,
            "plane": plane,
            "degrees_of_freedom": sketch.solve(),
        }

    def _add_line(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add line to sketch."""
        sketch_name = params["sketch"]
        start_point = params["start_point"]  # [x, y]
        end_point = params["end_point"]  # [x, y]
        construction = params.get("construction", False)

        doc = App.ActiveDocument
        sketch = doc.getObject(sketch_name)
        if not sketch:
            raise ValueError(f"Sketch {sketch_name} not found")

        # Add line geometry
        line_id = sketch.addGeometry(
            Part.LineSegment(
                App.Vector(start_point[0], start_point[1], 0),
                App.Vector(end_point[0], end_point[1], 0),
            ),
            construction,
        )

        return {
            "modified_objects": [sketch_name],
            "geometry_id": line_id,
            "start_point": start_point,
            "end_point": end_point,
            "construction": construction,
            "degrees_of_freedom": sketch.solve(),
        }

    def _add_rectangle(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add rectangle to sketch."""
        sketch_name = params["sketch"]
        corner1 = params["corner1"]  # [x, y]
        corner2 = params["corner2"]  # [x, y]
        construction = params.get("construction", False)

        doc = App.ActiveDocument
        sketch = doc.getObject(sketch_name)
        if not sketch:
            raise ValueError(f"Sketch {sketch_name} not found")

        # Calculate rectangle corners
        x1, y1 = corner1
        x2, y2 = corner2

        # Add four lines for rectangle
        line_ids = []

        # Bottom line
        line_ids.append(
            sketch.addGeometry(
                Part.LineSegment(App.Vector(x1, y1, 0), App.Vector(x2, y1, 0)),
                construction,
            )
        )

        # Right line
        line_ids.append(
            sketch.addGeometry(
                Part.LineSegment(App.Vector(x2, y1, 0), App.Vector(x2, y2, 0)),
                construction,
            )
        )

        # Top line
        line_ids.append(
            sketch.addGeometry(
                Part.LineSegment(App.Vector(x2, y2, 0), App.Vector(x1, y2, 0)),
                construction,
            )
        )

        # Left line
        line_ids.append(
            sketch.addGeometry(
                Part.LineSegment(App.Vector(x1, y2, 0), App.Vector(x1, y1, 0)),
                construction,
            )
        )

        # Add coincident constraints for corners
        sketch.addConstraint(
            Sketcher.Constraint("Coincident", line_ids[0], 2, line_ids[1], 1)
        )
        sketch.addConstraint(
            Sketcher.Constraint("Coincident", line_ids[1], 2, line_ids[2], 1)
        )
        sketch.addConstraint(
            Sketcher.Constraint("Coincident", line_ids[2], 2, line_ids[3], 1)
        )
        sketch.addConstraint(
            Sketcher.Constraint("Coincident", line_ids[3], 2, line_ids[0], 1)
        )

        # Add horizontal and vertical constraints
        sketch.addConstraint(Sketcher.Constraint("Horizontal", line_ids[0]))
        sketch.addConstraint(Sketcher.Constraint("Horizontal", line_ids[2]))
        sketch.addConstraint(Sketcher.Constraint("Vertical", line_ids[1]))
        sketch.addConstraint(Sketcher.Constraint("Vertical", line_ids[3]))

        return {
            "modified_objects": [sketch_name],
            "geometry_ids": line_ids,
            "corner1": corner1,
            "corner2": corner2,
            "width": abs(x2 - x1),
            "height": abs(y2 - y1),
            "degrees_of_freedom": sketch.solve(),
        }

    def _add_circle(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add circle to sketch."""
        sketch_name = params["sketch"]
        center = params["center"]  # [x, y]
        radius = params["radius"]
        construction = params.get("construction", False)

        doc = App.ActiveDocument
        sketch = doc.getObject(sketch_name)
        if not sketch:
            raise ValueError(f"Sketch {sketch_name} not found")

        # Add circle geometry
        circle_id = sketch.addGeometry(
            Part.Circle(
                App.Vector(center[0], center[1], 0), App.Vector(0, 0, 1), radius
            ),
            construction,
        )

        return {
            "modified_objects": [sketch_name],
            "geometry_id": circle_id,
            "center": center,
            "radius": radius,
            "construction": construction,
            "degrees_of_freedom": sketch.solve(),
        }

    def _add_arc(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add arc to sketch."""
        sketch_name = params["sketch"]
        center = params["center"]  # [x, y]
        start_point = params["start_point"]  # [x, y]
        end_point = params["end_point"]  # [x, y]
        construction = params.get("construction", False)

        doc = App.ActiveDocument
        sketch = doc.getObject(sketch_name)
        if not sketch:
            raise ValueError(f"Sketch {sketch_name} not found")

        # Create arc from three points
        arc_id = sketch.addGeometry(
            Part.ArcOfCircle(
                Part.Circle(
                    App.Vector(center[0], center[1], 0),
                    App.Vector(0, 0, 1),
                    1.0,  # Radius will be constrained
                ),
                0,  # Start angle
                1.57,  # End angle (will be adjusted)
            ),
            construction,
        )

        return {
            "modified_objects": [sketch_name],
            "geometry_id": arc_id,
            "center": center,
            "start_point": start_point,
            "end_point": end_point,
            "construction": construction,
            "degrees_of_freedom": sketch.solve(),
        }

    def _add_point(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add point to sketch."""
        sketch_name = params["sketch"]
        position = params["position"]  # [x, y]
        construction = params.get("construction", True)  # Points usually construction

        doc = App.ActiveDocument
        sketch = doc.getObject(sketch_name)
        if not sketch:
            raise ValueError(f"Sketch {sketch_name} not found")

        # Add point geometry
        point_id = sketch.addGeometry(
            Part.Point(App.Vector(position[0], position[1], 0)), construction
        )

        return {
            "modified_objects": [sketch_name],
            "geometry_id": point_id,
            "position": position,
            "construction": construction,
            "degrees_of_freedom": sketch.solve(),
        }

    def _add_constraint_horizontal(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add horizontal constraint to line."""
        sketch_name = params["sketch"]
        geometry_id = params["geometry_id"]

        doc = App.ActiveDocument
        sketch = doc.getObject(sketch_name)
        if not sketch:
            raise ValueError(f"Sketch {sketch_name} not found")

        constraint_id = sketch.addConstraint(
            Sketcher.Constraint("Horizontal", geometry_id)
        )

        return {
            "modified_objects": [sketch_name],
            "constraint_id": constraint_id,
            "constraint_type": "horizontal",
            "geometry_id": geometry_id,
            "degrees_of_freedom": sketch.solve(),
        }

    def _add_constraint_vertical(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add vertical constraint to line."""
        sketch_name = params["sketch"]
        geometry_id = params["geometry_id"]

        doc = App.ActiveDocument
        sketch = doc.getObject(sketch_name)
        if not sketch:
            raise ValueError(f"Sketch {sketch_name} not found")

        constraint_id = sketch.addConstraint(
            Sketcher.Constraint("Vertical", geometry_id)
        )

        return {
            "modified_objects": [sketch_name],
            "constraint_id": constraint_id,
            "constraint_type": "vertical",
            "geometry_id": geometry_id,
            "degrees_of_freedom": sketch.solve(),
        }

    def _add_constraint_parallel(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add parallel constraint between two lines."""
        sketch_name = params["sketch"]
        geometry_id1 = params["geometry_id1"]
        geometry_id2 = params["geometry_id2"]

        doc = App.ActiveDocument
        sketch = doc.getObject(sketch_name)
        if not sketch:
            raise ValueError(f"Sketch {sketch_name} not found")

        constraint_id = sketch.addConstraint(
            Sketcher.Constraint("Parallel", geometry_id1, geometry_id2)
        )

        return {
            "modified_objects": [sketch_name],
            "constraint_id": constraint_id,
            "constraint_type": "parallel",
            "geometry_ids": [geometry_id1, geometry_id2],
            "degrees_of_freedom": sketch.solve(),
        }

    def _add_constraint_perpendicular(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add perpendicular constraint between two lines."""
        sketch_name = params["sketch"]
        geometry_id1 = params["geometry_id1"]
        geometry_id2 = params["geometry_id2"]

        doc = App.ActiveDocument
        sketch = doc.getObject(sketch_name)
        if not sketch:
            raise ValueError(f"Sketch {sketch_name} not found")

        constraint_id = sketch.addConstraint(
            Sketcher.Constraint("Perpendicular", geometry_id1, geometry_id2)
        )

        return {
            "modified_objects": [sketch_name],
            "constraint_id": constraint_id,
            "constraint_type": "perpendicular",
            "geometry_ids": [geometry_id1, geometry_id2],
            "degrees_of_freedom": sketch.solve(),
        }

    def _add_constraint_equal(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add equal constraint between two geometries."""
        sketch_name = params["sketch"]
        geometry_id1 = params["geometry_id1"]
        geometry_id2 = params["geometry_id2"]

        doc = App.ActiveDocument
        sketch = doc.getObject(sketch_name)
        if not sketch:
            raise ValueError(f"Sketch {sketch_name} not found")

        constraint_id = sketch.addConstraint(
            Sketcher.Constraint("Equal", geometry_id1, geometry_id2)
        )

        return {
            "modified_objects": [sketch_name],
            "constraint_id": constraint_id,
            "constraint_type": "equal",
            "geometry_ids": [geometry_id1, geometry_id2],
            "degrees_of_freedom": sketch.solve(),
        }

    def _add_constraint_coincident(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add coincident constraint between two points."""
        sketch_name = params["sketch"]
        geometry_id1 = params["geometry_id1"]
        point_pos1 = params["point_pos1"]  # 1 or 2 (start/end point)
        geometry_id2 = params["geometry_id2"]
        point_pos2 = params["point_pos2"]

        doc = App.ActiveDocument
        sketch = doc.getObject(sketch_name)
        if not sketch:
            raise ValueError(f"Sketch {sketch_name} not found")

        constraint_id = sketch.addConstraint(
            Sketcher.Constraint(
                "Coincident", geometry_id1, point_pos1, geometry_id2, point_pos2
            )
        )

        return {
            "modified_objects": [sketch_name],
            "constraint_id": constraint_id,
            "constraint_type": "coincident",
            "geometry_ids": [geometry_id1, geometry_id2],
            "point_positions": [point_pos1, point_pos2],
            "degrees_of_freedom": sketch.solve(),
        }

    def _add_constraint_distance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add distance constraint."""
        sketch_name = params["sketch"]
        geometry_id1 = params["geometry_id1"]
        geometry_id2 = params.get("geometry_id2")
        distance = params["distance"]
        point_pos1 = params.get("point_pos1", 1)
        point_pos2 = params.get("point_pos2", 1)

        doc = App.ActiveDocument
        sketch = doc.getObject(sketch_name)
        if not sketch:
            raise ValueError(f"Sketch {sketch_name} not found")

        if geometry_id2 is not None:
            # Distance between two geometries
            constraint_id = sketch.addConstraint(
                Sketcher.Constraint(
                    "Distance",
                    geometry_id1,
                    point_pos1,
                    geometry_id2,
                    point_pos2,
                    distance,
                )
            )
        else:
            # Distance/length of single geometry
            constraint_id = sketch.addConstraint(
                Sketcher.Constraint("Distance", geometry_id1, distance)
            )

        return {
            "modified_objects": [sketch_name],
            "constraint_id": constraint_id,
            "constraint_type": "distance",
            "distance": distance,
            "geometry_ids": [geometry_id1] + ([geometry_id2] if geometry_id2 else []),
            "degrees_of_freedom": sketch.solve(),
        }

    def _add_constraint_radius(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add radius constraint to circle or arc."""
        sketch_name = params["sketch"]
        geometry_id = params["geometry_id"]
        radius = params["radius"]

        doc = App.ActiveDocument
        sketch = doc.getObject(sketch_name)
        if not sketch:
            raise ValueError(f"Sketch {sketch_name} not found")

        constraint_id = sketch.addConstraint(
            Sketcher.Constraint("Radius", geometry_id, radius)
        )

        return {
            "modified_objects": [sketch_name],
            "constraint_id": constraint_id,
            "constraint_type": "radius",
            "radius": radius,
            "geometry_id": geometry_id,
            "degrees_of_freedom": sketch.solve(),
        }

    def _add_constraint_angle(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add angle constraint between two lines."""
        sketch_name = params["sketch"]
        geometry_id1 = params["geometry_id1"]
        geometry_id2 = params["geometry_id2"]
        angle = params["angle"]  # In degrees

        doc = App.ActiveDocument
        sketch = doc.getObject(sketch_name)
        if not sketch:
            raise ValueError(f"Sketch {sketch_name} not found")

        constraint_id = sketch.addConstraint(
            Sketcher.Constraint("Angle", geometry_id1, geometry_id2, angle)
        )

        return {
            "modified_objects": [sketch_name],
            "constraint_id": constraint_id,
            "constraint_type": "angle",
            "angle": angle,
            "geometry_ids": [geometry_id1, geometry_id2],
            "degrees_of_freedom": sketch.solve(),
        }

    def _close_sketch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Close and exit sketch editing."""
        sketch_name = params["sketch"]

        doc = App.ActiveDocument
        sketch = doc.getObject(sketch_name)
        if not sketch:
            raise ValueError(f"Sketch {sketch_name} not found")

        # Recompute the sketch
        sketch.recompute()
        doc.recompute()

        return {
            "modified_objects": [sketch_name],
            "sketch_closed": True,
            "final_degrees_of_freedom": sketch.solve(),
            "constraint_count": len(sketch.Constraints),
            "geometry_count": len(sketch.Geometry),
        }

    def _fully_constrain_sketch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt to fully constrain the sketch automatically."""
        sketch_name = params["sketch"]

        doc = App.ActiveDocument
        sketch = doc.getObject(sketch_name)
        if not sketch:
            raise ValueError(f"Sketch {sketch_name} not found")

        initial_dof = sketch.solve()

        # Attempt automatic constraints
        # This is a simplified version - real implementation would be more complex

        # Fix first point to origin if no fixed points exist
        if initial_dof > 0:
            # Look for a suitable point to fix
            for i, geom in enumerate(sketch.Geometry):
                if hasattr(geom, "StartPoint"):
                    # Add constraint to fix point to origin
                    sketch.addConstraint(Sketcher.Constraint("Coincident", i, 1, -1, 1))
                    break

        final_dof = sketch.solve()

        return {
            "modified_objects": [sketch_name],
            "initial_dof": initial_dof,
            "final_dof": final_dof,
            "fully_constrained": final_dof == 0,
            "constraint_count": len(sketch.Constraints),
        }
