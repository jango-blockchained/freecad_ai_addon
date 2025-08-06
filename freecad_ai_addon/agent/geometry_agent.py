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
except ImportError:
    # Mock for testing outside FreeCAD
    App = None
    Part = None
    Draft = None

from .base_agent import BaseAgent, AgentTask, TaskResult, TaskStatus
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
        self.description = "Specialized agent for 3D geometric operations and part design"
        
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
            "boolean_union": self._boolean_union,
            "boolean_difference": self._boolean_difference,
            "boolean_intersection": self._boolean_intersection,
            "add_fillet": self._add_fillet,
            "add_chamfer": self._add_chamfer
        }
    
    def can_handle_task(self, task: AgentTask) -> bool:
        """Check if this agent can handle the given task."""
        if task.task_type not in self.capabilities:
            return False
        
        operation = task.parameters.get('operation')
        return operation in self.supported_operations
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validate task parameters."""
        operation = parameters.get('operation')
        if not operation:
            return False
        
        if operation not in self.supported_operations:
            return False
        
        # Validate operation-specific parameters
        if operation == "create_box":
            required = ['length', 'width', 'height']
            return all(param in parameters for param in required)
        
        elif operation == "create_cylinder":
            required = ['radius', 'height']
            return all(param in parameters for param in required)
        
        elif operation == "create_sphere":
            return 'radius' in parameters
        
        elif operation in ["boolean_union", "boolean_difference", "boolean_intersection"]:
            return 'objects' in parameters and len(parameters['objects']) >= 2
        
        elif operation in ["add_fillet", "add_chamfer"]:
            return 'object' in parameters and 'radius' in parameters
        
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
                "recommendations": ["Manual design decisions required"]
            }
    
    def handle_operation_error(self, operation: str, error: Exception, 
                              context: Dict[str, Any]) -> List[Dict[str, Any]]:
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
            return self.decision_engine.handle_operation_error(operation, error, context)
        else:
            # Fallback recovery strategies
            return [{
                "strategy": "retry_operation",
                "description": "Retry the operation",
                "success_probability": 0.3
            }]

    def execute_task(self, task: AgentTask) -> TaskResult:
        """Execute the geometric task."""
        operation = task.parameters.get('operation')
        operation_func = self.supported_operations.get(operation)
        
        if not operation_func:
            return TaskResult(
                status=TaskStatus.FAILED,
                error_message=f"Unsupported operation: {operation}"
            )
        
        try:
            result = operation_func(task.parameters)
            return TaskResult(
                status=TaskStatus.COMPLETED,
                result_data=result,
                created_objects=result.get('created_objects', []),
                modified_objects=result.get('modified_objects', [])
            )
        except Exception as e:
            return TaskResult(
                status=TaskStatus.FAILED,
                error_message=f"Operation {operation} failed: {str(e)}"
            )
    
    def _create_box(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a box primitive."""
        length = params['length']
        width = params['width'] 
        height = params['height']
        name = params.get('name', 'Box')
        placement = params.get('placement', None)
        
        doc = App.ActiveDocument
        box = doc.addObject("Part::Box", name)
        box.Length = length
        box.Width = width
        box.Height = height
        
        if placement:
            box.Placement = placement
        
        return {
            'created_objects': [box.Name],
            'object': box,
            'volume': box.Shape.Volume,
            'bounding_box': {
                'length': box.Shape.BoundBox.XLength,
                'width': box.Shape.BoundBox.YLength,
                'height': box.Shape.BoundBox.ZLength
            }
        }
    
    def _create_cylinder(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a cylinder primitive."""
        radius = params['radius']
        height = params['height']
        name = params.get('name', 'Cylinder')
        angle = params.get('angle', 360)  # Full cylinder by default
        placement = params.get('placement', None)
        
        doc = App.ActiveDocument
        cylinder = doc.addObject("Part::Cylinder", name)
        cylinder.Radius = radius
        cylinder.Height = height
        cylinder.Angle = angle
        
        if placement:
            cylinder.Placement = placement
        
        return {
            'created_objects': [cylinder.Name],
            'object': cylinder,
            'volume': cylinder.Shape.Volume,
            'surface_area': cylinder.Shape.Area
        }
    
    def _create_sphere(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a sphere primitive."""
        radius = params['radius']
        name = params.get('name', 'Sphere')
        angle1 = params.get('angle1', -90)  # Start angle
        angle2 = params.get('angle2', 90)   # End angle
        angle3 = params.get('angle3', 360)  # Full rotation by default
        placement = params.get('placement', None)
        
        doc = App.ActiveDocument
        sphere = doc.addObject("Part::Sphere", name)
        sphere.Radius = radius
        sphere.Angle1 = angle1
        sphere.Angle2 = angle2
        sphere.Angle3 = angle3
        
        if placement:
            sphere.Placement = placement
        
        return {
            'created_objects': [sphere.Name],
            'object': sphere,
            'volume': sphere.Shape.Volume,
            'surface_area': sphere.Shape.Area
        }
    
    def _create_cone(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a cone primitive."""
        radius1 = params['radius1']  # Bottom radius
        radius2 = params.get('radius2', 0)  # Top radius (0 for cone)
        height = params['height']
        name = params.get('name', 'Cone')
        angle = params.get('angle', 360)
        placement = params.get('placement', None)
        
        doc = App.ActiveDocument
        cone = doc.addObject("Part::Cone", name)
        cone.Radius1 = radius1
        cone.Radius2 = radius2
        cone.Height = height
        cone.Angle = angle
        
        if placement:
            cone.Placement = placement
        
        return {
            'created_objects': [cone.Name],
            'object': cone,
            'volume': cone.Shape.Volume,
            'surface_area': cone.Shape.Area
        }
    
    def _create_torus(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a torus primitive."""
        radius1 = params['radius1']  # Major radius
        radius2 = params['radius2']  # Minor radius
        name = params.get('name', 'Torus')
        angle1 = params.get('angle1', 0)
        angle2 = params.get('angle2', 360)
        angle3 = params.get('angle3', 360)
        placement = params.get('placement', None)
        
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
            'created_objects': [torus.Name],
            'object': torus,
            'volume': torus.Shape.Volume,
            'surface_area': torus.Shape.Area
        }
    
    def _boolean_union(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform boolean union operation."""
        objects = params['objects']
        name = params.get('name', 'Union')
        
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
        
        return {
            'created_objects': [union.Name],
            'object': union,
            'input_objects': objects,
            'volume': union.Shape.Volume
        }
    
    def _boolean_difference(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform boolean difference operation."""
        base_object = params['base_object']
        tool_objects = params['tool_objects']
        name = params.get('name', 'Difference')
        
        doc = App.ActiveDocument
        
        base = doc.getObject(base_object)
        if not base:
            raise ValueError(f"Base object {base_object} not found")
        
        tools = []
        for tool_name in tool_objects:
            tool = doc.getObject(tool_name)
            if not tool:
                raise ValueError(f"Tool object {tool_name} not found")
            tools.append(tool)
        
        # Create boolean difference
        difference = doc.addObject("Part::Cut", name)
        difference.Base = base
        difference.Tool = tools[0] if len(tools) == 1 else tools
        
        return {
            'created_objects': [difference.Name],
            'object': difference,
            'base_object': base_object,
            'tool_objects': tool_objects,
            'volume': difference.Shape.Volume
        }
    
    def _boolean_intersection(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform boolean intersection operation."""
        objects = params['objects']
        name = params.get('name', 'Intersection')
        
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
        
        return {
            'created_objects': [intersection.Name],
            'object': intersection,
            'input_objects': objects,
            'volume': intersection.Shape.Volume
        }
    
    def _add_fillet(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add fillet to object edges."""
        object_name = params['object']
        radius = params['radius']
        edges = params.get('edges', [])  # If empty, fillet all edges
        name = params.get('name', f'{object_name}_Fillet')
        
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
            edge_list = [(i+1, radius, radius) for i in range(edge_count)]
            fillet.Edges = edge_list
        
        return {
            'created_objects': [fillet.Name],
            'modified_objects': [object_name],
            'object': fillet,
            'radius': radius,
            'edge_count': len(edge_list)
        }
    
    def _add_chamfer(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add chamfer to object edges."""
        object_name = params['object']
        size = params['radius']  # Using 'radius' parameter for chamfer size
        edges = params.get('edges', [])
        name = params.get('name', f'{object_name}_Chamfer')
        
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
            edge_list = [(i+1, size, size) for i in range(edge_count)]
            chamfer.Edges = edge_list
        
        return {
            'created_objects': [chamfer.Name],
            'modified_objects': [object_name],
            'object': chamfer,
            'size': size,
            'edge_count': len(edge_list)
        }
    
    def _mirror_object(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Mirror object across a plane."""
        object_name = params['object']
        mirror_plane = params.get('plane', 'XY')  # XY, XZ, or YZ
        name = params.get('name', f'{object_name}_Mirror')
        
        doc = App.ActiveDocument
        obj = doc.getObject(object_name)
        if not obj:
            raise ValueError(f"Object {object_name} not found")
        
        mirror = doc.addObject("Part::Mirroring", name)
        mirror.Source = obj
        
        # Set mirror plane
        if mirror_plane == 'XY':
            mirror.Normal = App.Vector(0, 0, 1)
        elif mirror_plane == 'XZ':
            mirror.Normal = App.Vector(0, 1, 0)
        elif mirror_plane == 'YZ':
            mirror.Normal = App.Vector(1, 0, 0)
        else:
            # Custom normal vector
            mirror.Normal = App.Vector(*mirror_plane)
        
        return {
            'created_objects': [mirror.Name],
            'object': mirror,
            'source_object': object_name,
            'mirror_plane': mirror_plane
        }
    
    def _array_linear(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create linear array of object."""
        object_name = params['object']
        direction = params['direction']  # [x, y, z] vector
        count = params['count']
        spacing = params['spacing']
        name = params.get('name', f'{object_name}_LinearArray')
        
        doc = App.ActiveDocument
        obj = doc.getObject(object_name)
        if not obj:
            raise ValueError(f"Object {object_name} not found")
        
        # Use Draft workbench for array
        array = Draft.makeArray(
            obj,
            App.Vector(*direction) * spacing,
            App.Vector(0, 0, 0),
            count,
            1,
            name
        )
        
        return {
            'created_objects': [array.Name],
            'object': array,
            'source_object': object_name,
            'count': count,
            'spacing': spacing,
            'direction': direction
        }
    
    def _array_polar(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create polar array of object."""
        object_name = params['object']
        center = params.get('center', [0, 0, 0])
        axis = params.get('axis', [0, 0, 1])
        count = params['count']
        angle = params.get('angle', 360)  # Total angle for array
        name = params.get('name', f'{object_name}_PolarArray')
        
        doc = App.ActiveDocument
        obj = doc.getObject(object_name)
        if not obj:
            raise ValueError(f"Object {object_name} not found")
        
        # Use Draft workbench for polar array
        array = Draft.makeArray(
            obj,
            App.Vector(0, 0, 0),
            App.Vector(*axis),
            1,
            count,
            name
        )
        
        # Set array properties
        array.ArrayType = "polar"
        array.NumberPolar = count
        array.AnglePolar = angle
        array.Center = App.Vector(*center)
        array.Axis = App.Vector(*axis)
        
        return {
            'created_objects': [array.Name],
            'object': array,
            'source_object': object_name,
            'count': count,
            'angle': angle,
            'center': center,
            'axis': axis
        }
    
    def _scale_object(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Scale object by factor."""
        object_name = params['object']
        scale_factor = params.get('scale_factor', 1.0)
        scale_vector = params.get('scale_vector', [scale_factor, scale_factor, scale_factor])
        name = params.get('name', f'{object_name}_Scaled')
        
        doc = App.ActiveDocument
        obj = doc.getObject(object_name)
        if not obj:
            raise ValueError(f"Object {object_name} not found")
        
        # Create scaled copy
        scaled = doc.addObject("Part::Feature", name)
        scaled.Shape = obj.Shape.scaled(*scale_vector)
        
        return {
            'created_objects': [scaled.Name],
            'object': scaled,
            'source_object': object_name,
            'scale_factor': scale_factor,
            'scale_vector': scale_vector
        }
    
    def _rotate_object(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Rotate object around axis."""
        object_name = params['object']
        axis = params.get('axis', [0, 0, 1])
        angle = params['angle']  # In degrees
        center = params.get('center', [0, 0, 0])
        name = params.get('name', f'{object_name}_Rotated')
        
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
            'created_objects': [rotated.Name],
            'object': rotated,
            'source_object': object_name,
            'angle': angle,
            'axis': axis,
            'center': center
        }
    
    def _translate_object(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Translate object by vector."""
        object_name = params['object']
        translation = params['translation']  # [x, y, z] vector
        name = params.get('name', f'{object_name}_Translated')
        
        doc = App.ActiveDocument
        obj = doc.getObject(object_name)
        if not obj:
            raise ValueError(f"Object {object_name} not found")
        
        # Create translated copy
        translated = doc.addObject("Part::Feature", name)
        translated.Shape = obj.Shape
        translated.Placement.Base = App.Vector(*translation)
        
        return {
            'created_objects': [translated.Name],
            'object': translated,
            'source_object': object_name,
            'translation': translation
        }
