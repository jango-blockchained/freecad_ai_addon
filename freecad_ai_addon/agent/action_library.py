"""
Advanced Action Library for FreeCAD AI Addon
Provides structured actions for geometry, sketching, and analysis operations.
"""

from typing import Dict, Any, List, Optional, Tuple, Union
import logging

try:
    import FreeCAD as App
    import FreeCADGui as Gui
    import Part
    import Sketcher
    import Draft
    import PartDesign
    import Arch
except ImportError:
    # Mock for testing outside FreeCAD
    App = None
    Gui = None
    Part = None
    Sketcher = None
    Draft = None
    PartDesign = None
    Arch = None

logger = logging.getLogger(__name__)


class ActionLibrary:
    """
    Comprehensive action library for FreeCAD operations.
    
    Provides high-level functions for parametric modeling, feature creation,
    and geometric operations that can be easily called by AI agents.
    """
    
    def __init__(self):
        """Initialize the action library"""
        self.logger = logging.getLogger(f"{__name__}.ActionLibrary")
        self.operation_history = []
        self.created_objects = []
        self.modified_objects = []
        
        # Feature creation registry
        self.feature_registry = {
            # Basic primitives
            'box': self.create_box,
            'cylinder': self.create_cylinder,
            'sphere': self.create_sphere,
            'cone': self.create_cone,
            'torus': self.create_torus,
            'wedge': self.create_wedge,
            
            # Advanced primitives
            'helix': self.create_helix,
            'spiral': self.create_spiral,
            
            # Sketch-based features
            'extrude': self.create_extrusion,
            'revolve': self.create_revolution,
            'sweep': self.create_sweep,
            'loft': self.create_loft,
            
            # Modification features
            'fillet': self.add_fillet,
            'chamfer': self.add_chamfer,
            'shell': self.create_shell,
            'thickness': self.add_thickness,
            'draft': self.add_draft_angle,
            
            # Pattern features
            'linear_pattern': self.create_linear_pattern,
            'circular_pattern': self.create_circular_pattern,
            'mirror': self.create_mirror,
            
            # Boolean operations
            'union': self.boolean_union,
            'difference': self.boolean_difference,
            'intersection': self.boolean_intersection,
            'cut': self.boolean_cut,
            'fuse': self.boolean_fuse,
            
            # Measurement and analysis
            'measure_distance': self.measure_distance,
            'measure_angle': self.measure_angle,
            'calculate_volume': self.calculate_volume,
            'calculate_surface_area': self.calculate_surface_area,
            'center_of_mass': self.get_center_of_mass,
            'bounding_box': self.get_bounding_box,
        }
        
        self.logger.info("Action Library initialized with %d operations", len(self.feature_registry))
    
    def get_available_operations(self) -> List[str]:
        """Get list of all available operations"""
        return list(self.feature_registry.keys())
    
    def execute_operation(self, operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a named operation with parameters.
        
        Args:
            operation: Name of the operation to execute
            parameters: Dictionary of parameters for the operation
            
        Returns:
            Result dictionary with status, created objects, and operation details
        """
        if operation not in self.feature_registry:
            return {
                'status': 'failed',
                'error': f"Unknown operation: {operation}",
                'available_operations': self.get_available_operations()
            }
        
        try:
            operation_func = self.feature_registry[operation]
            result = operation_func(**parameters)
            
            # Record in history
            self.operation_history.append({
                'operation': operation,
                'parameters': parameters,
                'result': result,
                'timestamp': App.Date() if App else None
            })
            
            return {
                'status': 'success',
                'operation': operation,
                'result': result,
                'parameters': parameters
            }
            
        except Exception as e:
            self.logger.error(f"Operation {operation} failed: {str(e)}")
            return {
                'status': 'failed',
                'operation': operation,
                'error': str(e),
                'parameters': parameters
            }
    
    # ========================================================================
    # BASIC PRIMITIVE CREATION
    # ========================================================================
    
    def create_box(self, length: float, width: float, height: float,
                   name: str = "Box", placement: Optional[Any] = None) -> Dict[str, Any]:
        """
        Create a parametric box.
        
        Args:
            length: Box length (X-direction)
            width: Box width (Y-direction)  
            height: Box height (Z-direction)
            name: Object name
            placement: FreeCAD placement object
            
        Returns:
            Dictionary with created object information
        """
        if not App or not App.ActiveDocument:
            raise RuntimeError("No active FreeCAD document")
        
        doc = App.ActiveDocument
        box = doc.addObject("Part::Box", name)
        box.Length = length
        box.Width = width
        box.Height = height
        
        if placement:
            box.Placement = placement
        
        doc.recompute()
        self.created_objects.append(box.Name)
        
        return {
            'object_name': box.Name,
            'object_type': 'Box',
            'volume': box.Shape.Volume,
            'surface_area': box.Shape.Area,
            'dimensions': {'length': length, 'width': width, 'height': height},
            'bounding_box': self._get_bounding_box_dict(box.Shape.BoundBox)
        }
    
    def create_cylinder(self, radius: float, height: float,
                       name: str = "Cylinder", angle: float = 360.0,
                       placement: Optional[Any] = None) -> Dict[str, Any]:
        """
        Create a parametric cylinder.
        
        Args:
            radius: Cylinder radius
            height: Cylinder height
            name: Object name
            angle: Sweep angle in degrees (360 for full cylinder)
            placement: FreeCAD placement object
            
        Returns:
            Dictionary with created object information
        """
        if not App or not App.ActiveDocument:
            raise RuntimeError("No active FreeCAD document")
        
        doc = App.ActiveDocument
        cylinder = doc.addObject("Part::Cylinder", name)
        cylinder.Radius = radius
        cylinder.Height = height
        cylinder.Angle = angle
        
        if placement:
            cylinder.Placement = placement
        
        doc.recompute()
        self.created_objects.append(cylinder.Name)
        
        return {
            'object_name': cylinder.Name,
            'object_type': 'Cylinder',
            'volume': cylinder.Shape.Volume,
            'surface_area': cylinder.Shape.Area,
            'dimensions': {'radius': radius, 'height': height, 'angle': angle},
            'bounding_box': self._get_bounding_box_dict(cylinder.Shape.BoundBox)
        }
    
    def create_sphere(self, radius: float, name: str = "Sphere",
                     angle1: float = -90.0, angle2: float = 90.0, angle3: float = 360.0,
                     placement: Optional[Any] = None) -> Dict[str, Any]:
        """
        Create a parametric sphere.
        
        Args:
            radius: Sphere radius
            name: Object name
            angle1: Start angle for vertical sweep
            angle2: End angle for vertical sweep
            angle3: Horizontal sweep angle
            placement: FreeCAD placement object
            
        Returns:
            Dictionary with created object information
        """
        if not App or not App.ActiveDocument:
            raise RuntimeError("No active FreeCAD document")
        
        doc = App.ActiveDocument
        sphere = doc.addObject("Part::Sphere", name)
        sphere.Radius = radius
        sphere.Angle1 = angle1
        sphere.Angle2 = angle2
        sphere.Angle3 = angle3
        
        if placement:
            sphere.Placement = placement
        
        doc.recompute()
        self.created_objects.append(sphere.Name)
        
        return {
            'object_name': sphere.Name,
            'object_type': 'Sphere',
            'volume': sphere.Shape.Volume,
            'surface_area': sphere.Shape.Area,
            'dimensions': {'radius': radius, 'angle1': angle1, 'angle2': angle2, 'angle3': angle3},
            'bounding_box': self._get_bounding_box_dict(sphere.Shape.BoundBox)
        }
    
    def create_cone(self, radius1: float, radius2: float, height: float,
                   name: str = "Cone", angle: float = 360.0,
                   placement: Optional[Any] = None) -> Dict[str, Any]:
        """
        Create a parametric cone.
        
        Args:
            radius1: Bottom radius
            radius2: Top radius (0 for pointed cone)
            height: Cone height
            name: Object name
            angle: Sweep angle in degrees
            placement: FreeCAD placement object
            
        Returns:
            Dictionary with created object information
        """
        if not App or not App.ActiveDocument:
            raise RuntimeError("No active FreeCAD document")
        
        doc = App.ActiveDocument
        cone = doc.addObject("Part::Cone", name)
        cone.Radius1 = radius1
        cone.Radius2 = radius2
        cone.Height = height
        cone.Angle = angle
        
        if placement:
            cone.Placement = placement
        
        doc.recompute()
        self.created_objects.append(cone.Name)
        
        return {
            'object_name': cone.Name,
            'object_type': 'Cone',
            'volume': cone.Shape.Volume,
            'surface_area': cone.Shape.Area,
            'dimensions': {'radius1': radius1, 'radius2': radius2, 'height': height, 'angle': angle},
            'bounding_box': self._get_bounding_box_dict(cone.Shape.BoundBox)
        }
    
    def create_torus(self, radius1: float, radius2: float,
                    name: str = "Torus", angle1: float = -180.0, angle2: float = 180.0, angle3: float = 360.0,
                    placement: Optional[Any] = None) -> Dict[str, Any]:
        """
        Create a parametric torus.
        
        Args:
            radius1: Major radius (center to tube center)
            radius2: Minor radius (tube radius)
            name: Object name
            angle1: Start angle for meridional sweep
            angle2: End angle for meridional sweep
            angle3: Toroidal sweep angle
            placement: FreeCAD placement object
            
        Returns:
            Dictionary with created object information
        """
        if not App or not App.ActiveDocument:
            raise RuntimeError("No active FreeCAD document")
        
        doc = App.ActiveDocument
        torus = doc.addObject("Part::Torus", name)
        torus.Radius1 = radius1
        torus.Radius2 = radius2
        torus.Angle1 = angle1
        torus.Angle2 = angle2
        torus.Angle3 = angle3
        
        if placement:
            torus.Placement = placement
        
        doc.recompute()
        self.created_objects.append(torus.Name)
        
        return {
            'object_name': torus.Name,
            'object_type': 'Torus',
            'volume': torus.Shape.Volume,
            'surface_area': torus.Shape.Area,
            'dimensions': {'radius1': radius1, 'radius2': radius2, 'angle1': angle1, 'angle2': angle2, 'angle3': angle3},
            'bounding_box': self._get_bounding_box_dict(torus.Shape.BoundBox)
        }
    
    def create_wedge(self, xmin: float, ymin: float, zmin: float,
                    z2min: float, x2min: float, xmax: float, ymax: float, zmax: float,
                    z2max: float, x2max: float, name: str = "Wedge",
                    placement: Optional[Any] = None) -> Dict[str, Any]:
        """
        Create a parametric wedge.
        
        Args:
            xmin, ymin, zmin: Minimum coordinates
            z2min, x2min: Additional parameters for wedge shape
            xmax, ymax, zmax: Maximum coordinates  
            z2max, x2max: Additional parameters for wedge shape
            name: Object name
            placement: FreeCAD placement object
            
        Returns:
            Dictionary with created object information
        """
        if not App or not App.ActiveDocument:
            raise RuntimeError("No active FreeCAD document")
        
        doc = App.ActiveDocument
        wedge = doc.addObject("Part::Wedge", name)
        wedge.Xmin = xmin
        wedge.Ymin = ymin
        wedge.Zmin = zmin
        wedge.Z2min = z2min
        wedge.X2min = x2min
        wedge.Xmax = xmax
        wedge.Ymax = ymax
        wedge.Zmax = zmax
        wedge.Z2max = z2max
        wedge.X2max = x2max
        
        if placement:
            wedge.Placement = placement
        
        doc.recompute()
        self.created_objects.append(wedge.Name)
        
        return {
            'object_name': wedge.Name,
            'object_type': 'Wedge',
            'volume': wedge.Shape.Volume,
            'surface_area': wedge.Shape.Area,
            'bounding_box': self._get_bounding_box_dict(wedge.Shape.BoundBox)
        }
    
    # ========================================================================
    # ADVANCED PRIMITIVE CREATION
    # ========================================================================
    
    def create_helix(self, pitch: float, height: float, radius: float,
                    name: str = "Helix", angle: float = 0.0, 
                    localcoord: int = 0, style: int = 0,
                    placement: Optional[Any] = None) -> Dict[str, Any]:
        """
        Create a parametric helix.
        
        Args:
            pitch: Distance between turns
            height: Total height
            radius: Helix radius
            name: Object name
            angle: Growth angle
            localcoord: Local coordinate system (0=right-handed, 1=left-handed)
            style: Helix style (0=cylindrical, 1=conical, 2=spherical)
            placement: FreeCAD placement object
            
        Returns:
            Dictionary with created object information
        """
        if not App or not App.ActiveDocument:
            raise RuntimeError("No active FreeCAD document")
        
        doc = App.ActiveDocument
        helix = doc.addObject("Part::Helix", name)
        helix.Pitch = pitch
        helix.Height = height
        helix.Radius = radius
        helix.Angle = angle
        helix.LocalCoord = localcoord
        helix.Style = style
        
        if placement:
            helix.Placement = placement
        
        doc.recompute()
        self.created_objects.append(helix.Name)
        
        return {
            'object_name': helix.Name,
            'object_type': 'Helix',
            'length': helix.Shape.Length,
            'dimensions': {'pitch': pitch, 'height': height, 'radius': radius, 'angle': angle},
            'bounding_box': self._get_bounding_box_dict(helix.Shape.BoundBox)
        }
    
    def create_spiral(self, growth: float, rotations: float, radius: float,
                     name: str = "Spiral", placement: Optional[Any] = None) -> Dict[str, Any]:
        """
        Create a parametric spiral.
        
        Args:
            growth: Growth factor per rotation
            rotations: Number of rotations
            radius: Starting radius
            name: Object name
            placement: FreeCAD placement object
            
        Returns:
            Dictionary with created object information
        """
        if not App or not App.ActiveDocument:
            raise RuntimeError("No active FreeCAD document")
        
        doc = App.ActiveDocument
        spiral = doc.addObject("Part::Spiral", name)
        spiral.Growth = growth
        spiral.Rotations = rotations
        spiral.Radius = radius
        
        if placement:
            spiral.Placement = placement
        
        doc.recompute()
        self.created_objects.append(spiral.Name)
        
        return {
            'object_name': spiral.Name,
            'object_type': 'Spiral',
            'length': spiral.Shape.Length,
            'dimensions': {'growth': growth, 'rotations': rotations, 'radius': radius},
            'bounding_box': self._get_bounding_box_dict(spiral.Shape.BoundBox)
        }
    
    # ========================================================================
    # BOOLEAN OPERATIONS
    # ========================================================================
    
    def boolean_union(self, objects: List[str], name: str = "Union") -> Dict[str, Any]:
        """
        Create a boolean union of multiple objects.
        
        Args:
            objects: List of object names to union
            name: Name for the resulting object
            
        Returns:
            Dictionary with operation result information
        """
        if not App or not App.ActiveDocument:
            raise RuntimeError("No active FreeCAD document")
        
        if len(objects) < 2:
            raise ValueError("Boolean union requires at least 2 objects")
        
        doc = App.ActiveDocument
        base_obj = doc.getObject(objects[0])
        
        for obj_name in objects[1:]:
            tool_obj = doc.getObject(obj_name)
            if not tool_obj:
                raise ValueError(f"Object {obj_name} not found")
            
            union = doc.addObject("Part::Fuse", name)
            union.Base = base_obj
            union.Tool = tool_obj
            base_obj = union
        
        doc.recompute()
        self.created_objects.append(union.Name)
        self.modified_objects.extend(objects)
        
        return {
            'object_name': union.Name,
            'object_type': 'Boolean Union',
            'volume': union.Shape.Volume,
            'surface_area': union.Shape.Area,
            'input_objects': objects,
            'bounding_box': self._get_bounding_box_dict(union.Shape.BoundBox)
        }
    
    def boolean_difference(self, base: str, tool: str, name: str = "Difference") -> Dict[str, Any]:
        """
        Create a boolean difference (cut) operation.
        
        Args:
            base: Base object name
            tool: Tool object name (to be subtracted)
            name: Name for the resulting object
            
        Returns:
            Dictionary with operation result information
        """
        if not App or not App.ActiveDocument:
            raise RuntimeError("No active FreeCAD document")
        
        doc = App.ActiveDocument
        base_obj = doc.getObject(base)
        tool_obj = doc.getObject(tool)
        
        if not base_obj:
            raise ValueError(f"Base object {base} not found")
        if not tool_obj:
            raise ValueError(f"Tool object {tool} not found")
        
        cut = doc.addObject("Part::Cut", name)
        cut.Base = base_obj
        cut.Tool = tool_obj
        
        doc.recompute()
        self.created_objects.append(cut.Name)
        self.modified_objects.extend([base, tool])
        
        return {
            'object_name': cut.Name,
            'object_type': 'Boolean Difference',
            'volume': cut.Shape.Volume,
            'surface_area': cut.Shape.Area,
            'base_object': base,
            'tool_object': tool,
            'bounding_box': self._get_bounding_box_dict(cut.Shape.BoundBox)
        }
    
    def boolean_intersection(self, objects: List[str], name: str = "Intersection") -> Dict[str, Any]:
        """
        Create a boolean intersection of multiple objects.
        
        Args:
            objects: List of object names to intersect
            name: Name for the resulting object
            
        Returns:
            Dictionary with operation result information
        """
        if not App or not App.ActiveDocument:
            raise RuntimeError("No active FreeCAD document")
        
        if len(objects) < 2:
            raise ValueError("Boolean intersection requires at least 2 objects")
        
        doc = App.ActiveDocument
        base_obj = doc.getObject(objects[0])
        tool_obj = doc.getObject(objects[1])
        
        common = doc.addObject("Part::Common", name)
        common.Base = base_obj
        common.Tool = tool_obj
        
        # For more than 2 objects, chain the intersections
        for obj_name in objects[2:]:
            next_obj = doc.getObject(obj_name)
            new_common = doc.addObject("Part::Common", f"{name}_stage")
            new_common.Base = common
            new_common.Tool = next_obj
            common = new_common
        
        doc.recompute()
        self.created_objects.append(common.Name)
        self.modified_objects.extend(objects)
        
        return {
            'object_name': common.Name,
            'object_type': 'Boolean Intersection',
            'volume': common.Shape.Volume,
            'surface_area': common.Shape.Area,
            'input_objects': objects,
            'bounding_box': self._get_bounding_box_dict(common.Shape.BoundBox)
        }
    
    # Aliases for common operations
    def boolean_cut(self, base: str, tool: str, name: str = "Cut") -> Dict[str, Any]:
        """Alias for boolean_difference"""
        return self.boolean_difference(base, tool, name)
    
    def boolean_fuse(self, objects: List[str], name: str = "Fuse") -> Dict[str, Any]:
        """Alias for boolean_union"""
        return self.boolean_union(objects, name)
    
    # ========================================================================
    # MODIFICATION FEATURES
    # ========================================================================
    
    def add_fillet(self, obj_name: str, edges: Union[List[int], List], 
                  radius: float, name: str = "Fillet") -> Dict[str, Any]:
        """
        Add fillets to specified edges of an object.
        
        Args:
            obj_name: Name of the object to fillet
            edges: List of edge indices or edge objects
            radius: Fillet radius
            name: Name for the resulting object
            
        Returns:
            Dictionary with operation result information
        """
        if not App or not App.ActiveDocument:
            raise RuntimeError("No active FreeCAD document")
        
        doc = App.ActiveDocument
        obj = doc.getObject(obj_name)
        
        if not obj:
            raise ValueError(f"Object {obj_name} not found")
        
        fillet = doc.addObject("Part::Fillet", name)
        fillet.Base = obj
        
        # Add edges to fillet
        if isinstance(edges[0], int):
            # Edge indices provided
            fillet.Edges = [(i, radius, radius) for i in edges]
        else:
            # Edge objects provided - convert to indices
            edge_indices = []
            for edge in edges:
                for i, shape_edge in enumerate(obj.Shape.Edges):
                    if shape_edge.isSame(edge):
                        edge_indices.append(i)
                        break
            fillet.Edges = [(i, radius, radius) for i in edge_indices]
        
        doc.recompute()
        self.created_objects.append(fillet.Name)
        self.modified_objects.append(obj_name)
        
        return {
            'object_name': fillet.Name,
            'object_type': 'Fillet',
            'volume': fillet.Shape.Volume,
            'surface_area': fillet.Shape.Area,
            'base_object': obj_name,
            'radius': radius,
            'edge_count': len(edges),
            'bounding_box': self._get_bounding_box_dict(fillet.Shape.BoundBox)
        }
    
    def add_chamfer(self, obj_name: str, edges: Union[List[int], List],
                   size: float, name: str = "Chamfer") -> Dict[str, Any]:
        """
        Add chamfers to specified edges of an object.
        
        Args:
            obj_name: Name of the object to chamfer
            edges: List of edge indices or edge objects
            size: Chamfer size
            name: Name for the resulting object
            
        Returns:
            Dictionary with operation result information
        """
        if not App or not App.ActiveDocument:
            raise RuntimeError("No active FreeCAD document")
        
        doc = App.ActiveDocument
        obj = doc.getObject(obj_name)
        
        if not obj:
            raise ValueError(f"Object {obj_name} not found")
        
        chamfer = doc.addObject("Part::Chamfer", name)
        chamfer.Base = obj
        
        # Add edges to chamfer
        if isinstance(edges[0], int):
            # Edge indices provided
            chamfer.Edges = [(i, size, size) for i in edges]
        else:
            # Edge objects provided - convert to indices
            edge_indices = []
            for edge in edges:
                for i, shape_edge in enumerate(obj.Shape.Edges):
                    if shape_edge.isSame(edge):
                        edge_indices.append(i)
                        break
            chamfer.Edges = [(i, size, size) for i in edge_indices]
        
        doc.recompute()
        self.created_objects.append(chamfer.Name)
        self.modified_objects.append(obj_name)
        
        return {
            'object_name': chamfer.Name,
            'object_type': 'Chamfer',
            'volume': chamfer.Shape.Volume,
            'surface_area': chamfer.Shape.Area,
            'base_object': obj_name,
            'size': size,
            'edge_count': len(edges),
            'bounding_box': self._get_bounding_box_dict(chamfer.Shape.BoundBox)
        }
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def _get_bounding_box_dict(self, bbox) -> Dict[str, float]:
        """Convert FreeCAD BoundBox to dictionary"""
        if not bbox:
            return {}
        
        return {
            'xmin': bbox.XMin,
            'xmax': bbox.XMax,
            'ymin': bbox.YMin,
            'ymax': bbox.YMax,
            'zmin': bbox.ZMin,
            'zmax': bbox.ZMax,
            'xlength': bbox.XLength,
            'ylength': bbox.YLength,
            'zlength': bbox.ZLength
        }
    
    # ========================================================================
    # MEASUREMENT AND ANALYSIS
    # ========================================================================
    
    def measure_distance(self, obj1_name: str, obj2_name: str = None,
                        point1: Tuple[float, float, float] = None,
                        point2: Tuple[float, float, float] = None) -> Dict[str, Any]:
        """
        Measure distance between objects or points.
        
        Args:
            obj1_name: First object name
            obj2_name: Second object name (optional)
            point1: First point coordinates (optional)
            point2: Second point coordinates (optional)
            
        Returns:
            Dictionary with distance measurement information
        """
        if not App or not App.ActiveDocument:
            raise RuntimeError("No active FreeCAD document")
        
        doc = App.ActiveDocument
        
        if point1 and point2:
            # Point to point distance
            p1 = App.Vector(*point1)
            p2 = App.Vector(*point2)
            distance = p1.distanceToPoint(p2)
            
            return {
                'measurement_type': 'point_to_point',
                'distance': distance,
                'point1': point1,
                'point2': point2,
                'units': 'mm'
            }
        
        elif obj1_name and obj2_name:
            # Object to object distance
            obj1 = doc.getObject(obj1_name)
            obj2 = doc.getObject(obj2_name)
            
            if not obj1 or not obj2:
                raise ValueError("One or both objects not found")
            
            distance = obj1.Shape.distToShape(obj2.Shape)[0]
            
            return {
                'measurement_type': 'object_to_object',
                'distance': distance,
                'object1': obj1_name,
                'object2': obj2_name,
                'units': 'mm'
            }
        
        else:
            raise ValueError("Must provide either two objects or two points")
    
    def calculate_volume(self, obj_name: str) -> Dict[str, Any]:
        """
        Calculate volume of an object.
        
        Args:
            obj_name: Object name
            
        Returns:
            Dictionary with volume information
        """
        if not App or not App.ActiveDocument:
            raise RuntimeError("No active FreeCAD document")
        
        doc = App.ActiveDocument
        obj = doc.getObject(obj_name)
        
        if not obj:
            raise ValueError(f"Object {obj_name} not found")
        
        if not hasattr(obj, 'Shape'):
            raise ValueError(f"Object {obj_name} has no shape")
        
        volume = obj.Shape.Volume
        
        return {
            'object_name': obj_name,
            'volume': volume,
            'units': 'mm³',
            'volume_liters': volume / 1000000.0,
            'measurement_type': 'volume'
        }
    
    def calculate_surface_area(self, obj_name: str) -> Dict[str, Any]:
        """
        Calculate surface area of an object.
        
        Args:
            obj_name: Object name
            
        Returns:
            Dictionary with surface area information
        """
        if not App or not App.ActiveDocument:
            raise RuntimeError("No active FreeCAD document")
        
        doc = App.ActiveDocument
        obj = doc.getObject(obj_name)
        
        if not obj:
            raise ValueError(f"Object {obj_name} not found")
        
        if not hasattr(obj, 'Shape'):
            raise ValueError(f"Object {obj_name} has no shape")
        
        area = obj.Shape.Area
        
        return {
            'object_name': obj_name,
            'surface_area': area,
            'units': 'mm²',
            'area_m2': area / 1000000.0,
            'measurement_type': 'surface_area'
        }
    
    def get_center_of_mass(self, obj_name: str) -> Dict[str, Any]:
        """
        Get center of mass of an object.
        
        Args:
            obj_name: Object name
            
        Returns:
            Dictionary with center of mass information
        """
        if not App or not App.ActiveDocument:
            raise RuntimeError("No active FreeCAD document")
        
        doc = App.ActiveDocument
        obj = doc.getObject(obj_name)
        
        if not obj:
            raise ValueError(f"Object {obj_name} not found")
        
        if not hasattr(obj, 'Shape'):
            raise ValueError(f"Object {obj_name} has no shape")
        
        com = obj.Shape.CenterOfMass
        
        return {
            'object_name': obj_name,
            'center_of_mass': {'x': com.x, 'y': com.y, 'z': com.z},
            'units': 'mm',
            'measurement_type': 'center_of_mass'
        }
    
    def get_bounding_box(self, obj_name: str) -> Dict[str, Any]:
        """
        Get bounding box of an object.
        
        Args:
            obj_name: Object name
            
        Returns:
            Dictionary with bounding box information
        """
        if not App or not App.ActiveDocument:
            raise RuntimeError("No active FreeCAD document")
        
        doc = App.ActiveDocument
        obj = doc.getObject(obj_name)
        
        if not obj:
            raise ValueError(f"Object {obj_name} not found")
        
        if not hasattr(obj, 'Shape'):
            raise ValueError(f"Object {obj_name} has no shape")
        
        bbox = obj.Shape.BoundBox
        bbox_dict = self._get_bounding_box_dict(bbox)
        bbox_dict.update({
            'object_name': obj_name,
            'units': 'mm',
            'measurement_type': 'bounding_box'
        })
        
        return bbox_dict
    
    # ========================================================================
    # OPERATION HISTORY AND STATE
    # ========================================================================
    
    def get_operation_history(self) -> List[Dict[str, Any]]:
        """Get history of all executed operations"""
        return self.operation_history.copy()
    
    def get_created_objects(self) -> List[str]:
        """Get list of all objects created by this action library"""
        return self.created_objects.copy()
    
    def get_modified_objects(self) -> List[str]:
        """Get list of all objects modified by this action library"""
        return self.modified_objects.copy()
    
    def clear_history(self):
        """Clear operation history and object tracking"""
        self.operation_history.clear()
        self.created_objects.clear()
        self.modified_objects.clear()
    
    # ========================================================================
    # PLACEHOLDER IMPLEMENTATIONS FOR MISSING METHODS
    # ========================================================================
    
    def create_extrusion(self, sketch_name: str, distance: float,
                        direction: Tuple[float, float, float] = (0, 0, 1),
                        name: str = "Extrusion") -> Dict[str, Any]:
        """Placeholder for extrusion creation"""
        return {
            'status': 'not_implemented',
            'operation': 'create_extrusion',
            'sketch_name': sketch_name,
            'distance': distance
        }
    
    def create_revolution(self, sketch_name: str, axis: Tuple[float, float, float],
                         angle: float = 360.0, name: str = "Revolution") -> Dict[str, Any]:
        """Placeholder for revolution creation"""
        return {
            'status': 'not_implemented',
            'operation': 'create_revolution',
            'sketch_name': sketch_name,
            'angle': angle
        }
    
    def create_sweep(self, profile_sketch: str, path_sketch: str,
                    name: str = "Sweep") -> Dict[str, Any]:
        """Placeholder for sweep creation"""
        return {
            'status': 'not_implemented',
            'operation': 'create_sweep',
            'profile_sketch': profile_sketch,
            'path_sketch': path_sketch
        }
    
    def create_loft(self, sketches: List[str], name: str = "Loft") -> Dict[str, Any]:
        """Placeholder for loft creation"""
        return {
            'status': 'not_implemented',
            'operation': 'create_loft',
            'sketches': sketches
        }
    
    def create_shell(self, obj_name: str, faces: List[int], thickness: float,
                    name: str = "Shell") -> Dict[str, Any]:
        """Placeholder for shell creation"""
        return {
            'status': 'not_implemented',
            'operation': 'create_shell',
            'obj_name': obj_name,
            'thickness': thickness
        }
    
    def add_thickness(self, obj_name: str, thickness: float,
                     name: str = "Thickness") -> Dict[str, Any]:
        """Placeholder for thickness addition"""
        return {
            'status': 'not_implemented',
            'operation': 'add_thickness',
            'obj_name': obj_name,
            'thickness': thickness
        }
    
    def add_draft_angle(self, obj_name: str, faces: List[int], angle: float,
                       direction: Tuple[float, float, float] = (0, 0, 1),
                       name: str = "Draft") -> Dict[str, Any]:
        """Placeholder for draft angle addition"""
        return {
            'status': 'not_implemented',
            'operation': 'add_draft_angle',
            'obj_name': obj_name,
            'angle': angle
        }
    
    def create_linear_pattern(self, obj_name: str, direction: Tuple[float, float, float],
                             count: int, spacing: float,
                             name: str = "LinearPattern") -> Dict[str, Any]:
        """Placeholder for linear pattern creation"""
        return {
            'status': 'not_implemented',
            'operation': 'create_linear_pattern',
            'obj_name': obj_name,
            'count': count,
            'spacing': spacing
        }
    
    def create_circular_pattern(self, obj_name: str, axis: Tuple[float, float, float],
                               count: int, angle: float,
                               name: str = "CircularPattern") -> Dict[str, Any]:
        """Placeholder for circular pattern creation"""
        return {
            'status': 'not_implemented',
            'operation': 'create_circular_pattern',
            'obj_name': obj_name,
            'count': count,
            'angle': angle
        }
    
    def create_mirror(self, obj_name: str, plane: str,
                     name: str = "Mirror") -> Dict[str, Any]:
        """Placeholder for mirror creation"""
        return {
            'status': 'not_implemented',
            'operation': 'create_mirror',
            'obj_name': obj_name,
            'plane': plane
        }
    
    def measure_angle(self, obj1_name: str, obj2_name: str,
                     reference_point: Tuple[float, float, float] = None) -> Dict[str, Any]:
        """Placeholder for angle measurement"""
        return {
            'status': 'not_implemented',
            'operation': 'measure_angle',
            'obj1_name': obj1_name,
            'obj2_name': obj2_name
        }
    
    def measure_curvature(self, obj_name: str, point: Tuple[float, float, float]) -> Dict[str, Any]:
        """Placeholder for curvature measurement"""
        return {
            'status': 'not_implemented',
            'operation': 'measure_curvature',
            'obj_name': obj_name,
            'point': point
        }
