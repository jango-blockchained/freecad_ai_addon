"""
Analysis Action Library for FreeCAD AI Addon.

Comprehensive library for geometric analysis, validation, measurement,
and design optimization operations.
"""

from typing import Dict, Any, List, Tuple
import logging
import math

try:
    import FreeCAD as App
    import FreeCADGui as Gui
    import Part
    import Mesh
    import MeshPart
except ImportError:
    # Mock for testing outside FreeCAD
    App = None
    Gui = None
    Part = None
    Mesh = None
    MeshPart = None

logger = logging.getLogger(__name__)


class AnalysisActionLibrary:
    """
    Comprehensive analysis action library for FreeCAD operations.
    
    Provides analysis, validation, measurement, and optimization
    capabilities for CAD objects and designs.
    """
    
    def __init__(self):
        """Initialize the analysis action library"""
        self.logger = logging.getLogger(f"{__name__}.AnalysisActionLibrary")
        self.analysis_history = []
        
        # Analysis operation registry
        self.analysis_operations = {
            # Geometric analysis
            'geometric_properties': self.analyze_geometric_properties,
            'mass_properties': self.analyze_mass_properties,
            'bounding_analysis': self.analyze_bounding_geometry,
            'surface_analysis': self.analyze_surface_properties,
            'volume_analysis': self.analyze_volume_properties,
            'cross_section_analysis': self.analyze_cross_section,
            
            # Validation and checking
            'validate_geometry': self.validate_geometry,
            'check_intersections': self.check_object_intersections,
            'check_self_intersections': self.check_self_intersections,
            'topology_check': self.check_topology,
            'watertight_check': self.check_watertight,
            
            # Manufacturing analysis
            'printability_analysis': self.analyze_3d_printability,
            'draft_angle_analysis': self.analyze_draft_angles,
            'undercut_analysis': self.analyze_undercuts,
            'wall_thickness_analysis': self.analyze_wall_thickness,
            'support_analysis': self.analyze_support_requirements,
            'overhang_analysis': self.analyze_overhangs,
            
            # Structural analysis
            'stress_concentration_analysis': self.analyze_stress_concentration,
            'moment_of_inertia': self.calculate_moment_of_inertia,
            'section_properties': self.analyze_section_properties,
            
            # Measurement operations
            'measure_distance': self.measure_distance,
            'measure_angle': self.measure_angle,
            'measure_curvature': self.measure_curvature,
            'measure_deviation': self.measure_surface_deviation,
            
            # Comparison operations
            'compare_geometries': self.compare_two_geometries,
            'compare_volumes': self.compare_volumes,
            'compare_surfaces': self.compare_surface_areas,
            
            # Quality assessment
            'mesh_quality_analysis': self.analyze_mesh_quality,
            'surface_quality_analysis': self.analyze_surface_quality,
            'design_complexity_analysis': self.analyze_design_complexity,
        }
        
        self.logger.info("Analysis Action Library initialized with %d operations",
                        len(self.analysis_operations))
    
    def execute_analysis(self, operation: str, 
                        parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a named analysis operation with parameters.
        
        Args:
            operation: Name of the analysis operation
            parameters: Dictionary of parameters
            
        Returns:
            Result dictionary with analysis results
        """
        if operation not in self.analysis_operations:
            return {
                'status': 'failed',
                'error': f"Unknown analysis operation: {operation}",
                'available_operations': list(self.analysis_operations.keys())
            }
        
        try:
            operation_func = self.analysis_operations[operation]
            result = operation_func(**parameters)
            
            # Record in history
            self.analysis_history.append({
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
            self.logger.error(f"Analysis operation {operation} failed: {str(e)}")
            return {
                'status': 'failed',
                'operation': operation,
                'error': str(e),
                'parameters': parameters
            }
    
    # ==================================================================
    # GEOMETRIC ANALYSIS
    # ==================================================================
    
    def analyze_geometric_properties(self, obj_name: str) -> Dict[str, Any]:
        """
        Analyze comprehensive geometric properties of an object.
        
        Args:
            obj_name: Name of the object to analyze
            
        Returns:
            Dictionary with geometric properties
        """
        if not App or not App.ActiveDocument:
            raise RuntimeError("No active FreeCAD document")
        
        obj = App.ActiveDocument.getObject(obj_name)
        if not obj or not hasattr(obj, 'Shape'):
            raise ValueError(f"Object {obj_name} not found or has no shape")
        
        shape = obj.Shape
        
        # Basic geometric properties
        properties = {
            'object_name': obj_name,
            'volume': shape.Volume,
            'surface_area': shape.Area,
            'center_of_mass': {
                'x': shape.CenterOfMass.x,
                'y': shape.CenterOfMass.y,
                'z': shape.CenterOfMass.z
            },
            'bounding_box': self._get_bounding_box_dict(shape.BoundBox),
            'edge_count': len(shape.Edges),
            'face_count': len(shape.Faces),
            'vertex_count': len(shape.Vertexes),
            'solid_count': len(shape.Solids),
            'shell_count': len(shape.Shells),
            'wire_count': len(shape.Wires)
        }
        
        # Additional geometric characteristics
        if shape.Volume > 0:
            bbox = shape.BoundBox
            properties['compactness'] = (shape.Volume / 
                                       (bbox.XLength * bbox.YLength * bbox.ZLength))
            properties['sphericity'] = ((math.pi ** (1/3)) * 
                                      ((6 * shape.Volume) ** (2/3)) / shape.Area)
        
        # Surface-to-volume ratio
        if shape.Volume > 0:
            properties['surface_to_volume_ratio'] = shape.Area / shape.Volume
        
        return properties
    
    def analyze_mass_properties(self, obj_name: str, 
                               density: float = 1.0,
                               material: str = "Generic") -> Dict[str, Any]:
        """
        Analyze mass properties of an object.
        
        Args:
            obj_name: Name of the object to analyze
            density: Material density (g/cm³)
            material: Material name
            
        Returns:
            Dictionary with mass properties
        """
        if not App or not App.ActiveDocument:
            raise RuntimeError("No active FreeCAD document")
        
        obj = App.ActiveDocument.getObject(obj_name)
        if not obj or not hasattr(obj, 'Shape'):
            raise ValueError(f"Object {obj_name} not found or has no shape")
        
        shape = obj.Shape
        
        # Volume in mm³, convert to cm³ for mass calculation
        volume_cm3 = shape.Volume / 1000.0
        mass_g = volume_cm3 * density
        
        # Center of mass
        com = shape.CenterOfMass
        
        # Moments of inertia (simplified calculation)
        # This is a basic implementation - real calculation would be more complex
        bbox = shape.BoundBox
        
        # Approximation using bounding box for moment of inertia
        width = bbox.XLength / 10.0  # Convert to cm
        height = bbox.YLength / 10.0
        depth = bbox.ZLength / 10.0
        
        # Moments of inertia for a rectangular solid (approximation)
        ixx = (mass_g / 12.0) * (height**2 + depth**2)
        iyy = (mass_g / 12.0) * (width**2 + depth**2)
        izz = (mass_g / 12.0) * (width**2 + height**2)
        
        return {
            'object_name': obj_name,
            'material': material,
            'density': density,
            'volume_mm3': shape.Volume,
            'volume_cm3': volume_cm3,
            'mass_g': mass_g,
            'mass_kg': mass_g / 1000.0,
            'center_of_mass': {
                'x': com.x,
                'y': com.y,
                'z': com.z
            },
            'moments_of_inertia': {
                'ixx': ixx,
                'iyy': iyy,
                'izz': izz,
                'units': 'g⋅cm²'
            }
        }
    
    def analyze_bounding_geometry(self, obj_name: str) -> Dict[str, Any]:
        """
        Analyze bounding geometry and spatial characteristics.
        
        Args:
            obj_name: Name of the object to analyze
            
        Returns:
            Dictionary with bounding analysis
        """
        if not App or not App.ActiveDocument:
            raise RuntimeError("No active FreeCAD document")
        
        obj = App.ActiveDocument.getObject(obj_name)
        if not obj or not hasattr(obj, 'Shape'):
            raise ValueError(f"Object {obj_name} not found or has no shape")
        
        shape = obj.Shape
        bbox = shape.BoundBox
        
        # Analyze bounding box characteristics
        dimensions = [bbox.XLength, bbox.YLength, bbox.ZLength]
        dimensions.sort(reverse=True)
        
        max_dim = dimensions[0]
        mid_dim = dimensions[1]
        min_dim = dimensions[2]
        
        # Aspect ratios
        aspect_ratio_primary = max_dim / mid_dim if mid_dim > 0 else float('inf')
        aspect_ratio_secondary = mid_dim / min_dim if min_dim > 0 else float('inf')
        
        # Shape classification based on aspect ratios
        if aspect_ratio_primary < 1.5 and aspect_ratio_secondary < 1.5:
            shape_class = "cubic"
        elif aspect_ratio_primary < 2.0:
            shape_class = "rectangular"
        elif min_dim < max_dim * 0.1:
            shape_class = "plate-like"
        elif mid_dim < max_dim * 0.1:
            shape_class = "rod-like"
        else:
            shape_class = "elongated"
        
        return {
            'object_name': obj_name,
            'bounding_box': self._get_bounding_box_dict(bbox),
            'dimensions': {
                'maximum': max_dim,
                'middle': mid_dim,
                'minimum': min_dim
            },
            'aspect_ratios': {
                'primary': aspect_ratio_primary,
                'secondary': aspect_ratio_secondary
            },
            'shape_classification': shape_class,
            'volume_efficiency': shape.Volume / (bbox.XLength * bbox.YLength * bbox.ZLength)
        }
    
    # ==================================================================
    # MANUFACTURING ANALYSIS
    # ==================================================================
    
    def analyze_3d_printability(self, obj_name: str,
                               layer_height: float = 0.2,
                               nozzle_diameter: float = 0.4,
                               max_overhang_angle: float = 45.0) -> Dict[str, Any]:
        """
        Analyze 3D printability of an object.
        
        Args:
            obj_name: Name of the object to analyze
            layer_height: 3D printer layer height (mm)
            nozzle_diameter: Nozzle diameter (mm)
            max_overhang_angle: Maximum unsupported overhang angle (degrees)
            
        Returns:
            Dictionary with 3D printability analysis
        """
        if not App or not App.ActiveDocument:
            raise RuntimeError("No active FreeCAD document")
        
        obj = App.ActiveDocument.getObject(obj_name)
        if not obj or not hasattr(obj, 'Shape'):
            raise ValueError(f"Object {obj_name} not found or has no shape")
        
        shape = obj.Shape
        issues = []
        recommendations = []
        
        # Analyze overhangs
        overhang_faces = []
        for face in shape.Faces:
            # Get face normal
            normal = face.normalAt(0.5, 0.5)  # Normal at face center
            
            # Calculate angle with Z-axis (build direction)
            z_axis = App.Vector(0, 0, 1)
            angle = math.degrees(normal.getAngle(z_axis))
            
            # Check if it's an overhang
            if 90 < angle < (180 - max_overhang_angle):
                overhang_faces.append({
                    'face_index': shape.Faces.index(face),
                    'angle': angle,
                    'area': face.Area
                })
        
        if overhang_faces:
            issues.append("Overhanging surfaces detected")
            recommendations.append("Add support structures or reorient part")
        
        # Check wall thickness
        min_wall_thickness = nozzle_diameter * 2  # Rule of thumb
        # This is a simplified check - real implementation would be more complex
        bbox = shape.BoundBox
        min_dimension = min(bbox.XLength, bbox.YLength, bbox.ZLength)
        
        if min_dimension < min_wall_thickness:
            issues.append(f"Thin walls detected (minimum: {min_dimension:.2f}mm)")
            recommendations.append(f"Increase wall thickness to at least {min_wall_thickness:.2f}mm")
        
        # Check for bridges
        # Simplified bridge detection - real implementation would analyze geometry
        bridge_warning = False
        if bbox.XLength > 20 or bbox.YLength > 20:  # Arbitrary threshold
            bridge_warning = True
            issues.append("Potential bridging issues for large spans")
            recommendations.append("Consider adding support for long bridges")
        
        # Overall printability score
        score = 100
        score -= len(overhang_faces) * 10  # Deduct points for overhangs
        if min_dimension < min_wall_thickness:
            score -= 20
        if bridge_warning:
            score -= 10
        
        score = max(0, score)  # Ensure score doesn't go negative
        
        # Determine printability level
        if score >= 80:
            printability = "excellent"
        elif score >= 60:
            printability = "good"
        elif score >= 40:
            printability = "fair"
        else:
            printability = "poor"
        
        return {
            'object_name': obj_name,
            'printability_score': score,
            'printability_level': printability,
            'print_settings': {
                'layer_height': layer_height,
                'nozzle_diameter': nozzle_diameter,
                'max_overhang_angle': max_overhang_angle
            },
            'issues': issues,
            'recommendations': recommendations,
            'overhang_analysis': {
                'overhang_faces': len(overhang_faces),
                'total_overhang_area': sum(f['area'] for f in overhang_faces),
                'faces': overhang_faces
            },
            'minimum_wall_thickness': min_dimension,
            'recommended_wall_thickness': min_wall_thickness
        }
    
    def analyze_draft_angles(self, obj_name: str,
                           direction: Tuple[float, float, float] = (0, 0, 1),
                           min_draft_angle: float = 1.0) -> Dict[str, Any]:
        """
        Analyze draft angles for injection molding or casting.
        
        Args:
            obj_name: Name of the object to analyze
            direction: Draft direction vector
            min_draft_angle: Minimum required draft angle (degrees)
            
        Returns:
            Dictionary with draft angle analysis
        """
        if not App or not App.ActiveDocument:
            raise RuntimeError("No active FreeCAD document")
        
        obj = App.ActiveDocument.getObject(obj_name)
        if not obj or not hasattr(obj, 'Shape'):
            raise ValueError(f"Object {obj_name} not found or has no shape")
        
        shape = obj.Shape
        draft_direction = App.Vector(*direction)
        
        faces_needing_draft = []
        faces_with_adequate_draft = []
        
        for i, face in enumerate(shape.Faces):
            # Get face normal at center
            normal = face.normalAt(0.5, 0.5)
            
            # Calculate angle between normal and draft direction
            angle = math.degrees(normal.getAngle(draft_direction))
            
            # Draft angle is the complement of the angle with draft direction
            draft_angle = 90.0 - min(angle, 180.0 - angle)
            
            face_info = {
                'face_index': i,
                'draft_angle': draft_angle,
                'area': face.Area,
                'normal': {'x': normal.x, 'y': normal.y, 'z': normal.z}
            }
            
            if abs(draft_angle) < min_draft_angle:
                faces_needing_draft.append(face_info)
            else:
                faces_with_adequate_draft.append(face_info)
        
        # Calculate overall compliance
        total_area = sum(face.Area for face in shape.Faces)
        compliant_area = sum(f['area'] for f in faces_with_adequate_draft)
        compliance_percentage = (compliant_area / total_area) * 100 if total_area > 0 else 0
        
        return {
            'object_name': obj_name,
            'draft_direction': direction,
            'minimum_draft_angle': min_draft_angle,
            'total_faces': len(shape.Faces),
            'faces_needing_draft': len(faces_needing_draft),
            'faces_with_adequate_draft': len(faces_with_adequate_draft),
            'compliance_percentage': compliance_percentage,
            'faces_analysis': {
                'needing_draft': faces_needing_draft,
                'adequate_draft': faces_with_adequate_draft
            },
            'recommendation': "Add draft angles to vertical faces" if faces_needing_draft else "Draft angles adequate"
        }
    
    def analyze_wall_thickness(self, obj_name: str,
                             min_thickness: float = 1.0,
                             max_thickness: float = 10.0) -> Dict[str, Any]:
        """
        Analyze wall thickness throughout an object.
        
        Args:
            obj_name: Name of the object to analyze
            min_thickness: Minimum acceptable wall thickness
            max_thickness: Maximum recommended wall thickness
            
        Returns:
            Dictionary with wall thickness analysis
        """
        if not App or not App.ActiveDocument:
            raise RuntimeError("No active FreeCAD document")
        
        obj = App.ActiveDocument.getObject(obj_name)
        if not obj or not hasattr(obj, 'Shape'):
            raise ValueError(f"Object {obj_name} not found or has no shape")
        
        shape = obj.Shape
        
        # This is a simplified implementation
        # Real wall thickness analysis would require more sophisticated algorithms
        
        # Use bounding box to estimate overall thickness
        bbox = shape.BoundBox
        dimensions = [bbox.XLength, bbox.YLength, bbox.ZLength]
        dimensions.sort()
        
        estimated_thickness = dimensions[0]  # Smallest dimension as thickness estimate
        
        # Categorize thickness
        if estimated_thickness < min_thickness:
            thickness_category = "too_thin"
            issues = [f"Estimated thickness {estimated_thickness:.2f}mm is below minimum {min_thickness}mm"]
            recommendations = [f"Increase thickness to at least {min_thickness}mm"]
        elif estimated_thickness > max_thickness:
            thickness_category = "too_thick"
            issues = [f"Estimated thickness {estimated_thickness:.2f}mm exceeds maximum {max_thickness}mm"]
            recommendations = ["Consider reducing thickness to save material"]
        else:
            thickness_category = "acceptable"
            issues = []
            recommendations = ["Wall thickness appears acceptable"]
        
        # Volume-based material usage estimate
        volume_mm3 = shape.Volume
        surface_area_mm2 = shape.Area
        
        # Rough estimate of average thickness
        if surface_area_mm2 > 0:
            avg_thickness_estimate = volume_mm3 / surface_area_mm2
        else:
            avg_thickness_estimate = 0
        
        return {
            'object_name': obj_name,
            'analysis_type': 'wall_thickness',
            'thickness_limits': {
                'minimum': min_thickness,
                'maximum': max_thickness
            },
            'estimated_thickness': estimated_thickness,
            'average_thickness_estimate': avg_thickness_estimate,
            'thickness_category': thickness_category,
            'volume_mm3': volume_mm3,
            'surface_area_mm2': surface_area_mm2,
            'issues': issues,
            'recommendations': recommendations
        }
    
    # ==================================================================
    # VALIDATION AND CHECKING
    # ==================================================================
    
    def validate_geometry(self, obj_name: str) -> Dict[str, Any]:
        """
        Validate geometric integrity of an object.
        
        Args:
            obj_name: Name of the object to validate
            
        Returns:
            Dictionary with validation results
        """
        if not App or not App.ActiveDocument:
            raise RuntimeError("No active FreeCAD document")
        
        obj = App.ActiveDocument.getObject(obj_name)
        if not obj or not hasattr(obj, 'Shape'):
            raise ValueError(f"Object {obj_name} not found or has no shape")
        
        shape = obj.Shape
        validation_results = {
            'object_name': obj_name,
            'valid': True,
            'issues': [],
            'warnings': [],
            'checks_performed': []
        }
        
        # Check if shape is valid
        validation_results['checks_performed'].append('shape_validity')
        if not shape.isValid():
            validation_results['valid'] = False
            validation_results['issues'].append("Shape geometry is invalid")
        
        # Check if shape is null
        validation_results['checks_performed'].append('null_shape')
        if shape.isNull():
            validation_results['valid'] = False
            validation_results['issues'].append("Shape is null/empty")
        
        # Check for closed/watertight geometry
        validation_results['checks_performed'].append('watertight')
        if hasattr(shape, 'isClosed'):
            if not shape.isClosed():
                validation_results['warnings'].append("Shape is not closed/watertight")
        
        # Check volume
        validation_results['checks_performed'].append('volume')
        if shape.Volume <= 0:
            validation_results['warnings'].append("Shape has zero or negative volume")
        
        # Check for self-intersections (basic check)
        validation_results['checks_performed'].append('self_intersection')
        try:
            # This is a simplified check
            cleaned_shape = shape.removeSplitter()
            if cleaned_shape.Volume != shape.Volume:
                validation_results['warnings'].append("Potential self-intersections detected")
        except Exception:
            validation_results['warnings'].append("Could not check for self-intersections")
        
        # Check topology
        validation_results['checks_performed'].append('topology')
        edge_count = len(shape.Edges)
        face_count = len(shape.Faces)
        vertex_count = len(shape.Vertexes)
        
        # Basic topology sanity checks
        if edge_count == 0 and face_count > 0:
            validation_results['warnings'].append("Faces without edges detected")
        if vertex_count == 0 and edge_count > 0:
            validation_results['warnings'].append("Edges without vertices detected")
        
        return validation_results
    
    def check_object_intersections(self, obj1_name: str, 
                                 obj2_name: str) -> Dict[str, Any]:
        """
        Check if two objects intersect.
        
        Args:
            obj1_name: Name of first object
            obj2_name: Name of second object
            
        Returns:
            Dictionary with intersection analysis
        """
        if not App or not App.ActiveDocument:
            raise RuntimeError("No active FreeCAD document")
        
        obj1 = App.ActiveDocument.getObject(obj1_name)
        obj2 = App.ActiveDocument.getObject(obj2_name)
        
        if not obj1 or not hasattr(obj1, 'Shape'):
            raise ValueError(f"Object {obj1_name} not found or has no shape")
        if not obj2 or not hasattr(obj2, 'Shape'):
            raise ValueError(f"Object {obj2_name} not found or has no shape")
        
        shape1 = obj1.Shape
        shape2 = obj2.Shape
        
        # Check for intersection
        try:
            common = shape1.common(shape2)
            intersects = common.Volume > 0
            
            if intersects:
                intersection_volume = common.Volume
                overlap_percentage1 = (intersection_volume / shape1.Volume) * 100
                overlap_percentage2 = (intersection_volume / shape2.Volume) * 100
            else:
                intersection_volume = 0
                overlap_percentage1 = 0
                overlap_percentage2 = 0
            
            # Calculate minimum distance if no intersection
            if not intersects:
                try:
                    min_distance = shape1.distToShape(shape2)[0]
                except Exception:
                    min_distance = None
            else:
                min_distance = 0
            
            return {
                'object1': obj1_name,
                'object2': obj2_name,
                'intersects': intersects,
                'intersection_volume': intersection_volume,
                'overlap_percentage': {
                    'object1': overlap_percentage1,
                    'object2': overlap_percentage2
                },
                'minimum_distance': min_distance,
                'analysis_type': 'intersection_check'
            }
            
        except Exception as e:
            return {
                'object1': obj1_name,
                'object2': obj2_name,
                'intersects': None,
                'error': f"Intersection check failed: {str(e)}",
                'analysis_type': 'intersection_check'
            }
    
    # ==================================================================
    # MEASUREMENT OPERATIONS
    # ==================================================================
    
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
            Dictionary with distance measurement
        """
        if not App or not App.ActiveDocument:
            raise RuntimeError("No active FreeCAD document")
        
        if point1 and point2:
            # Point to point measurement
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
            # Object to object measurement
            obj1 = App.ActiveDocument.getObject(obj1_name)
            obj2 = App.ActiveDocument.getObject(obj2_name)
            
            if not obj1 or not obj2:
                raise ValueError("One or both objects not found")
            
            if not (hasattr(obj1, 'Shape') and hasattr(obj2, 'Shape')):
                raise ValueError("One or both objects have no shape")
            
            try:
                distance_info = obj1.Shape.distToShape(obj2.Shape)
                distance = distance_info[0]
                closest_points = distance_info[1]
                
                return {
                    'measurement_type': 'object_to_object',
                    'distance': distance,
                    'object1': obj1_name,
                    'object2': obj2_name,
                    'closest_points': {
                        'on_object1': (closest_points[0].x, closest_points[0].y, closest_points[0].z),
                        'on_object2': (closest_points[1].x, closest_points[1].y, closest_points[1].z)
                    },
                    'units': 'mm'
                }
                
            except Exception as e:
                return {
                    'measurement_type': 'object_to_object',
                    'error': f"Distance measurement failed: {str(e)}",
                    'object1': obj1_name,
                    'object2': obj2_name
                }
        
        else:
            raise ValueError("Must provide either two objects or two points")
    
    def measure_angle(self, obj1_name: str, obj2_name: str,
                     reference_point: Tuple[float, float, float] = None) -> Dict[str, Any]:
        """
        Measure angle between two objects or edges.
        
        Args:
            obj1_name: First object/edge name
            obj2_name: Second object/edge name
            reference_point: Reference point for angle measurement
            
        Returns:
            Dictionary with angle measurement
        """
        if not App or not App.ActiveDocument:
            raise RuntimeError("No active FreeCAD document")
        
        obj1 = App.ActiveDocument.getObject(obj1_name)
        obj2 = App.ActiveDocument.getObject(obj2_name)
        
        if not obj1 or not obj2:
            raise ValueError("One or both objects not found")
        
        try:
            # This is a simplified implementation
            # Real angle measurement would depend on object types and context
            
            if hasattr(obj1, 'Shape') and hasattr(obj2, 'Shape'):
                # For shapes, we can measure angle between face normals
                if obj1.Shape.Faces and obj2.Shape.Faces:
                    normal1 = obj1.Shape.Faces[0].normalAt(0.5, 0.5)
                    normal2 = obj2.Shape.Faces[0].normalAt(0.5, 0.5)
                    
                    angle_rad = normal1.getAngle(normal2)
                    angle_deg = math.degrees(angle_rad)
                    
                    return {
                        'measurement_type': 'face_normals_angle',
                        'angle_degrees': angle_deg,
                        'angle_radians': angle_rad,
                        'object1': obj1_name,
                        'object2': obj2_name,
                        'units': 'degrees'
                    }
            
            return {
                'measurement_type': 'angle',
                'error': "Angle measurement not supported for these object types",
                'object1': obj1_name,
                'object2': obj2_name
            }
            
        except Exception as e:
            return {
                'measurement_type': 'angle',
                'error': f"Angle measurement failed: {str(e)}",
                'object1': obj1_name,
                'object2': obj2_name
            }
    
    # ==================================================================
    # UTILITY METHODS
    # ==================================================================
    
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
            'zlength': bbox.ZLength,
            'center': {
                'x': (bbox.XMin + bbox.XMax) / 2,
                'y': (bbox.YMin + bbox.YMax) / 2,
                'z': (bbox.ZMin + bbox.ZMax) / 2
            }
        }
    
    def get_analysis_history(self) -> List[Dict[str, Any]]:
        """Get history of all executed analyses"""
        return self.analysis_history.copy()
    
    def clear_analysis_history(self):
        """Clear analysis history"""
        self.analysis_history.clear()
    
    def get_available_analyses(self) -> List[str]:
        """Get list of all available analysis operations"""
        return list(self.analysis_operations.keys())
    
    # ==================================================================
    # PLACEHOLDER IMPLEMENTATIONS FOR MISSING METHODS
    # ==================================================================
    
    def analyze_surface_properties(self, obj_name: str) -> Dict[str, Any]:
        """Placeholder for surface properties analysis"""
        return {'status': 'not_implemented', 'operation': 'analyze_surface_properties'}
    
    def analyze_volume_properties(self, obj_name: str) -> Dict[str, Any]:
        """Placeholder for volume properties analysis"""
        return {'status': 'not_implemented', 'operation': 'analyze_volume_properties'}
    
    def analyze_cross_section(self, obj_name: str, plane: str) -> Dict[str, Any]:
        """Placeholder for cross section analysis"""
        return {'status': 'not_implemented', 'operation': 'analyze_cross_section'}
    
    def check_self_intersections(self, obj_name: str) -> Dict[str, Any]:
        """Placeholder for self intersection check"""
        return {'status': 'not_implemented', 'operation': 'check_self_intersections'}
    
    def check_topology(self, obj_name: str) -> Dict[str, Any]:
        """Placeholder for topology check"""
        return {'status': 'not_implemented', 'operation': 'check_topology'}
    
    def check_watertight(self, obj_name: str) -> Dict[str, Any]:
        """Placeholder for watertight check"""
        return {'status': 'not_implemented', 'operation': 'check_watertight'}
    
    def analyze_overhangs(self, obj_name: str, angle: float = 45.0) -> Dict[str, Any]:
        """Placeholder for overhang analysis"""
        return {'status': 'not_implemented', 'operation': 'analyze_overhangs'}
    
    def analyze_support_requirements(self, obj_name: str) -> Dict[str, Any]:
        """Placeholder for support requirements analysis"""
        return {'status': 'not_implemented', 'operation': 'analyze_support_requirements'}
    
    def analyze_undercuts(self, obj_name: str) -> Dict[str, Any]:
        """Placeholder for undercut analysis"""
        return {'status': 'not_implemented', 'operation': 'analyze_undercuts'}
    
    def analyze_stress_concentration(self, obj_name: str) -> Dict[str, Any]:
        """Placeholder for stress concentration analysis"""
        return {'status': 'not_implemented', 'operation': 'analyze_stress_concentration'}
    
    def calculate_moment_of_inertia(self, obj_name: str) -> Dict[str, Any]:
        """Placeholder for moment of inertia calculation"""
        return {'status': 'not_implemented', 'operation': 'calculate_moment_of_inertia'}
    
    def analyze_section_properties(self, obj_name: str) -> Dict[str, Any]:
        """Placeholder for section properties analysis"""
        return {'status': 'not_implemented', 'operation': 'analyze_section_properties'}
    
    def measure_curvature(self, obj_name: str, point: Tuple[float, float, float]) -> Dict[str, Any]:
        """Placeholder for curvature measurement"""
        return {'status': 'not_implemented', 'operation': 'measure_curvature'}
    
    def measure_surface_deviation(self, obj1_name: str, obj2_name: str) -> Dict[str, Any]:
        """Placeholder for surface deviation measurement"""
        return {'status': 'not_implemented', 'operation': 'measure_surface_deviation'}
    
    def compare_two_geometries(self, obj1_name: str, obj2_name: str) -> Dict[str, Any]:
        """Placeholder for geometry comparison"""
        return {'status': 'not_implemented', 'operation': 'compare_two_geometries'}
    
    def compare_volumes(self, obj1_name: str, obj2_name: str) -> Dict[str, Any]:
        """Placeholder for volume comparison"""
        return {'status': 'not_implemented', 'operation': 'compare_volumes'}
    
    def compare_surface_areas(self, obj1_name: str, obj2_name: str) -> Dict[str, Any]:
        """Placeholder for surface area comparison"""
        return {'status': 'not_implemented', 'operation': 'compare_surface_areas'}
    
    def analyze_mesh_quality(self, obj_name: str) -> Dict[str, Any]:
        """Placeholder for mesh quality analysis"""
        return {'status': 'not_implemented', 'operation': 'analyze_mesh_quality'}
    
    def analyze_surface_quality(self, obj_name: str) -> Dict[str, Any]:
        """Placeholder for surface quality analysis"""
        return {'status': 'not_implemented', 'operation': 'analyze_surface_quality'}
    
    def analyze_design_complexity(self, obj_name: str) -> Dict[str, Any]:
        """Placeholder for design complexity analysis"""
        return {'status': 'not_implemented', 'operation': 'analyze_design_complexity'}
