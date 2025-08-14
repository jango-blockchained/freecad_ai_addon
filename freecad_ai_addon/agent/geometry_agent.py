"""
Geometry Agent for FreeCAD AI Addon.
Handles geometric operations like creating and modifying 3D objects.
"""

from typing import Dict, Any, List
import logging

try:
    import FreeCAD as App
    import Part
    import Draft
    import PartDesign  # Optional, used when available
except ImportError:
    # Mock for testing outside FreeCAD
    App = None
    Part = None
    Draft = None
    PartDesign = None

from .base_agent import BaseAgent, AgentTask, TaskResult, TaskStatus, TaskType
from .action_library import ActionLibrary

logger = logging.getLogger(__name__)


class GeometryAgent(BaseAgent):
    """
    Specialized agent for geometric operations in FreeCAD.

    Handles creation and modification of 3D geometric objects
    including primitives, boolean operations, and transformations.
    """

    def __init__(self):
        super().__init__("GeometryAgent", "geometry")
        self.description = (
            "Specialized agent for 3D geometric operations and part design"
        )

        # This agent handles geometry creation and modification tasks
        self.capabilities = [
            TaskType.GEOMETRY_CREATION,
            TaskType.GEOMETRY_MODIFICATION,
        ]

        # Initialize action library
        self.action_library = ActionLibrary()

        # Initialize decision engine (will be set by agent framework)
        self.decision_engine = None

        # Register supported operations
        self.supported_operations = {
            "create_box": self._create_box,
            "create_cylinder": self._create_cylinder,
            "create_sphere": self._create_sphere,
            "create_cone": self._create_cone,
            "create_torus": self._create_torus,
            # Feature / sketch based creations
            "extrude_from_sketch": self._extrude_from_sketch,
            "pocket_from_sketch": self._pocket_from_sketch,
            "loft_profiles": self._loft_profiles,
            "sweep_profile": self._sweep_profile,
            "boolean_union": self._boolean_union,
            "boolean_difference": self._boolean_difference,
            "boolean_intersection": self._boolean_intersection,
            "add_fillet": self._add_fillet,
            "add_chamfer": self._add_chamfer,
            # Transformations and arrays
            "mirror_object": self._mirror_object,
            "array_linear": self._array_linear,
            "array_polar": self._array_polar,
            "scale_object": self._scale_object,
            "rotate_object": self._rotate_object,
            "translate_object": self._translate_object,
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
        if operation == "create_box":
            required = ["length", "width", "height"]
            if not all(param in parameters for param in required):
                return False
            # Dimensions must be positive
            return all(
                isinstance(parameters[p], (int, float)) and parameters[p] > 0
                for p in required
            )

        elif operation == "create_cylinder":
            required = ["radius", "height"]
            if not all(param in parameters for param in required):
                return False
            return all(
                isinstance(parameters[p], (int, float)) and parameters[p] > 0
                for p in required
            )

        elif operation == "create_sphere":
            return (
                "radius" in parameters
                and isinstance(parameters["radius"], (int, float))
                and parameters["radius"] > 0
            )

        elif operation in [
            "boolean_union",
            "boolean_difference",
            "boolean_intersection",
        ]:
            # boolean_difference uses base_object + tool_objects; others use objects list
            if operation == "boolean_difference":
                return (
                    "base_object" in parameters
                    and "tool_objects" in parameters
                    and isinstance(parameters["tool_objects"], list)
                    and len(parameters["tool_objects"]) >= 1
                )
            return (
                "objects" in parameters
                and isinstance(parameters["objects"], list)
                and len(parameters["objects"]) >= 2
            )

        elif operation in ["add_fillet", "add_chamfer"]:
            return (
                "object" in parameters
                and "radius" in parameters
                and isinstance(parameters["radius"], (int, float))
                and parameters["radius"] > 0
            )

        elif operation == "mirror_object":
            return "object" in parameters and "plane" in parameters

        elif operation == "array_linear":
            return (
                "object" in parameters
                and "direction" in parameters
                and "count" in parameters
                and "spacing" in parameters
            )

        elif operation == "array_polar":
            return (
                "object" in parameters
                and "count" in parameters
                and isinstance(parameters["count"], int)
                and parameters["count"] >= 2
            )

        elif operation == "scale_object":
            return "object" in parameters and (
                "scale_factor" in parameters or "scale_vector" in parameters
            )

        elif operation == "rotate_object":
            return "object" in parameters and "angle" in parameters

        elif operation == "translate_object":
            return "object" in parameters and "translation" in parameters

        elif operation == "extrude_from_sketch":
            return (
                "sketch" in parameters
                and "length" in parameters
                and isinstance(parameters.get("length"), (int, float))
            )

        elif operation == "pocket_from_sketch":
            return (
                "sketch" in parameters
                and "depth" in parameters
                and isinstance(parameters.get("depth"), (int, float))
            )

        elif operation == "loft_profiles":
            return (
                isinstance(parameters.get("profiles"), list)
                and len(parameters.get("profiles", [])) >= 2
            )

        elif operation == "sweep_profile":
            return "profile" in parameters and "path" in parameters

        # Add more validation as needed
        return True

    def make_intelligent_decision(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use decision engine to make intelligent design decisions

        Args:
            request: Design request with geometry info and context

        Returns:
            Decision result with recommendations and execution plan
        """
        if self.decision_engine:
            return self.decision_engine.make_design_decision(request)
        else:
            # Fallback when decision engine not available
            return {
                "success": False,
                "error": "Decision engine not initialized",
                "recommendations": ["Manual design decisions required"],
            }

    def handle_operation_error(
        self, operation: str, error: Exception, context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Handle operation errors using intelligent recovery

        Args:
            operation: Name of the failed operation
            error: Exception that occurred
            context: Operation context

        Returns:
            List of recovery strategies
        """
        if self.decision_engine:
            return self.decision_engine.handle_operation_error(
                operation, error, context
            )
        else:
            # Fallback recovery strategies
            return [
                {
                    "strategy": "retry_operation",
                    "description": "Retry the operation",
                    "success_probability": 0.3,
                }
            ]

    def execute_task(self, task: AgentTask) -> TaskResult:
        """Execute the geometric task."""
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

    def _create_box(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a box primitive."""
        length = params["length"]
        width = params["width"]
        height = params["height"]
        name = params.get("name", "Box")
        placement = params.get("placement", None)

        doc = App.ActiveDocument
        box = doc.addObject("Part::Box", name)
        box.Length = length
        box.Width = width
        box.Height = height

        if placement:
            box.Placement = placement

        return {
            "created_objects": [box.Name],
            "object": box,
            "volume": box.Shape.Volume,
            "bounding_box": {
                "length": box.Shape.BoundBox.XLength,
                "width": box.Shape.BoundBox.YLength,
                "height": box.Shape.BoundBox.ZLength,
            },
        }

    def _create_cylinder(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a cylinder primitive."""
        radius = params["radius"]
        height = params["height"]
        name = params.get("name", "Cylinder")
        angle = params.get("angle", 360)  # Full cylinder by default
        placement = params.get("placement", None)

        doc = App.ActiveDocument
        cylinder = doc.addObject("Part::Cylinder", name)
        cylinder.Radius = radius
        cylinder.Height = height
        cylinder.Angle = angle

        if placement:
            cylinder.Placement = placement

        return {
            "created_objects": [cylinder.Name],
            "object": cylinder,
            "volume": cylinder.Shape.Volume,
            "surface_area": cylinder.Shape.Area,
        }

    def _create_sphere(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a sphere primitive."""
        radius = params["radius"]
        name = params.get("name", "Sphere")
        angle1 = params.get("angle1", -90)  # Start angle
        angle2 = params.get("angle2", 90)  # End angle
        angle3 = params.get("angle3", 360)  # Full rotation by default
        placement = params.get("placement", None)

        doc = App.ActiveDocument
        sphere = doc.addObject("Part::Sphere", name)
        sphere.Radius = radius
        sphere.Angle1 = angle1
        sphere.Angle2 = angle2
        sphere.Angle3 = angle3

        if placement:
            sphere.Placement = placement

        return {
            "created_objects": [sphere.Name],
            "object": sphere,
            "volume": sphere.Shape.Volume,
            "surface_area": sphere.Shape.Area,
        }

    def _create_cone(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a cone primitive."""
        radius1 = params["radius1"]  # Bottom radius
        radius2 = params.get("radius2", 0)  # Top radius (0 for cone)
        height = params["height"]
        name = params.get("name", "Cone")
        angle = params.get("angle", 360)
        placement = params.get("placement", None)

        doc = App.ActiveDocument
        cone = doc.addObject("Part::Cone", name)
        cone.Radius1 = radius1
        cone.Radius2 = radius2
        cone.Height = height
        cone.Angle = angle

        if placement:
            cone.Placement = placement

        return {
            "created_objects": [cone.Name],
            "object": cone,
            "volume": cone.Shape.Volume,
            "surface_area": cone.Shape.Area,
        }

    def _create_torus(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a torus primitive."""
        radius1 = params["radius1"]  # Major radius
        radius2 = params["radius2"]  # Minor radius
        name = params.get("name", "Torus")
        angle1 = params.get("angle1", 0)
        angle2 = params.get("angle2", 360)
        angle3 = params.get("angle3", 360)
        placement = params.get("placement", None)

        doc = App.ActiveDocument
        torus = doc.addObject("Part::Torus", name)
        torus.Radius1 = radius1
        torus.Radius2 = radius2
        torus.Angle1 = angle1
        torus.Angle2 = angle2
        torus.Angle3 = angle3

        if placement:
            torus.Placement = placement

        return {
            "created_objects": [torus.Name],
            "object": torus,
            "volume": torus.Shape.Volume,
            "surface_area": torus.Shape.Area,
        }

    def _boolean_union(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform boolean union operation."""
        objects = params["objects"]
        name = params.get("name", "Union")

        if len(objects) < 2:
            raise ValueError("Boolean union requires at least 2 objects")

        doc = App.ActiveDocument

        # Get object references
        obj_refs = []
        for obj_name in objects:
            obj = doc.getObject(obj_name)
            if not obj:
                raise ValueError(f"Object {obj_name} not found")
            obj_refs.append(obj)

        # Create boolean union
        union = doc.addObject("Part::MultiFuse", name)
        union.Shapes = obj_refs
        doc.recompute()

        # Safety guard: ensure resulting shape is valid and non-empty
        shape = getattr(union, "Shape", None)
        volume = getattr(shape, "Volume", None)
        if (
            shape is None
            or getattr(shape, "isNull", lambda: False)()
            or volume is None
            or volume <= 0
        ):
            # Attempt fallback: sequential fuse
            try:
                prev = obj_refs[0]
                for idx, nxt in enumerate(obj_refs[1:], start=1):
                    fuse = doc.addObject("Part::Fuse", f"{name}_seq{idx}")
                    fuse.Base = prev
                    fuse.Tool = nxt
                    doc.recompute()
                    if getattr(getattr(fuse, "Shape", None), "Volume", 0) <= 0:
                        raise ValueError("Sequential fuse produced empty shape")
                    prev = fuse
                union = prev
                volume = getattr(getattr(union, "Shape", None), "Volume", None)
            except Exception as e:
                raise ValueError(f"Boolean union failed to produce valid shape: {e}")

        return {
            "created_objects": [union.Name],
            "object": union,
            "input_objects": objects,
            "volume": volume,
        }

    def _boolean_difference(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform boolean difference operation."""
        base_object = params["base_object"]
        tool_objects = params["tool_objects"]
        name = params.get("name", "Difference")

        doc = App.ActiveDocument

        base = doc.getObject(base_object)
        if not base:
            raise ValueError(f"Base object {base_object} not found")

        # Chain cuts for multiple tools
        current = base
        for idx, tool_name in enumerate(tool_objects):
            tool = doc.getObject(tool_name)
            if not tool:
                raise ValueError(f"Tool object {tool_name} not found")
            stage_name = (
                name if idx == len(tool_objects) - 1 else f"{name}_stage{idx+1}"
            )
            cut = doc.addObject("Part::Cut", stage_name)
            cut.Base = current
            cut.Tool = tool
            current = cut

        doc.recompute()

        shape = getattr(current, "Shape", None)
        volume = getattr(shape, "Volume", None)
        if (
            shape is None
            or getattr(shape, "isNull", lambda: False)()
            or volume is None
            or volume <= 0
        ):
            raise ValueError("Boolean difference produced empty or invalid shape")

        return {
            "created_objects": [current.Name],
            "object": current,
            "base_object": base_object,
            "tool_objects": tool_objects,
            "volume": volume,
        }

    def _boolean_intersection(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform boolean intersection operation."""
        objects = params["objects"]
        name = params.get("name", "Intersection")

        if len(objects) < 2:
            raise ValueError("Boolean intersection requires at least 2 objects")

        doc = App.ActiveDocument

        # Get object references
        obj_refs = []
        for obj_name in objects:
            obj = doc.getObject(obj_name)
            if not obj:
                raise ValueError(f"Object {obj_name} not found")
            obj_refs.append(obj)

        # Create boolean intersection
        intersection = doc.addObject("Part::MultiCommon", name)
        intersection.Shapes = obj_refs
        doc.recompute()

        shape = getattr(intersection, "Shape", None)
        volume = getattr(shape, "Volume", None)
        if (
            shape is None
            or getattr(shape, "isNull", lambda: False)()
            or volume is None
            or volume <= 0
        ):
            raise ValueError("Boolean intersection produced empty or invalid shape")

        return {
            "created_objects": [intersection.Name],
            "object": intersection,
            "input_objects": objects,
            "volume": volume,
        }

    # -----------------------------------------------------------------
    # Advanced feature operations
    # -----------------------------------------------------------------

    def _extrude_from_sketch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Extrude (pad) a sketch by a given length.

        Falls back gracefully in headless/mock mode.
        """
        if not App or not App.ActiveDocument:
            raise RuntimeError("Extrude requires active FreeCAD document")

        sketch_name = params["sketch"]
        length = params.get("length", 10.0)
        taper = params.get("taper", 0.0)
        name = params.get("name", f"{sketch_name}_Extrude")

        doc = App.ActiveDocument
        sketch = doc.getObject(sketch_name)
        if not sketch:
            raise ValueError(f"Sketch {sketch_name} not found")

        # Prefer PartDesign Pad when available and sketch is suitable
        try:
            if PartDesign and sketch.TypeId.startswith("Sketcher::SketchObject"):
                pad = doc.addObject("PartDesign::Pad", name)
                pad.Profile = sketch
                pad.Length = length
                if hasattr(pad, "TaperAngle"):
                    pad.TaperAngle = taper
                doc.recompute()
                vol = getattr(getattr(pad, "Shape", None), "Volume", None)
                return {
                    "created_objects": [pad.Name],
                    "object": pad,
                    "sketch": sketch_name,
                    "length": length,
                    "taper": taper,
                    "volume": vol,
                }
        except Exception:
            # Fallback to Part extrusion
            pass

        # Generic Part extrusion
        extrude = doc.addObject("Part::Extrusion", name)
        extrude.Base = sketch
        extrude.Dir = (0, 0, length)
        extrude.Solid = True
        extrude.TaperAngle = taper if hasattr(extrude, "TaperAngle") else 0.0
        doc.recompute()
        vol = getattr(getattr(extrude, "Shape", None), "Volume", None)
        return {
            "created_objects": [extrude.Name],
            "object": extrude,
            "sketch": sketch_name,
            "length": length,
            "taper": taper,
            "volume": vol,
        }

    def _pocket_from_sketch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a pocket (cut) from a sketch into a base solid.

        Simplified implementation: extrudes sketch then performs boolean difference
        with provided base object.
        """
        if not App or not App.ActiveDocument:
            raise RuntimeError("Pocket requires active FreeCAD document")

        sketch_name = params["sketch"]
        depth = params.get("depth", 5.0)
        base_object = params.get("base_object")
        name = params.get("name", f"{sketch_name}_Pocket")

        if not base_object:
            raise ValueError("base_object parameter required for pocket")

        doc = App.ActiveDocument
        sketch = doc.getObject(sketch_name)
        base = doc.getObject(base_object)
        if not sketch:
            raise ValueError(f"Sketch {sketch_name} not found")
        if not base:
            raise ValueError(f"Base object {base_object} not found")

        # Create temporary extrusion of sketch for cut profile
        ext = doc.addObject("Part::Extrusion", f"{sketch_name}_PocketProfile")
        ext.Base = sketch
        ext.Dir = (0, 0, depth * -1.0)  # Negative direction by default
        ext.Solid = True
        doc.recompute()

        # Perform cut
        cut = doc.addObject("Part::Cut", name)
        cut.Base = base
        cut.Tool = ext
        doc.recompute()
        vol = getattr(getattr(cut, "Shape", None), "Volume", None)
        return {
            "created_objects": [cut.Name],
            "object": cut,
            "sketch": sketch_name,
            "base_object": base_object,
            "depth": depth,
            "volume": vol,
        }

    def _loft_profiles(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a loft through multiple profile sketches/wires."""
        if not App or not App.ActiveDocument:
            raise RuntimeError("Loft requires active FreeCAD document")

        profiles = params.get("profiles", [])
        solid = params.get("solid", True)
        ruled = params.get("ruled", False)
        closed = params.get("closed", False)
        name = params.get("name", "Loft")

        if len(profiles) < 2:
            raise ValueError("Loft requires at least two profiles")

        doc = App.ActiveDocument
        objs = []
        for p in profiles:
            o = doc.getObject(p)
            if not o:
                raise ValueError(f"Profile {p} not found")
            objs.append(o)

        loft = doc.addObject("Part::Loft", name)
        loft.Sections = objs
        loft.Solid = solid
        loft.Ruled = ruled
        loft.Closed = closed
        doc.recompute()
        vol = getattr(getattr(loft, "Shape", None), "Volume", None)
        return {
            "created_objects": [loft.Name],
            "object": loft,
            "profiles": profiles,
            "solid": solid,
            "ruled": ruled,
            "closed": closed,
            "volume": vol,
        }

    def _sweep_profile(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sweep a profile along a path."""
        if not App or not App.ActiveDocument:
            raise RuntimeError("Sweep requires active FreeCAD document")

        profile = params["profile"]
        path = params["path"]
        name = params.get("name", f"{profile}_Sweep")
        solid = params.get("solid", True)

        doc = App.ActiveDocument
        profile_obj = doc.getObject(profile)
        path_obj = doc.getObject(path)
        if not profile_obj:
            raise ValueError(f"Profile {profile} not found")
        if not path_obj:
            raise ValueError(f"Path {path} not found")

        sweep = doc.addObject("Part::Sweep", name)
        sweep.Sections = [profile_obj]
        sweep.Spine = path_obj
        sweep.Solid = solid
        doc.recompute()
        vol = getattr(getattr(sweep, "Shape", None), "Volume", None)
        return {
            "created_objects": [sweep.Name],
            "object": sweep,
            "profile": profile,
            "path": path,
            "solid": solid,
            "volume": vol,
        }

    def _add_fillet(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add fillet to object edges."""
        object_name = params["object"]
        radius = params["radius"]
        edges = params.get("edges", [])  # If empty, fillet all edges
        name = params.get("name", f"{object_name}_Fillet")

        doc = App.ActiveDocument
        obj = doc.getObject(object_name)
        if not obj:
            raise ValueError(f"Object {object_name} not found")

        fillet = doc.addObject("Part::Fillet", name)
        fillet.Base = obj

        if edges:
            # Fillet specific edges
            edge_list = [(edge_id, radius, radius) for edge_id in edges]
            fillet.Edges = edge_list
        else:
            # Fillet all edges
            edge_count = len(obj.Shape.Edges)
            edge_list = [(i + 1, radius, radius) for i in range(edge_count)]
            fillet.Edges = edge_list

        return {
            "created_objects": [fillet.Name],
            "modified_objects": [object_name],
            "object": fillet,
            "radius": radius,
            "edge_count": len(edge_list),
        }

    def _add_chamfer(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add chamfer to object edges."""
        object_name = params["object"]
        size = params["radius"]  # Using 'radius' parameter for chamfer size
        edges = params.get("edges", [])
        name = params.get("name", f"{object_name}_Chamfer")

        doc = App.ActiveDocument
        obj = doc.getObject(object_name)
        if not obj:
            raise ValueError(f"Object {object_name} not found")

        chamfer = doc.addObject("Part::Chamfer", name)
        chamfer.Base = obj

        if edges:
            # Chamfer specific edges
            edge_list = [(edge_id, size, size) for edge_id in edges]
            chamfer.Edges = edge_list
        else:
            # Chamfer all edges
            edge_count = len(obj.Shape.Edges)
            edge_list = [(i + 1, size, size) for i in range(edge_count)]
            chamfer.Edges = edge_list

        return {
            "created_objects": [chamfer.Name],
            "modified_objects": [object_name],
            "object": chamfer,
            "size": size,
            "edge_count": len(edge_list),
        }

    def _mirror_object(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Mirror object across a plane."""
        object_name = params["object"]
        mirror_plane = params.get("plane", "XY")  # XY, XZ, or YZ
        name = params.get("name", f"{object_name}_Mirror")

        doc = App.ActiveDocument
        obj = doc.getObject(object_name)
        if not obj:
            raise ValueError(f"Object {object_name} not found")

        mirror = doc.addObject("Part::Mirroring", name)
        mirror.Source = obj

        # Set mirror plane
        if mirror_plane == "XY":
            mirror.Normal = App.Vector(0, 0, 1)
        elif mirror_plane == "XZ":
            mirror.Normal = App.Vector(0, 1, 0)
        elif mirror_plane == "YZ":
            mirror.Normal = App.Vector(1, 0, 0)
        else:
            # Custom normal vector
            mirror.Normal = App.Vector(*mirror_plane)

        return {
            "created_objects": [mirror.Name],
            "object": mirror,
            "source_object": object_name,
            "mirror_plane": mirror_plane,
        }

    def _array_linear(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create linear array of object."""
        object_name = params["object"]
        direction = params["direction"]  # [x, y, z] vector
        count = params["count"]
        spacing = params["spacing"]
        name = params.get("name", f"{object_name}_LinearArray")

        doc = App.ActiveDocument
        obj = doc.getObject(object_name)
        if not obj:
            raise ValueError(f"Object {object_name} not found")

        # Use Draft workbench for array
        array = Draft.makeArray(
            obj, App.Vector(*direction) * spacing, App.Vector(0, 0, 0), count, 1, name
        )

        return {
            "created_objects": [array.Name],
            "object": array,
            "source_object": object_name,
            "count": count,
            "spacing": spacing,
            "direction": direction,
        }

    def _array_polar(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create polar array of object."""
        object_name = params["object"]
        center = params.get("center", [0, 0, 0])
        axis = params.get("axis", [0, 0, 1])
        count = params["count"]
        angle = params.get("angle", 360)  # Total angle for array
        name = params.get("name", f"{object_name}_PolarArray")

        doc = App.ActiveDocument
        obj = doc.getObject(object_name)
        if not obj:
            raise ValueError(f"Object {object_name} not found")

        # Use Draft workbench for polar array
        array = Draft.makeArray(
            obj, App.Vector(0, 0, 0), App.Vector(*axis), 1, count, name
        )

        # Set array properties
        array.ArrayType = "polar"
        array.NumberPolar = count
        array.AnglePolar = angle
        array.Center = App.Vector(*center)
        array.Axis = App.Vector(*axis)

        return {
            "created_objects": [array.Name],
            "object": array,
            "source_object": object_name,
            "count": count,
            "angle": angle,
            "center": center,
            "axis": axis,
        }

    def _scale_object(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Scale object by factor."""
        object_name = params["object"]
        scale_factor = params.get("scale_factor", 1.0)
        scale_vector = params.get(
            "scale_vector", [scale_factor, scale_factor, scale_factor]
        )
        name = params.get("name", f"{object_name}_Scaled")

        doc = App.ActiveDocument
        obj = doc.getObject(object_name)
        if not obj:
            raise ValueError(f"Object {object_name} not found")

        # Create scaled copy
        scaled = doc.addObject("Part::Feature", name)
        scaled.Shape = obj.Shape.scaled(*scale_vector)

        return {
            "created_objects": [scaled.Name],
            "object": scaled,
            "source_object": object_name,
            "scale_factor": scale_factor,
            "scale_vector": scale_vector,
        }

    def _rotate_object(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Rotate object around axis."""
        object_name = params["object"]
        axis = params.get("axis", [0, 0, 1])
        angle = params["angle"]  # In degrees
        center = params.get("center", [0, 0, 0])
        name = params.get("name", f"{object_name}_Rotated")

        doc = App.ActiveDocument
        obj = doc.getObject(object_name)
        if not obj:
            raise ValueError(f"Object {object_name} not found")

        # Create rotation
        rotation = App.Rotation(App.Vector(*axis), angle)
        placement = App.Placement(App.Vector(*center), rotation)

        # Create rotated copy
        rotated = doc.addObject("Part::Feature", name)
        rotated.Shape = obj.Shape
        rotated.Placement = placement

        return {
            "created_objects": [rotated.Name],
            "object": rotated,
            "source_object": object_name,
            "angle": angle,
            "axis": axis,
            "center": center,
        }

    def _translate_object(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Translate object by vector."""
        object_name = params["object"]
        translation = params["translation"]  # [x, y, z] vector
        name = params.get("name", f"{object_name}_Translated")

        doc = App.ActiveDocument
        obj = doc.getObject(object_name)
        if not obj:
            raise ValueError(f"Object {object_name} not found")

        # Create translated copy
        translated = doc.addObject("Part::Feature", name)
        translated.Shape = obj.Shape
        translated.Placement.Base = App.Vector(*translation)

        return {
            "created_objects": [translated.Name],
            "object": translated,
            "source_object": object_name,
            "translation": translation,
        }
