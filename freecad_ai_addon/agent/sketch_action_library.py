"""
Sketch Action Library for FreeCAD AI Addon.

Comprehensive library for sketch creation, constraint management, and
2D geometric operations that can be executed by AI agents.
"""

from typing import Dict, Any, List, Optional, Tuple
import logging
import math

try:
    import FreeCAD as App
    import FreeCADGui as Gui
    import Part
    import Sketcher
    import Draft
except ImportError:
    # Mock for testing outside FreeCAD
    App = None
    Gui = None
    Part = None
    Sketcher = None
    Draft = None

logger = logging.getLogger(__name__)


class SketchActionLibrary:
    """
    Comprehensive sketch action library for FreeCAD operations.
    
    Provides high-level functions for sketch creation, constraint
    management, and 2D geometric operations.
    """
    
    def __init__(self):
        """Initialize the sketch action library"""
        self.logger = logging.getLogger(f"{__name__}.SketchActionLibrary")
        self.operation_history = []
        self.created_sketches = []
        self.modified_sketches = []
        
        # Sketch operation registry
        self.sketch_operations = {
            # Sketch management
            'create_sketch': self.create_sketch,
            'close_sketch': self.close_sketch,
            'fully_constrain': self.fully_constrain_sketch,
            
            # Basic geometry
            'add_line': self.add_line,
            'add_rectangle': self.add_rectangle,
            'add_circle': self.add_circle,
            'add_arc': self.add_arc,
            'add_ellipse': self.add_ellipse,
            'add_point': self.add_point,
            'add_polygon': self.add_polygon,
            'add_bspline': self.add_bspline,
            
            # Advanced geometry
            'add_slot': self.add_slot,
            'add_fillet': self.add_sketch_fillet,
            'add_chamfer': self.add_sketch_chamfer,
            
            # Constraints
            'add_horizontal_constraint': self.add_horizontal_constraint,
            'add_vertical_constraint': self.add_vertical_constraint,
            'add_parallel_constraint': self.add_parallel_constraint,
            'add_perpendicular_constraint': self.add_perpendicular_constraint,
            'add_tangent_constraint': self.add_tangent_constraint,
            'add_equal_constraint': self.add_equal_constraint,
            'add_coincident_constraint': self.add_coincident_constraint,
            'add_distance_constraint': self.add_distance_constraint,
            'add_radius_constraint': self.add_radius_constraint,
            'add_diameter_constraint': self.add_diameter_constraint,
            'add_angle_constraint': self.add_angle_constraint,
            'add_symmetric_constraint': self.add_symmetric_constraint,
            
            # Patterns and arrays
            'rectangular_pattern': self.create_rectangular_pattern,
            'polar_pattern': self.create_polar_pattern,
            'linear_pattern': self.create_linear_pattern,
            
            # Analysis and validation
            'get_sketch_info': self.get_sketch_info,
            'validate_sketch': self.validate_sketch,
            'check_constraints': self.check_constraints,
            'suggest_constraints': self.suggest_constraints,
        }
        
        # Constraint type mapping
        self.constraint_types = {
            'horizontal': 'Horizontal',
            'vertical': 'Vertical', 
            'parallel': 'Parallel',
            'perpendicular': 'Perpendicular',
            'tangent': 'Tangent',
            'equal': 'Equal',
            'coincident': 'Coincident',
            'distance': 'Distance',
            'distance_x': 'DistanceX',
            'distance_y': 'DistanceY',
            'radius': 'Radius',
            'diameter': 'Diameter',
            'angle': 'Angle',
            'symmetric': 'Symmetric',
            'point_on_object': 'PointOnObject',
            'block': 'Block'
        }
        
        self.logger.info("Sketch Action Library initialized with %d operations", 
                        len(self.sketch_operations))
    
    def execute_sketch_operation(self, operation: str, 
                               parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a named sketch operation with parameters.
        
        Args:
            operation: Name of the operation to execute
            parameters: Dictionary of parameters for the operation
            
        Returns:
            Result dictionary with status and operation details
        """
        if operation not in self.sketch_operations:
            return {
                'status': 'failed',
                'error': f"Unknown sketch operation: {operation}",
                'available_operations': list(self.sketch_operations.keys())
            }
        
        try:
            operation_func = self.sketch_operations[operation]
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
            self.logger.error(f"Sketch operation {operation} failed: {str(e)}")
            return {
                'status': 'failed',
                'operation': operation,
                'error': str(e),
                'parameters': parameters
            }
    
    # ===================================================================
    # SKETCH MANAGEMENT
    # ===================================================================
    
    def create_sketch(self, name: str = "Sketch", 
                     plane: str = "XY_Plane",
                     support: Optional[str] = None,
                     map_mode: str = "FlatFace") -> Dict[str, Any]:
        """
        Create a new sketch.
        
        Args:
            name: Sketch name
            plane: Reference plane (XY_Plane, XZ_Plane, YZ_Plane)
            support: Support object name (optional)
            map_mode: Attachment mapping mode
            
        Returns:
            Dictionary with sketch creation information
        """
        if not App or not App.ActiveDocument:
            raise RuntimeError("No active FreeCAD document")
        
        doc = App.ActiveDocument
        sketch = doc.addObject('Sketcher::SketchObject', name)
        
        # Set up attachment
        if support:
            support_obj = doc.getObject(support)
            if support_obj:
                sketch.Support = support_obj
                sketch.MapMode = map_mode
        else:
            # Attach to standard plane
            if plane == "XY_Plane":
                sketch.Placement.Rotation = App.Rotation(0, 0, 0, 1)
            elif plane == "XZ_Plane":
                sketch.Placement.Rotation = App.Rotation(1, 0, 0, -90)
            elif plane == "YZ_Plane":
                sketch.Placement.Rotation = App.Rotation(0, 1, 0, 90)
        
        doc.recompute()
        self.created_sketches.append(sketch.Name)
        
        return {
            'sketch_name': sketch.Name,
            'plane': plane,
            'support': support,
            'map_mode': map_mode,
            'geometry_count': 0,
            'constraint_count': 0
        }
    
    def close_sketch(self, sketch_name: str) -> Dict[str, Any]:
        """
        Close/finish a sketch (exit edit mode).
        
        Args:
            sketch_name: Name of the sketch to close
            
        Returns:
            Dictionary with sketch status information
        """
        if not App or not App.ActiveDocument:
            raise RuntimeError("No active FreeCAD document")
        
        doc = App.ActiveDocument
        sketch = doc.getObject(sketch_name)
        
        if not sketch:
            raise ValueError(f"Sketch {sketch_name} not found")
        
        # Attempt to solve constraints
        sketch.solve()
        doc.recompute()
        
        return {
            'sketch_name': sketch_name,
            'status': 'closed',
            'geometry_count': len(sketch.Geometry),
            'constraint_count': len(sketch.Constraints),
            'fully_constrained': self._is_fully_constrained(sketch)
        }
    
    def fully_constrain_sketch(self, sketch_name: str) -> Dict[str, Any]:
        """
        Attempt to fully constrain a sketch automatically.
        
        Args:
            sketch_name: Name of the sketch to constrain
            
        Returns:
            Dictionary with constraint status information
        """
        if not App or not App.ActiveDocument:
            raise RuntimeError("No active FreeCAD document")
        
        doc = App.ActiveDocument
        sketch = doc.getObject(sketch_name)
        
        if not sketch:
            raise ValueError(f"Sketch {sketch_name} not found")
        
        initial_constraints = len(sketch.Constraints)
        
        # Add basic constraints automatically
        added_constraints = []
        
        # Find and add coincident constraints for connected lines
        for i, geom1 in enumerate(sketch.Geometry):
            for j, geom2 in enumerate(sketch.Geometry[i+1:], i+1):
                if self._should_be_coincident(geom1, geom2):
                    try:
                        constraint_id = sketch.addConstraint(
                            Sketcher.Constraint('Coincident', i, 2, j, 1)
                        )
                        added_constraints.append(constraint_id)
                    except Exception:
                        pass  # Constraint might already exist or be invalid
        
        # Add horizontal/vertical constraints for axis-aligned lines
        for i, geom in enumerate(sketch.Geometry):
            if hasattr(geom, 'StartPoint') and hasattr(geom, 'EndPoint'):
                start = geom.StartPoint
                end = geom.EndPoint
                
                # Check if line is horizontal (within tolerance)
                if abs(start.y - end.y) < 0.001:
                    try:
                        constraint_id = sketch.addConstraint(
                            Sketcher.Constraint('Horizontal', i)
                        )
                        added_constraints.append(constraint_id)
                    except Exception:
                        pass
                
                # Check if line is vertical (within tolerance)
                elif abs(start.x - end.x) < 0.001:
                    try:
                        constraint_id = sketch.addConstraint(
                            Sketcher.Constraint('Vertical', i)
                        )
                        added_constraints.append(constraint_id)
                    except Exception:
                        pass
        
        sketch.solve()
        doc.recompute()
        
        final_constraints = len(sketch.Constraints)
        
        return {
            'sketch_name': sketch_name,
            'initial_constraints': initial_constraints,
            'final_constraints': final_constraints,
            'added_constraints': len(added_constraints),
            'fully_constrained': self._is_fully_constrained(sketch),
            'constraint_ids': added_constraints
        }
    
    # ===================================================================
    # BASIC GEOMETRY CREATION
    # ===================================================================
    
    def add_line(self, sketch_name: str, start: Tuple[float, float],
                end: Tuple[float, float], construction: bool = False) -> Dict[str, Any]:
        """
        Add a line to a sketch.
        
        Args:
            sketch_name: Name of the target sketch
            start: Start point (x, y)
            end: End point (x, y)
            construction: Whether this is construction geometry
            
        Returns:
            Dictionary with line creation information
        """
        if not App or not App.ActiveDocument:
            raise RuntimeError("No active FreeCAD document")
        
        doc = App.ActiveDocument
        sketch = doc.getObject(sketch_name)
        
        if not sketch:
            raise ValueError(f"Sketch {sketch_name} not found")
        
        start_point = App.Vector(start[0], start[1], 0)
        end_point = App.Vector(end[0], end[1], 0)
        
        line_id = sketch.addGeometry(Part.LineSegment(start_point, end_point))
        
        if construction:
            sketch.toggleConstruction(line_id)
        
        doc.recompute()
        self.modified_sketches.append(sketch_name)
        
        length = start_point.distanceToPoint(end_point)
        
        return {
            'sketch_name': sketch_name,
            'geometry_id': line_id,
            'geometry_type': 'Line',
            'start_point': start,
            'end_point': end,
            'length': length,
            'construction': construction
        }
    
    def add_rectangle(self, sketch_name: str, corner1: Tuple[float, float],
                     corner2: Tuple[float, float], 
                     construction: bool = False) -> Dict[str, Any]:
        """
        Add a rectangle to a sketch.
        
        Args:
            sketch_name: Name of the target sketch
            corner1: First corner (x, y)
            corner2: Opposite corner (x, y)
            construction: Whether this is construction geometry
            
        Returns:
            Dictionary with rectangle creation information
        """
        if not App or not App.ActiveDocument:
            raise RuntimeError("No active FreeCAD document")
        
        doc = App.ActiveDocument
        sketch = doc.getObject(sketch_name)
        
        if not sketch:
            raise ValueError(f"Sketch {sketch_name} not found")
        
        x1, y1 = corner1
        x2, y2 = corner2
        
        # Create four lines for rectangle
        lines = []
        points = [
            (x1, y1), (x2, y1), (x2, y2), (x1, y2), (x1, y1)
        ]
        
        for i in range(4):
            start = App.Vector(points[i][0], points[i][1], 0)
            end = App.Vector(points[i+1][0], points[i+1][1], 0)
            line_id = sketch.addGeometry(Part.LineSegment(start, end))
            lines.append(line_id)
            
            if construction:
                sketch.toggleConstruction(line_id)
        
        # Add coincident constraints to connect corners
        constraint_ids = []
        for i in range(4):
            next_i = (i + 1) % 4
            constraint_id = sketch.addConstraint(
                Sketcher.Constraint('Coincident', lines[i], 2, lines[next_i], 1)
            )
            constraint_ids.append(constraint_id)
        
        # Add horizontal and vertical constraints
        constraint_ids.append(sketch.addConstraint(
            Sketcher.Constraint('Horizontal', lines[0])
        ))
        constraint_ids.append(sketch.addConstraint(
            Sketcher.Constraint('Horizontal', lines[2])
        ))
        constraint_ids.append(sketch.addConstraint(
            Sketcher.Constraint('Vertical', lines[1])
        ))
        constraint_ids.append(sketch.addConstraint(
            Sketcher.Constraint('Vertical', lines[3])
        ))
        
        doc.recompute()
        self.modified_sketches.append(sketch_name)
        
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        
        return {
            'sketch_name': sketch_name,
            'geometry_ids': lines,
            'constraint_ids': constraint_ids,
            'geometry_type': 'Rectangle',
            'corner1': corner1,
            'corner2': corner2,
            'width': width,
            'height': height,
            'area': width * height,
            'construction': construction
        }
    
    def add_circle(self, sketch_name: str, center: Tuple[float, float],
                  radius: float, construction: bool = False) -> Dict[str, Any]:
        """
        Add a circle to a sketch.
        
        Args:
            sketch_name: Name of the target sketch
            center: Center point (x, y)
            radius: Circle radius
            construction: Whether this is construction geometry
            
        Returns:
            Dictionary with circle creation information
        """
        if not App or not App.ActiveDocument:
            raise RuntimeError("No active FreeCAD document")
        
        doc = App.ActiveDocument
        sketch = doc.getObject(sketch_name)
        
        if not sketch:
            raise ValueError(f"Sketch {sketch_name} not found")
        
        center_point = App.Vector(center[0], center[1], 0)
        circle = Part.Circle(center_point, App.Vector(0, 0, 1), radius)
        
        circle_id = sketch.addGeometry(circle)
        
        if construction:
            sketch.toggleConstruction(circle_id)
        
        doc.recompute()
        self.modified_sketches.append(sketch_name)
        
        return {
            'sketch_name': sketch_name,
            'geometry_id': circle_id,
            'geometry_type': 'Circle',
            'center': center,
            'radius': radius,
            'diameter': radius * 2,
            'circumference': 2 * math.pi * radius,
            'area': math.pi * radius * radius,
            'construction': construction
        }
    
    def add_arc(self, sketch_name: str, center: Tuple[float, float],
               start_angle: float, end_angle: float, radius: float,
               construction: bool = False) -> Dict[str, Any]:
        """
        Add an arc to a sketch.
        
        Args:
            sketch_name: Name of the target sketch
            center: Center point (x, y)
            start_angle: Start angle in degrees
            end_angle: End angle in degrees
            radius: Arc radius
            construction: Whether this is construction geometry
            
        Returns:
            Dictionary with arc creation information
        """
        if not App or not App.ActiveDocument:
            raise RuntimeError("No active FreeCAD document")
        
        doc = App.ActiveDocument
        sketch = doc.getObject(sketch_name)
        
        if not sketch:
            raise ValueError(f"Sketch {sketch_name} not found")
        
        center_point = App.Vector(center[0], center[1], 0)
        
        # Convert angles to radians
        start_rad = math.radians(start_angle)
        end_rad = math.radians(end_angle)
        
        arc = Part.ArcOfCircle(
            Part.Circle(center_point, App.Vector(0, 0, 1), radius),
            start_rad, end_rad
        )
        
        arc_id = sketch.addGeometry(arc)
        
        if construction:
            sketch.toggleConstruction(arc_id)
        
        doc.recompute()
        self.modified_sketches.append(sketch_name)
        
        arc_length = radius * abs(end_rad - start_rad)
        
        return {
            'sketch_name': sketch_name,
            'geometry_id': arc_id,
            'geometry_type': 'Arc',
            'center': center,
            'radius': radius,
            'start_angle': start_angle,
            'end_angle': end_angle,
            'arc_length': arc_length,
            'construction': construction
        }
    
    # ===================================================================
    # CONSTRAINT MANAGEMENT
    # ===================================================================
    
    def add_horizontal_constraint(self, sketch_name: str, 
                                geometry_id: int) -> Dict[str, Any]:
        """
        Add a horizontal constraint to a line.
        
        Args:
            sketch_name: Name of the target sketch
            geometry_id: ID of the geometry to constrain
            
        Returns:
            Dictionary with constraint information
        """
        return self._add_constraint(
            sketch_name, 'Horizontal', [geometry_id]
        )
    
    def add_vertical_constraint(self, sketch_name: str,
                              geometry_id: int) -> Dict[str, Any]:
        """
        Add a vertical constraint to a line.
        
        Args:
            sketch_name: Name of the target sketch
            geometry_id: ID of the geometry to constrain
            
        Returns:
            Dictionary with constraint information
        """
        return self._add_constraint(
            sketch_name, 'Vertical', [geometry_id]
        )
    
    def add_distance_constraint(self, sketch_name: str,
                              geometry_id1: int, point_pos1: int,
                              geometry_id2: int, point_pos2: int,
                              distance: float) -> Dict[str, Any]:
        """
        Add a distance constraint between two points.
        
        Args:
            sketch_name: Name of the target sketch
            geometry_id1: ID of first geometry
            point_pos1: Point position on first geometry (1=start, 2=end, 3=center)
            geometry_id2: ID of second geometry
            point_pos2: Point position on second geometry
            distance: Target distance
            
        Returns:
            Dictionary with constraint information
        """
        if not App or not App.ActiveDocument:
            raise RuntimeError("No active FreeCAD document")
        
        doc = App.ActiveDocument
        sketch = doc.getObject(sketch_name)
        
        if not sketch:
            raise ValueError(f"Sketch {sketch_name} not found")
        
        constraint = Sketcher.Constraint(
            'Distance',
            geometry_id1, point_pos1,
            geometry_id2, point_pos2,
            distance
        )
        
        constraint_id = sketch.addConstraint(constraint)
        sketch.solve()
        doc.recompute()
        
        self.modified_sketches.append(sketch_name)
        
        return {
            'sketch_name': sketch_name,
            'constraint_id': constraint_id,
            'constraint_type': 'Distance',
            'geometry_ids': [geometry_id1, geometry_id2],
            'distance': distance,
            'status': 'added'
        }
    
    def add_radius_constraint(self, sketch_name: str, geometry_id: int,
                            radius: float) -> Dict[str, Any]:
        """
        Add a radius constraint to a circle or arc.
        
        Args:
            sketch_name: Name of the target sketch
            geometry_id: ID of the circle/arc to constrain
            radius: Target radius
            
        Returns:
            Dictionary with constraint information
        """
        if not App or not App.ActiveDocument:
            raise RuntimeError("No active FreeCAD document")
        
        doc = App.ActiveDocument
        sketch = doc.getObject(sketch_name)
        
        if not sketch:
            raise ValueError(f"Sketch {sketch_name} not found")
        
        constraint = Sketcher.Constraint('Radius', geometry_id, radius)
        constraint_id = sketch.addConstraint(constraint)
        sketch.solve()
        doc.recompute()
        
        self.modified_sketches.append(sketch_name)
        
        return {
            'sketch_name': sketch_name,
            'constraint_id': constraint_id,
            'constraint_type': 'Radius',
            'geometry_id': geometry_id,
            'radius': radius,
            'status': 'added'
        }
    
    # ===================================================================
    # UTILITY METHODS
    # ===================================================================
    
    def _add_constraint(self, sketch_name: str, constraint_type: str,
                       geometry_ids: List[int], 
                       value: Optional[float] = None) -> Dict[str, Any]:
        """
        Generic method to add constraints.
        
        Args:
            sketch_name: Name of the target sketch
            constraint_type: Type of constraint
            geometry_ids: List of geometry IDs
            value: Constraint value (for dimensional constraints)
            
        Returns:
            Dictionary with constraint information
        """
        if not App or not App.ActiveDocument:
            raise RuntimeError("No active FreeCAD document")
        
        doc = App.ActiveDocument
        sketch = doc.getObject(sketch_name)
        
        if not sketch:
            raise ValueError(f"Sketch {sketch_name} not found")
        
        # Create constraint based on type and parameters
        if len(geometry_ids) == 1:
            if value is not None:
                constraint = Sketcher.Constraint(
                    constraint_type, geometry_ids[0], value
                )
            else:
                constraint = Sketcher.Constraint(
                    constraint_type, geometry_ids[0]
                )
        elif len(geometry_ids) == 2:
            constraint = Sketcher.Constraint(
                constraint_type, geometry_ids[0], geometry_ids[1]
            )
        else:
            raise ValueError(f"Unsupported constraint configuration for {constraint_type}")
        
        constraint_id = sketch.addConstraint(constraint)
        sketch.solve()
        doc.recompute()
        
        self.modified_sketches.append(sketch_name)
        
        return {
            'sketch_name': sketch_name,
            'constraint_id': constraint_id,
            'constraint_type': constraint_type,
            'geometry_ids': geometry_ids,
            'value': value,
            'status': 'added'
        }
    
    def _is_fully_constrained(self, sketch) -> bool:
        """Check if a sketch is fully constrained."""
        if not sketch:
            return False
        
        try:
            # A sketch is fully constrained if it has no degrees of freedom
            return sketch.getDOF() == 0
        except Exception:
            return False
    
    def _should_be_coincident(self, geom1, geom2) -> bool:
        """
        Check if two geometries should have coincident constraints.
        
        This is a simplified heuristic - in practice, this would be more
        sophisticated and check actual point positions.
        """
        # This is a placeholder implementation
        # Real implementation would check if endpoints are close
        return False
    
    def get_sketch_info(self, sketch_name: str) -> Dict[str, Any]:
        """
        Get comprehensive information about a sketch.
        
        Args:
            sketch_name: Name of the sketch
            
        Returns:
            Dictionary with sketch information
        """
        if not App or not App.ActiveDocument:
            raise RuntimeError("No active FreeCAD document")
        
        doc = App.ActiveDocument
        sketch = doc.getObject(sketch_name)
        
        if not sketch:
            raise ValueError(f"Sketch {sketch_name} not found")
        
        geometry_info = []
        for i, geom in enumerate(sketch.Geometry):
            geom_info = {
                'id': i,
                'type': geom.__class__.__name__,
                'construction': sketch.getConstruction(i)
            }
            
            if hasattr(geom, 'StartPoint'):
                geom_info['start_point'] = (geom.StartPoint.x, geom.StartPoint.y)
            if hasattr(geom, 'EndPoint'):
                geom_info['end_point'] = (geom.EndPoint.x, geom.EndPoint.y)
            if hasattr(geom, 'Center'):
                geom_info['center'] = (geom.Center.x, geom.Center.y)
            if hasattr(geom, 'Radius'):
                geom_info['radius'] = geom.Radius
                
            geometry_info.append(geom_info)
        
        constraint_info = []
        for i, constraint in enumerate(sketch.Constraints):
            constraint_info.append({
                'id': i,
                'type': constraint.Type,
                'value': getattr(constraint, 'Value', None),
                'geometry_refs': [constraint.First, constraint.Second] if hasattr(constraint, 'Second') else [constraint.First]
            })
        
        return {
            'sketch_name': sketch_name,
            'geometry_count': len(sketch.Geometry),
            'constraint_count': len(sketch.Constraints),
            'degrees_of_freedom': sketch.getDOF(),
            'fully_constrained': self._is_fully_constrained(sketch),
            'geometry': geometry_info,
            'constraints': constraint_info
        }
    
    def validate_sketch(self, sketch_name: str) -> Dict[str, Any]:
        """
        Validate a sketch and report any issues.
        
        Args:
            sketch_name: Name of the sketch to validate
            
        Returns:
            Dictionary with validation results
        """
        if not App or not App.ActiveDocument:
            raise RuntimeError("No active FreeCAD document")
        
        doc = App.ActiveDocument
        sketch = doc.getObject(sketch_name)
        
        if not sketch:
            raise ValueError(f"Sketch {sketch_name} not found")
        
        validation_results = {
            'sketch_name': sketch_name,
            'valid': True,
            'warnings': [],
            'errors': [],
            'suggestions': []
        }
        
        # Check degrees of freedom
        dof = sketch.getDOF()
        if dof > 0:
            validation_results['warnings'].append(
                f"Sketch has {dof} degrees of freedom - not fully constrained"
            )
        elif dof < 0:
            validation_results['errors'].append(
                f"Sketch is over-constrained ({abs(dof)} conflicting constraints)"
            )
            validation_results['valid'] = False
        
        # Check for invalid geometry
        for i, geom in enumerate(sketch.Geometry):
            if hasattr(geom, 'isValid') and not geom.isValid():
                validation_results['errors'].append(
                    f"Geometry {i} is invalid"
                )
                validation_results['valid'] = False
        
        # Check for redundant constraints
        try:
            sketch.solve()
        except Exception as e:
            validation_results['errors'].append(
                f"Sketch solve failed: {str(e)}"
            )
            validation_results['valid'] = False
        
        return validation_results
    
    def check_constraints(self, sketch_name: str) -> Dict[str, Any]:
        """
        Analyze constraints in a sketch.
        
        Args:
            sketch_name: Name of the sketch to analyze
            
        Returns:
            Dictionary with constraint analysis
        """
        sketch_info = self.get_sketch_info(sketch_name)
        
        constraint_summary = {}
        for constraint in sketch_info['constraints']:
            constraint_type = constraint['type']
            if constraint_type in constraint_summary:
                constraint_summary[constraint_type] += 1
            else:
                constraint_summary[constraint_type] = 1
        
        return {
            'sketch_name': sketch_name,
            'total_constraints': sketch_info['constraint_count'],
            'constraint_types': constraint_summary,
            'degrees_of_freedom': sketch_info['degrees_of_freedom'],
            'status': 'fully_constrained' if sketch_info['fully_constrained'] else 'under_constrained'
        }
    
    def suggest_constraints(self, sketch_name: str) -> Dict[str, Any]:
        """
        Suggest constraints to improve sketch definition.
        
        Args:
            sketch_name: Name of the sketch to analyze
            
        Returns:
            Dictionary with constraint suggestions
        """
        sketch_info = self.get_sketch_info(sketch_name)
        suggestions = []
        
        # Analyze geometry for potential constraints
        for geom in sketch_info['geometry']:
            if geom['type'] == 'LineSegment':
                # Suggest horizontal/vertical constraints for axis-aligned lines
                if 'start_point' in geom and 'end_point' in geom:
                    start = geom['start_point']
                    end = geom['end_point']
                    
                    if abs(start[1] - end[1]) < 0.001:  # Nearly horizontal
                        suggestions.append({
                            'type': 'horizontal',
                            'geometry_id': geom['id'],
                            'reason': 'Line appears to be horizontal'
                        })
                    elif abs(start[0] - end[0]) < 0.001:  # Nearly vertical
                        suggestions.append({
                            'type': 'vertical', 
                            'geometry_id': geom['id'],
                            'reason': 'Line appears to be vertical'
                        })
        
        return {
            'sketch_name': sketch_name,
            'suggestion_count': len(suggestions),
            'suggestions': suggestions,
            'current_dof': sketch_info['degrees_of_freedom']
        }
    
    # ==================================================================
    # PLACEHOLDER IMPLEMENTATIONS FOR MISSING METHODS
    # ==================================================================
    
    def add_ellipse(self, sketch_name: str, center: Tuple[float, float],
                   major_radius: float, minor_radius: float,
                   construction: bool = False) -> Dict[str, Any]:
        """Placeholder for ellipse creation"""
        return {'status': 'not_implemented', 'operation': 'add_ellipse'}
    
    def add_polygon(self, sketch_name: str, center: Tuple[float, float],
                   radius: float, sides: int = 6,
                   construction: bool = False) -> Dict[str, Any]:
        """Placeholder for polygon creation"""
        return {'status': 'not_implemented', 'operation': 'add_polygon'}
    
    def add_bspline(self, sketch_name: str, points: List[Tuple[float, float]],
                   construction: bool = False) -> Dict[str, Any]:
        """Placeholder for B-spline creation"""
        return {'status': 'not_implemented', 'operation': 'add_bspline'}
    
    def add_slot(self, sketch_name: str, start: Tuple[float, float],
                end: Tuple[float, float], width: float,
                construction: bool = False) -> Dict[str, Any]:
        """Placeholder for slot creation"""
        return {'status': 'not_implemented', 'operation': 'add_slot'}
    
    def add_sketch_fillet(self, sketch_name: str, geometry_id1: int,
                         geometry_id2: int, radius: float) -> Dict[str, Any]:
        """Placeholder for sketch fillet"""
        return {'status': 'not_implemented', 'operation': 'add_sketch_fillet'}
    
    def add_sketch_chamfer(self, sketch_name: str, geometry_id1: int,
                          geometry_id2: int, size: float) -> Dict[str, Any]:
        """Placeholder for sketch chamfer"""
        return {'status': 'not_implemented', 'operation': 'add_sketch_chamfer'}
    
    def add_parallel_constraint(self, sketch_name: str, geometry_id1: int,
                               geometry_id2: int) -> Dict[str, Any]:
        """Placeholder for parallel constraint"""
        return self._add_constraint(sketch_name, 'Parallel', [geometry_id1, geometry_id2])
    
    def add_perpendicular_constraint(self, sketch_name: str, geometry_id1: int,
                                    geometry_id2: int) -> Dict[str, Any]:
        """Placeholder for perpendicular constraint"""
        return self._add_constraint(sketch_name, 'Perpendicular', [geometry_id1, geometry_id2])
    
    def add_tangent_constraint(self, sketch_name: str, geometry_id1: int,
                              geometry_id2: int) -> Dict[str, Any]:
        """Placeholder for tangent constraint"""
        return self._add_constraint(sketch_name, 'Tangent', [geometry_id1, geometry_id2])
    
    def add_equal_constraint(self, sketch_name: str, geometry_id1: int,
                            geometry_id2: int) -> Dict[str, Any]:
        """Placeholder for equal constraint"""
        return self._add_constraint(sketch_name, 'Equal', [geometry_id1, geometry_id2])
    
    def add_coincident_constraint(self, sketch_name: str, geometry_id1: int,
                                 point_pos1: int, geometry_id2: int,
                                 point_pos2: int) -> Dict[str, Any]:
        """Placeholder for coincident constraint"""
        # This would need more complex implementation
        return {'status': 'not_implemented', 'operation': 'add_coincident_constraint'}
    
    def add_diameter_constraint(self, sketch_name: str, geometry_id: int,
                               diameter: float) -> Dict[str, Any]:
        """Placeholder for diameter constraint"""
        return self._add_constraint(sketch_name, 'Diameter', [geometry_id], diameter)
    
    def add_angle_constraint(self, sketch_name: str, geometry_id1: int,
                            geometry_id2: int, angle: float) -> Dict[str, Any]:
        """Placeholder for angle constraint"""
        # This would need more complex implementation
        return {'status': 'not_implemented', 'operation': 'add_angle_constraint'}
    
    def add_symmetric_constraint(self, sketch_name: str, geometry_id1: int,
                                geometry_id2: int, symmetry_line_id: int) -> Dict[str, Any]:
        """Placeholder for symmetric constraint"""
        return {'status': 'not_implemented', 'operation': 'add_symmetric_constraint'}
    
    def create_rectangular_pattern(self, sketch_name: str, geometry_ids: List[int],
                                  rows: int, cols: int, row_spacing: float,
                                  col_spacing: float) -> Dict[str, Any]:
        """Placeholder for rectangular pattern"""
        return {'status': 'not_implemented', 'operation': 'create_rectangular_pattern'}
    
    def create_polar_pattern(self, sketch_name: str, geometry_ids: List[int],
                            center: Tuple[float, float], count: int,
                            angle: float) -> Dict[str, Any]:
        """Placeholder for polar pattern"""
        return {'status': 'not_implemented', 'operation': 'create_polar_pattern'}
    
    def create_linear_pattern(self, sketch_name: str, geometry_ids: List[int],
                             direction: Tuple[float, float], count: int,
                             spacing: float) -> Dict[str, Any]:
        """Placeholder for linear pattern"""
        return {'status': 'not_implemented', 'operation': 'create_linear_pattern'}
    
    def add_point(self, sketch_name: str, position: Tuple[float, float],
                 construction: bool = False) -> Dict[str, Any]:
        """
        Add a point to a sketch.
        
        Args:
            sketch_name: Name of the target sketch
            position: Point position (x, y)
            construction: Whether this is construction geometry
            
        Returns:
            Dictionary with point creation information
        """
        if not App or not App.ActiveDocument:
            raise RuntimeError("No active FreeCAD document")
        
        doc = App.ActiveDocument
        sketch = doc.getObject(sketch_name)
        
        if not sketch:
            raise ValueError(f"Sketch {sketch_name} not found")
        
        point_vector = App.Vector(position[0], position[1], 0)
        point = Part.Point(point_vector)
        
        point_id = sketch.addGeometry(point)
        
        if construction:
            sketch.toggleConstruction(point_id)
        
        doc.recompute()
        self.modified_sketches.append(sketch_name)
        
        return {
            'sketch_name': sketch_name,
            'geometry_id': point_id,
            'geometry_type': 'Point',
            'position': position,
            'construction': construction
        }
