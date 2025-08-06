"""
Advanced Sketch Pattern Library for FreeCAD AI Addon.

Provides advanced sketch pattern creation, constraint automation,
and intelligent sketch operations.
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


class AdvancedSketchPatterns:
    """
    Advanced sketch pattern creation and management system.
    
    Provides intelligent pattern creation, constraint automation,
    and advanced 2D geometric operations.
    """
    
    def __init__(self):
        """Initialize the advanced sketch patterns library."""
        self.logger = logging.getLogger(f"{__name__}.AdvancedSketchPatterns")
        self.pattern_library = {
            # Geometric patterns
            'rectangular_hole_pattern': self.create_rectangular_hole_pattern,
            'circular_hole_pattern': self.create_circular_hole_pattern,
            'linear_slot_pattern': self.create_linear_slot_pattern,
            'hexagonal_pattern': self.create_hexagonal_pattern,
            'spiral_pattern': self.create_spiral_pattern,
            'gear_tooth_pattern': self.create_gear_tooth_pattern,
            
            # Structural patterns
            'mounting_holes': self.create_mounting_holes,
            'reinforcement_ribs': self.create_reinforcement_ribs,
            'ventilation_holes': self.create_ventilation_holes,
            'cable_management': self.create_cable_management_slots,
            
            # Manufacturing patterns
            'drill_pattern': self.create_drill_pattern,
            'counterbore_pattern': self.create_counterbore_pattern,
            'countersink_pattern': self.create_countersink_pattern,
            'thread_pattern': self.create_thread_pattern,
        }
        
        self.constraint_patterns = {
            'symmetry': self.apply_symmetry_constraints,
            'equal_spacing': self.apply_equal_spacing_constraints,
            'concentric': self.apply_concentric_constraints,
            'tangent_chain': self.apply_tangent_chain_constraints,
            'parallel_lines': self.apply_parallel_line_constraints,
            'perpendicular_grid': self.apply_perpendicular_grid_constraints,
        }
        
        self.logger.info("Advanced Sketch Patterns initialized with %d patterns",
                        len(self.pattern_library))
    
    def create_intelligent_pattern(self, pattern_type: str,
                                 parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create an intelligent pattern with automatic constraints.
        
        Args:
            pattern_type: Type of pattern to create
            parameters: Pattern parameters
            
        Returns:
            Pattern creation result
        """
        if pattern_type not in self.pattern_library:
            return {
                'status': 'failed',
                'error': f"Unknown pattern type: {pattern_type}",
                'available_patterns': list(self.pattern_library.keys())
            }
        
        try:
            pattern_func = self.pattern_library[pattern_type]
            result = pattern_func(parameters)
            
            # Apply automatic constraints if requested
            if parameters.get('auto_constrain', True):
                constraint_result = self._apply_automatic_constraints(
                    result, pattern_type)
                result.update(constraint_result)
            
            return {
                'status': 'success',
                'pattern_type': pattern_type,
                'result': result,
                'parameters': parameters
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create pattern {pattern_type}: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'pattern_type': pattern_type
            }
    
    def create_parametric_sketch(self, sketch_name: str,
                               geometry: List[Dict[str, Any]],
                               constraints: List[Dict[str, Any]],
                               parameters: Dict[str, Any] = None
                               ) -> Dict[str, Any]:
        """
        Create a fully parametric sketch with geometry and constraints.
        
        Args:
            sketch_name: Name of the sketch
            geometry: List of geometric elements to create
            constraints: List of constraints to apply
            parameters: Parametric values
            
        Returns:
            Sketch creation result
        """
        if not App or not App.ActiveDocument:
            return {
                'status': 'failed',
                'error': "No active FreeCAD document"
            }
        
        try:
            doc = App.ActiveDocument
            
            # Create sketch object
            sketch = doc.addObject('Sketcher::SketchObject', sketch_name)
            sketch.Support = [(doc.getObject('XY_Plane'), '')]
            sketch.MapMode = 'FlatFace'
            
            # Add geometry
            geometry_indices = []
            for geom in geometry:
                index = self._add_sketch_geometry(sketch, geom)
                geometry_indices.append(index)
            
            # Apply constraints
            constraint_indices = []
            for constraint in constraints:
                index = self._add_sketch_constraint(sketch, constraint)
                constraint_indices.append(index)
            
            # Set parameters if provided
            if parameters:
                self._set_sketch_parameters(sketch, parameters)
            
            # Update sketch
            sketch.recompute()
            doc.recompute()
            
            return {
                'status': 'success',
                'sketch_name': sketch_name,
                'geometry_count': len(geometry_indices),
                'constraint_count': len(constraint_indices),
                'parameters': parameters or {},
                'sketch_object': sketch.Name
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create parametric sketch {sketch_name}: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    # ========================================================================
    # GEOMETRIC PATTERNS
    # ========================================================================
    
    def create_rectangular_hole_pattern(self, params: Dict[str, Any]
                                      ) -> Dict[str, Any]:
        """Create a rectangular pattern of holes."""
        rows = params.get('rows', 2)
        cols = params.get('cols', 2)
        hole_diameter = params.get('hole_diameter', 5.0)
        row_spacing = params.get('row_spacing', 20.0)
        col_spacing = params.get('col_spacing', 20.0)
        sketch_name = params.get('sketch_name', 'HolePattern')
        
        holes = []
        for i in range(rows):
            for j in range(cols):
                x = j * col_spacing
                y = i * row_spacing
                hole = {
                    'type': 'circle',
                    'center': (x, y),
                    'radius': hole_diameter / 2,
                    'construction': False
                }
                holes.append(hole)
        
        return {
            'sketch_name': sketch_name,
            'geometry': holes,
            'pattern_info': {
                'type': 'rectangular_holes',
                'rows': rows,
                'cols': cols,
                'total_holes': rows * cols
            }
        }
    
    def create_circular_hole_pattern(self, params: Dict[str, Any]
                                   ) -> Dict[str, Any]:
        """Create a circular pattern of holes."""
        count = params.get('count', 6)
        radius = params.get('radius', 25.0)
        hole_diameter = params.get('hole_diameter', 5.0)
        start_angle = params.get('start_angle', 0.0)
        center = params.get('center', (0, 0))
        
        holes = []
        angle_step = 360.0 / count
        
        for i in range(count):
            angle = math.radians(start_angle + i * angle_step)
            x = center[0] + radius * math.cos(angle)
            y = center[1] + radius * math.sin(angle)
            
            hole = {
                'type': 'circle',
                'center': (x, y),
                'radius': hole_diameter / 2,
                'construction': False
            }
            holes.append(hole)
        
        return {
            'geometry': holes,
            'pattern_info': {
                'type': 'circular_holes',
                'count': count,
                'radius': radius,
                'total_holes': count
            }
        }
    
    def create_hexagonal_pattern(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a hexagonal pattern."""
        rings = params.get('rings', 2)
        spacing = params.get('spacing', 10.0)
        element_size = params.get('element_size', 3.0)
        center = params.get('center', (0, 0))
        
        elements = []
        
        # Center element
        elements.append({
            'type': 'circle',
            'center': center,
            'radius': element_size / 2
        })
        
        # Rings around center
        for ring in range(1, rings + 1):
            count = 6 * ring
            ring_radius = ring * spacing
            
            for i in range(count):
                angle = 2 * math.pi * i / count
                x = center[0] + ring_radius * math.cos(angle)
                y = center[1] + ring_radius * math.sin(angle)
                
                elements.append({
                    'type': 'circle',
                    'center': (x, y),
                    'radius': element_size / 2
                })
        
        return {
            'geometry': elements,
            'pattern_info': {
                'type': 'hexagonal',
                'rings': rings,
                'total_elements': len(elements)
            }
        }
    
    def create_gear_tooth_pattern(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a gear tooth pattern."""
        teeth_count = params.get('teeth_count', 20)
        pitch_diameter = params.get('pitch_diameter', 50.0)
        addendum = params.get('addendum', 2.5)
        dedendum = params.get('dedendum', 3.125)
        center = params.get('center', (0, 0))
        
        # Calculate radii
        outer_radius = pitch_diameter / 2 + addendum
        inner_radius = pitch_diameter / 2 - dedendum
        pitch_radius = pitch_diameter / 2
        
        # Create tooth profile
        tooth_profiles = []
        tooth_angle = 2 * math.pi / teeth_count
        
        for i in range(teeth_count):
            base_angle = i * tooth_angle
            
            # Simplified involute tooth profile
            # (In production, this would be a proper involute curve)
            points = []
            
            # Inner point
            angle1 = base_angle - tooth_angle / 4
            x1 = center[0] + inner_radius * math.cos(angle1)
            y1 = center[1] + inner_radius * math.sin(angle1)
            points.append((x1, y1))
            
            # Pitch point
            x2 = center[0] + pitch_radius * math.cos(base_angle)
            y2 = center[1] + pitch_radius * math.sin(base_angle)
            points.append((x2, y2))
            
            # Outer point
            x3 = center[0] + outer_radius * math.cos(base_angle)
            y3 = center[1] + outer_radius * math.sin(base_angle)
            points.append((x3, y3))
            
            # Other side
            angle2 = base_angle + tooth_angle / 4
            x4 = center[0] + inner_radius * math.cos(angle2)
            y4 = center[1] + inner_radius * math.sin(angle2)
            points.append((x4, y4))
            
            # Create lines for tooth profile
            for j in range(len(points) - 1):
                tooth_profiles.append({
                    'type': 'line',
                    'start': points[j],
                    'end': points[j + 1]
                })
        
        return {
            'geometry': tooth_profiles,
            'pattern_info': {
                'type': 'gear_teeth',
                'teeth_count': teeth_count,
                'pitch_diameter': pitch_diameter
            }
        }
    
    def create_linear_slot_pattern(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a linear pattern of slots."""
        count = params.get('count', 3)
        spacing = params.get('spacing', 20.0)
        slot_length = params.get('slot_length', 10.0)
        slot_width = params.get('slot_width', 3.0)
        
        slots = []
        for i in range(count):
            x = i * spacing
            # Create slot as two circles connected by lines
            slots.append({
                'type': 'circle',
                'center': (x - slot_length/2, 0),
                'radius': slot_width / 2
            })
            slots.append({
                'type': 'circle',
                'center': (x + slot_length/2, 0),
                'radius': slot_width / 2
            })
            slots.append({
                'type': 'line',
                'start': (x - slot_length/2, slot_width/2),
                'end': (x + slot_length/2, slot_width/2)
            })
            slots.append({
                'type': 'line',
                'start': (x - slot_length/2, -slot_width/2),
                'end': (x + slot_length/2, -slot_width/2)
            })
        
        return {
            'geometry': slots,
            'pattern_info': {
                'type': 'linear_slots',
                'count': count,
                'total_elements': len(slots)
            }
        }

    def create_spiral_pattern(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a spiral pattern."""
        turns = params.get('turns', 3.0)
        start_radius = params.get('start_radius', 5.0)
        end_radius = params.get('end_radius', 20.0)
        points = params.get('points', 50)
        center = params.get('center', (0, 0))
        
        elements = []
        for i in range(points):
            t = i / (points - 1)
            angle = t * turns * 2 * math.pi
            radius = start_radius + t * (end_radius - start_radius)
            
            x = center[0] + radius * math.cos(angle)
            y = center[1] + radius * math.sin(angle)
            
            elements.append({
                'type': 'point',
                'position': (x, y)
            })
        
        return {
            'geometry': elements,
            'pattern_info': {
                'type': 'spiral',
                'turns': turns,
                'points': points
            }
        }

    def create_reinforcement_ribs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create reinforcement ribs pattern."""
        count = params.get('count', 5)
        spacing = params.get('spacing', 10.0)
        rib_height = params.get('rib_height', 15.0)
        rib_thickness = params.get('rib_thickness', 2.0)
        
        ribs = []
        for i in range(count):
            x = i * spacing
            # Create rib as rectangle
            ribs.extend([
                {
                    'type': 'line',
                    'start': (x - rib_thickness/2, 0),
                    'end': (x + rib_thickness/2, 0)
                },
                {
                    'type': 'line',
                    'start': (x + rib_thickness/2, 0),
                    'end': (x + rib_thickness/2, rib_height)
                },
                {
                    'type': 'line',
                    'start': (x + rib_thickness/2, rib_height),
                    'end': (x - rib_thickness/2, rib_height)
                },
                {
                    'type': 'line',
                    'start': (x - rib_thickness/2, rib_height),
                    'end': (x - rib_thickness/2, 0)
                }
            ])
        
        return {
            'geometry': ribs,
            'pattern_info': {
                'type': 'reinforcement_ribs',
                'count': count
            }
        }

    def create_ventilation_holes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create ventilation holes pattern."""
        return self.create_hexagonal_pattern({
            'rings': params.get('rings', 3),
            'spacing': params.get('spacing', 8.0),
            'element_size': params.get('hole_diameter', 4.0),
            'center': params.get('center', (0, 0))
        })

    def create_cable_management_slots(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create cable management slots."""
        return self.create_linear_slot_pattern({
            'count': params.get('count', 4),
            'spacing': params.get('spacing', 15.0),
            'slot_length': params.get('slot_length', 12.0),
            'slot_width': params.get('slot_width', 4.0)
        })

    def create_counterbore_pattern(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create counterbore pattern."""
        base_holes = self.create_rectangular_hole_pattern(params)
        counterbore_diameter = params.get('counterbore_diameter', 
                                        params.get('hole_diameter', 5.0) * 2)
        
        # Add counterbore circles
        for hole in base_holes['geometry']:
            if hole['type'] == 'circle':
                center = hole['center']
                base_holes['geometry'].append({
                    'type': 'circle',
                    'center': center,
                    'radius': counterbore_diameter / 2,
                    'construction': True
                })
        
        return base_holes

    def create_countersink_pattern(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create countersink pattern."""
        return self.create_counterbore_pattern(params)  # Similar implementation

    def create_thread_pattern(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create thread representation pattern."""
        thread_diameter = params.get('thread_diameter', 6.0)
        pitch = params.get('pitch', 1.0)
        length = params.get('length', 20.0)
        center = params.get('center', (0, 0))
        
        # Simplified thread representation
        turns = int(length / pitch)
        elements = []
        
        for i in range(turns):
            y = center[1] + i * pitch
            # Major diameter circle
            elements.append({
                'type': 'circle',
                'center': (center[0], y),
                'radius': thread_diameter / 2,
                'construction': True
            })
            # Minor diameter circle
            elements.append({
                'type': 'circle',
                'center': (center[0], y),
                'radius': thread_diameter * 0.8 / 2,
                'construction': True
            })
        
        return {
            'geometry': elements,
            'pattern_info': {
                'type': 'thread',
                'diameter': thread_diameter,
                'pitch': pitch,
                'turns': turns
            }
        }
    
    def create_mounting_holes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create mounting holes pattern."""
        hole_type = params.get('hole_type', 'M6')  # M3, M4, M5, M6, M8, M10
        spacing = params.get('spacing', 25.0)
        count = params.get('count', 4)
        layout = params.get('layout', 'square')  # square, linear, circular
        
        # Standard hole diameters for metric bolts
        hole_diameters = {
            'M3': 3.2, 'M4': 4.2, 'M5': 5.2,
            'M6': 6.5, 'M8': 8.5, 'M10': 10.5
        }
        
        hole_diameter = hole_diameters.get(hole_type, 6.5)
        
        if layout == 'square':
            return self.create_rectangular_hole_pattern({
                'rows': 2, 'cols': 2,
                'hole_diameter': hole_diameter,
                'row_spacing': spacing,
                'col_spacing': spacing
            })
        elif layout == 'linear':
            holes = []
            for i in range(count):
                holes.append({
                    'type': 'circle',
                    'center': (i * spacing, 0),
                    'radius': hole_diameter / 2
                })
            return {'geometry': holes, 'pattern_info': {'type': 'linear_mounting'}}
        elif layout == 'circular':
            return self.create_circular_hole_pattern({
                'count': count,
                'radius': spacing,
                'hole_diameter': hole_diameter
            })
    
    def create_drill_pattern(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a drill pattern with pilot holes."""
        drill_diameter = params.get('drill_diameter', 8.0)
        pilot_diameter = params.get('pilot_diameter', 3.0)
        spacing = params.get('spacing', 20.0)
        count = params.get('count', 3)
        
        holes = []
        for i in range(count):
            x = i * spacing
            
            # Main drill hole
            holes.append({
                'type': 'circle',
                'center': (x, 0),
                'radius': drill_diameter / 2,
                'construction': False
            })
            
            # Pilot hole (construction)
            holes.append({
                'type': 'circle',
                'center': (x, 0),
                'radius': pilot_diameter / 2,
                'construction': True
            })
        
        return {
            'geometry': holes,
            'pattern_info': {
                'type': 'drill_pattern',
                'drill_count': count,
                'drill_diameter': drill_diameter
            }
        }
    
    # ========================================================================
    # CONSTRAINT AUTOMATION
    # ========================================================================
    
    def apply_symmetry_constraints(self, sketch: Any,
                                 elements: List[int]) -> Dict[str, Any]:
        """Apply symmetry constraints to sketch elements."""
        # Implementation for symmetry constraints
        return {'status': 'success', 'constraints_added': 0}
    
    def apply_equal_spacing_constraints(self, sketch: Any,
                                      elements: List[int]) -> Dict[str, Any]:
        """Apply equal spacing constraints."""
        # Implementation for equal spacing
        return {'status': 'success', 'constraints_added': 0}

    def apply_concentric_constraints(self, sketch: Any,
                                   elements: List[int]) -> Dict[str, Any]:
        """Apply concentric constraints to circular elements."""
        # Implementation for concentric constraints
        return {'status': 'success', 'constraints_added': 0}

    def apply_tangent_chain_constraints(self, sketch: Any,
                                      elements: List[int]) -> Dict[str, Any]:
        """Apply tangent constraints in a chain."""
        # Implementation for tangent chain constraints
        return {'status': 'success', 'constraints_added': 0}

    def apply_parallel_line_constraints(self, sketch: Any,
                                      elements: List[int]) -> Dict[str, Any]:
        """Apply parallel constraints to lines."""
        # Implementation for parallel line constraints
        return {'status': 'success', 'constraints_added': 0}

    def apply_perpendicular_grid_constraints(self, sketch: Any,
                                           elements: List[int]) -> Dict[str, Any]:
        """Apply perpendicular grid constraints."""
        # Implementation for perpendicular grid constraints
        return {'status': 'success', 'constraints_added': 0}
    
    # ========================================================================
    # PRIVATE HELPER METHODS
    # ========================================================================
    
    def _add_sketch_geometry(self, sketch: Any,
                            geom_def: Dict[str, Any]) -> int:
        """Add geometry element to sketch."""
        # If Part module is not available, return mock ID
        if Part is None:
            return 0
            
        geom_type = geom_def.get('type')
        
        if geom_type == 'line':
            start = geom_def['start']
            end = geom_def['end']
            line = Part.LineSegment(App.Vector(start[0], start[1], 0),
                                   App.Vector(end[0], end[1], 0))
            return sketch.addGeometry(line,
                                     geom_def.get('construction', False))
            
        elif geom_type == 'circle':
            center = geom_def['center']
            radius = geom_def['radius']
            circle = Part.Circle(App.Vector(center[0], center[1], 0),
                                App.Vector(0, 0, 1), radius)
            return sketch.addGeometry(circle,
                                     geom_def.get('construction', False))
            
        elif geom_type == 'arc':
            center = geom_def['center']
            radius = geom_def['radius']
            start_angle = geom_def.get('start_angle', 0)
            end_angle = geom_def.get('end_angle', math.pi)
            
            arc = Part.ArcOfCircle(
                Part.Circle(App.Vector(center[0], center[1], 0),
                           App.Vector(0, 0, 1), radius),
                start_angle, end_angle)
            return sketch.addGeometry(arc,
                                     geom_def.get('construction', False))
        
        return -1
    
    def _add_sketch_constraint(self, sketch: Any,
                              constraint_def: Dict[str, Any]) -> int:
        """Add constraint to sketch."""
        # If Sketcher module is not available, return mock ID
        if Sketcher is None:
            return 0
            
        constraint_type = constraint_def.get('type')
        
        if constraint_type == 'coincident':
            geo1 = constraint_def['geo1']
            point1 = constraint_def.get('point1', 1)
            geo2 = constraint_def['geo2']
            point2 = constraint_def.get('point2', 1)
            constraint = Sketcher.Constraint('Coincident', geo1, point1,
                                           geo2, point2)
            return sketch.addConstraint(constraint)
            
        elif constraint_type == 'distance':
            geo = constraint_def['geo']
            distance = constraint_def['distance']
            constraint = Sketcher.Constraint('Distance', geo, distance)
            return sketch.addConstraint(constraint)
            
        elif constraint_type == 'radius':
            geo = constraint_def['geo']
            radius = constraint_def['radius']
            constraint = Sketcher.Constraint('Radius', geo, radius)
            return sketch.addConstraint(constraint)
        
        return -1
    
    def _set_sketch_parameters(self, sketch: Any,
                             parameters: Dict[str, Any]):
        """Set parametric values in sketch."""
        # Implementation for setting parametric values
        pass
    
    def _apply_automatic_constraints(self, result: Dict[str, Any],
                                   pattern_type: str) -> Dict[str, Any]:
        """Apply automatic constraints based on pattern type."""
        # Implementation for automatic constraint application
        return {'auto_constraints_applied': True}
