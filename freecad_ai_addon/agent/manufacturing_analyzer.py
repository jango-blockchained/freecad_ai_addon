"""
Manufacturing Analysis Library for FreeCAD AI Addon.

Provides comprehensive manufacturing analysis including CNC machining,
3D printing, injection molding, and general manufacturing guidelines.
"""

from typing import Dict, Any, List
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


class ManufacturingAnalyzer:
    """
    Comprehensive manufacturing analysis system.
    
    Provides analysis and optimization for various manufacturing processes
    including CNC machining, 3D printing, injection molding, and casting.
    """
    
    def __init__(self):
        """Initialize the manufacturing analyzer."""
        self.logger = logging.getLogger(f"{__name__}.ManufacturingAnalyzer")
        
        # Manufacturing process analyzers
        self.analyzers = {
            'cnc_machining': self.analyze_cnc_machining,
            '3d_printing': self.analyze_3d_printing,
            'injection_molding': self.analyze_injection_molding,
            'casting': self.analyze_casting,
            'sheet_metal': self.analyze_sheet_metal,
            'welding': self.analyze_welding,
            'assembly': self.analyze_assembly,
        }
        
        # Standard tool libraries
        self.cnc_tools = {
            'end_mills': {
                '1mm': {'diameter': 1.0, 'max_depth': 3.0, 'feed_rate': 100},
                '2mm': {'diameter': 2.0, 'max_depth': 6.0, 'feed_rate': 200},
                '3mm': {'diameter': 3.0, 'max_depth': 9.0, 'feed_rate': 300},
                '6mm': {'diameter': 6.0, 'max_depth': 18.0, 'feed_rate': 600},
                '10mm': {'diameter': 10.0, 'max_depth': 30.0, 'feed_rate': 800},
                '20mm': {'diameter': 20.0, 'max_depth': 60.0, 'feed_rate': 1000},
            },
            'drills': {
                '1mm': {'diameter': 1.0, 'max_depth': 10.0},
                '2mm': {'diameter': 2.0, 'max_depth': 20.0},
                '3mm': {'diameter': 3.0, 'max_depth': 30.0},
                '5mm': {'diameter': 5.0, 'max_depth': 50.0},
                '6mm': {'diameter': 6.0, 'max_depth': 60.0},
                '8mm': {'diameter': 8.0, 'max_depth': 80.0},
                '10mm': {'diameter': 10.0, 'max_depth': 100.0},
            }
        }
        
        # Material properties database
        self.materials = {
            'aluminum': {
                'density': 2.7,  # g/cm³
                'tensile_strength': 276,  # MPa
                'yield_strength': 207,  # MPa
                'machinability': 'excellent',
                'min_wall_thickness': 0.5,  # mm
                'draft_angle': 0.5,  # degrees
            },
            'steel': {
                'density': 7.85,
                'tensile_strength': 400,
                'yield_strength': 250,
                'machinability': 'good',
                'min_wall_thickness': 1.0,
                'draft_angle': 1.0,
            },
            'plastic_abs': {
                'density': 1.05,
                'tensile_strength': 40,
                'yield_strength': 30,
                'machinability': 'fair',
                'min_wall_thickness': 0.8,
                'draft_angle': 1.0,
            },
            'plastic_pla': {
                'density': 1.24,
                'tensile_strength': 50,
                'yield_strength': 40,
                'machinability': 'poor',
                'min_wall_thickness': 0.4,
                'draft_angle': 0.0,  # 3D printing
            }
        }
        
        self.logger.info("Manufacturing Analyzer initialized")
    
    def analyze_manufacturing_feasibility(self, obj_name: str,
                                        process: str,
                                        material: str = 'aluminum',
                                        parameters: Dict[str, Any] = None
                                        ) -> Dict[str, Any]:
        """
        Analyze manufacturing feasibility for a given process.
        
        Args:
            obj_name: Name of the FreeCAD object to analyze
            process: Manufacturing process (cnc_machining, 3d_printing, etc.)
            material: Material type
            parameters: Process-specific parameters
            
        Returns:
            Manufacturing feasibility analysis
        """
        if process not in self.analyzers:
            return {
                'status': 'failed',
                'error': f"Unknown process: {process}",
                'available_processes': list(self.analyzers.keys())
            }
        
        if not App or not App.ActiveDocument:
            return {
                'status': 'failed',
                'error': "No active FreeCAD document"
            }
        
        try:
            obj = App.ActiveDocument.getObject(obj_name)
            if not obj or not hasattr(obj, 'Shape'):
                return {
                    'status': 'failed',
                    'error': f"Object {obj_name} not found or has no shape"
                }
            
            # Get material properties
            material_props = self.materials.get(material, self.materials['aluminum'])
            
            # Run process-specific analysis
            analyzer_func = self.analyzers[process]
            analysis_result = analyzer_func(obj, material_props, parameters or {})
            
            # Add general analysis
            general_analysis = self._analyze_general_properties(obj, material_props)
            analysis_result.update(general_analysis)
            
            return {
                'status': 'success',
                'object_name': obj_name,
                'process': process,
                'material': material,
                'analysis': analysis_result
            }
            
        except Exception as e:
            self.logger.error(f"Manufacturing analysis failed for {obj_name}: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    # ========================================================================
    # CNC MACHINING ANALYSIS
    # ========================================================================
    
    def analyze_cnc_machining(self, obj: Any, material_props: Dict[str, Any],
                            parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze CNC machining feasibility."""
        analysis = {
            'process': 'cnc_machining',
            'feasibility': 'good',
            'issues': [],
            'recommendations': [],
            'toolpath_analysis': {},
            'estimated_time': 0.0,
            'material_removal': 0.0
        }
        
        shape = obj.Shape
        bbox = shape.BoundBox
        
        # Analyze accessibility
        accessibility = self._analyze_tool_accessibility(shape)
        analysis['accessibility'] = accessibility
        
        # Check for undercuts
        undercuts = self._detect_undercuts(shape)
        if undercuts['count'] > 0:
            analysis['issues'].append("Undercuts detected - may require multiple setups")
            analysis['undercuts'] = undercuts
        
        # Analyze wall thickness
        wall_analysis = self._analyze_wall_thickness(shape, material_props)
        if wall_analysis['min_thickness'] < material_props['min_wall_thickness']:
            analysis['issues'].append(
                f"Wall thickness below minimum ({material_props['min_wall_thickness']}mm)")
        
        # Draft angle analysis
        draft_analysis = self._analyze_draft_angles(shape)
        analysis['draft_angles'] = draft_analysis
        
        # Tool selection
        tool_selection = self._select_optimal_tools(shape, self.cnc_tools)
        analysis['recommended_tools'] = tool_selection
        
        # Machining time estimation
        estimated_time = self._estimate_machining_time(shape, tool_selection, material_props)
        analysis['estimated_time'] = estimated_time
        
        # Material utilization
        billet_volume = bbox.XLength * bbox.YLength * bbox.ZLength
        part_volume = shape.Volume
        material_utilization = (part_volume / billet_volume) * 100
        analysis['material_utilization'] = material_utilization
        
        if material_utilization < 30:
            analysis['recommendations'].append(
                "Low material utilization - consider design optimization")
        
        # Surface finish recommendations
        surface_finish = self._recommend_surface_finish(shape, material_props)
        analysis['surface_finish'] = surface_finish
        
        return analysis
    
    # ========================================================================
    # 3D PRINTING ANALYSIS
    # ========================================================================
    
    def analyze_3d_printing(self, obj: Any, material_props: Dict[str, Any],
                           parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze 3D printing feasibility."""
        analysis = {
            'process': '3d_printing',
            'feasibility': 'excellent',
            'issues': [],
            'recommendations': [],
            'support_requirements': {},
            'print_time': 0.0,
            'material_usage': 0.0
        }
        
        shape = obj.Shape
        layer_height = parameters.get('layer_height', 0.2)
        nozzle_diameter = parameters.get('nozzle_diameter', 0.4)
        
        # Overhang analysis
        overhang_analysis = self._analyze_overhangs(shape, parameters)
        analysis['overhangs'] = overhang_analysis
        
        if overhang_analysis['critical_overhangs'] > 0:
            analysis['issues'].append("Critical overhangs detected - supports required")
            analysis['support_requirements'] = {
                'required': True,
                'area': overhang_analysis.get('support_area', 0),
                'type': 'tree_supports' if overhang_analysis['critical_overhangs'] > 5 else 'linear_supports'
            }
        
        # Bridge analysis
        bridge_analysis = self._analyze_bridges(shape)
        analysis['bridges'] = bridge_analysis
        
        # Wall thickness analysis for 3D printing
        min_wall = nozzle_diameter * 2
        wall_analysis = self._analyze_wall_thickness(shape, {'min_wall_thickness': min_wall})
        if wall_analysis['min_thickness'] < min_wall:
            analysis['issues'].append(f"Wall thickness below printable minimum ({min_wall}mm)")
        
        # Layer adhesion analysis
        layer_adhesion = self._analyze_layer_adhesion(shape, layer_height)
        analysis['layer_adhesion'] = layer_adhesion
        
        # Print orientation recommendations
        orientation = self._recommend_print_orientation(shape)
        analysis['recommended_orientation'] = orientation
        
        # Estimate print time
        print_time = self._estimate_print_time(shape, parameters)
        analysis['print_time'] = print_time
        
        # Material usage
        material_usage = self._calculate_material_usage(shape, parameters)
        analysis['material_usage'] = material_usage
        
        return analysis
    
    # ========================================================================
    # INJECTION MOLDING ANALYSIS
    # ========================================================================
    
    def analyze_injection_molding(self, obj: Any, material_props: Dict[str, Any],
                                parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze injection molding feasibility."""
        analysis = {
            'process': 'injection_molding',
            'feasibility': 'good',
            'issues': [],
            'recommendations': [],
            'mold_complexity': 'medium',
            'cycle_time': 0.0
        }
        
        shape = obj.Shape
        
        # Draft angle analysis (critical for injection molding)
        draft_analysis = self._analyze_draft_angles(shape)
        min_draft = material_props.get('draft_angle', 1.0)
        
        insufficient_draft = [angle for angle in draft_analysis.get('angles', [])
                            if angle < min_draft]
        if insufficient_draft:
            analysis['issues'].append(f"Insufficient draft angles (min {min_draft}°)")
            analysis['draft_issues'] = len(insufficient_draft)
        
        # Wall thickness uniformity
        wall_uniformity = self._analyze_wall_uniformity(shape)
        analysis['wall_uniformity'] = wall_uniformity
        
        if wall_uniformity['variation'] > 50:  # 50% variation
            analysis['issues'].append("High wall thickness variation - may cause warping")
        
        # Undercut analysis (affects mold complexity)
        undercuts = self._detect_undercuts(shape)
        if undercuts['count'] > 0:
            analysis['mold_complexity'] = 'high'
            analysis['recommendations'].append("Undercuts require side actions or inserts")
        
        # Gate location analysis
        gate_analysis = self._analyze_gate_locations(shape)
        analysis['gate_recommendations'] = gate_analysis
        
        # Cooling analysis
        cooling_analysis = self._analyze_cooling_requirements(shape, material_props)
        analysis['cooling'] = cooling_analysis
        
        # Estimate cycle time
        cycle_time = self._estimate_injection_cycle_time(shape, material_props)
        analysis['cycle_time'] = cycle_time
        
        return analysis
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _analyze_general_properties(self, obj: Any,
                                  material_props: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze general geometric properties."""
        shape = obj.Shape
        bbox = shape.BoundBox
        
        return {
            'volume': shape.Volume,
            'surface_area': shape.Area,
            'bounding_box': {
                'x': bbox.XLength,
                'y': bbox.YLength,
                'z': bbox.ZLength
            },
            'mass': shape.Volume * material_props.get('density', 1.0) / 1000,  # kg
            'complexity_score': self._calculate_complexity_score(shape)
        }
    
    def _analyze_tool_accessibility(self, shape: Any) -> Dict[str, Any]:
        """Analyze tool accessibility for machining."""
        # Simplified accessibility analysis
        faces = getattr(shape, 'Faces', [])
        accessible_faces = 0
        
        for face in faces:
            # Check if face normal points in accessible direction
            if hasattr(face, 'normalAt'):
                normal = face.normalAt(0.5, 0.5)
                if normal.z > 0.1 or abs(normal.x) > 0.8 or abs(normal.y) > 0.8:
                    accessible_faces += 1
            else:
                # For mocked faces, assume accessible
                accessible_faces += 1
        
        total_faces = len(faces)
        accessibility_ratio = accessible_faces / total_faces if total_faces else 1.0
        
        return {
            'total_faces': total_faces,
            'accessible_faces': accessible_faces,
            'accessibility_ratio': accessibility_ratio,
            'accessibility_rating': 'good' if accessibility_ratio > 0.7 else 'limited'
        }
    
    def _detect_undercuts(self, shape: Any) -> Dict[str, Any]:
        """Detect undercuts in the geometry."""
        # Simplified undercut detection
        faces = getattr(shape, 'Faces', [])
        undercuts = []
        
        for i, face in enumerate(faces):
            if hasattr(face, 'normalAt') and hasattr(face, 'Area'):
                normal = face.normalAt(0.5, 0.5)
                # Check for faces with upward-pointing normals (potential undercuts)
                if normal.z < -0.5:
                    undercuts.append({
                        'face_index': i,
                        'normal': (normal.x, normal.y, normal.z),
                        'area': face.Area
                    })
            else:
                # For mocked faces, assume no undercuts
                pass
        
        return {
            'count': len(undercuts),
            'undercuts': undercuts,
            'total_undercut_area': sum(uc['area'] for uc in undercuts)
        }
    
    def _analyze_wall_thickness(self, shape: Any,
                              material_props: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze wall thickness throughout the part."""
        # Simplified wall thickness analysis
        bbox = shape.BoundBox
        min_dimension = min(bbox.XLength, bbox.YLength, bbox.ZLength)
        
        # Estimate minimum wall thickness (simplified)
        estimated_min_thickness = min_dimension * 0.1
        
        return {
            'min_thickness': estimated_min_thickness,
            'max_thickness': min_dimension * 0.5,
            'average_thickness': min_dimension * 0.25,
            'meets_minimum': estimated_min_thickness >= material_props.get('min_wall_thickness', 1.0)
        }
    
    def _analyze_draft_angles(self, shape: Any) -> Dict[str, Any]:
        """Analyze draft angles on vertical faces."""
        faces = getattr(shape, 'Faces', [])
        vertical_faces = []
        
        for face in faces:
            if hasattr(face, 'normalAt') and hasattr(face, 'Area'):
                normal = face.normalAt(0.5, 0.5)
                # Check if face is approximately vertical
                if abs(normal.z) < 0.2:  # Nearly vertical
                    # Calculate draft angle (simplified)
                    draft_angle = math.degrees(math.asin(abs(normal.z)))
                    vertical_faces.append({
                        'area': face.Area,
                        'draft_angle': draft_angle
                    })
        
        if vertical_faces:
            total_faces = len(vertical_faces)
            avg_draft = sum(f['draft_angle'] for f in vertical_faces) / total_faces
            min_draft = min(f['draft_angle'] for f in vertical_faces)
        else:
            avg_draft = min_draft = 0
        
        return {
            'vertical_faces': len(vertical_faces),
            'average_draft': avg_draft,
            'minimum_draft': min_draft,
            'angles': [f['draft_angle'] for f in vertical_faces]
        }
    
    def _calculate_complexity_score(self, shape: Any) -> float:
        """Calculate a complexity score for the geometry."""
        # Simplified complexity calculation
        faces_count = len(getattr(shape, 'Faces', []))
        edges_count = len(getattr(shape, 'Edges', []))
        vertices_count = len(getattr(shape, 'Vertexes', []))
        
        # Normalize by volume
        volume = max(getattr(shape, 'Volume', 1.0), 1.0)
        
        complexity = (faces_count * 0.5 + edges_count * 0.3 + 
                     vertices_count * 0.2) / volume
        return min(complexity * 1000, 10.0)  # Scale and cap at 10
    
    # Placeholder implementations for other analysis methods
    def _select_optimal_tools(self, shape: Any, tools: Dict[str, Any]) -> Dict[str, Any]:
        """Select optimal tools for machining."""
        return {'primary_tool': '6mm_end_mill', 'secondary_tools': ['3mm_drill']}
    
    def _estimate_machining_time(self, shape: Any, tools: Dict[str, Any],
                               material: Dict[str, Any]) -> float:
        """Estimate machining time."""
        return shape.Volume * 0.1  # Simplified: 0.1 min per cm³
    
    def _recommend_surface_finish(self, shape: Any,
                                material: Dict[str, Any]) -> Dict[str, Any]:
        """Recommend surface finish parameters."""
        return {'roughness': 'Ra 1.6', 'process': 'milling'}
    
    def _analyze_overhangs(self, shape: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze overhangs for 3D printing."""
        return {'critical_overhangs': 0, 'support_area': 0}
    
    def _analyze_bridges(self, shape: Any) -> Dict[str, Any]:
        """Analyze bridge structures."""
        return {'bridge_count': 0, 'max_bridge_length': 0}
    
    def _analyze_layer_adhesion(self, shape: Any, layer_height: float) -> Dict[str, Any]:
        """Analyze layer adhesion requirements."""
        return {'adhesion_score': 0.8, 'critical_areas': []}
    
    def _recommend_print_orientation(self, shape: Any) -> Dict[str, Any]:
        """Recommend optimal print orientation."""
        return {'orientation': 'flat', 'support_volume': 0}
    
    def _estimate_print_time(self, shape: Any, params: Dict[str, Any]) -> float:
        """Estimate 3D printing time."""
        return shape.Volume * 2.0  # Simplified: 2 min per cm³
    
    def _calculate_material_usage(self, shape: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate material usage for 3D printing."""
        return {'part_volume': shape.Volume, 'support_volume': 0, 'total_volume': shape.Volume}
    
    # Additional placeholder methods for injection molding
    def _analyze_wall_uniformity(self, shape: Any) -> Dict[str, Any]:
        """Analyze wall thickness uniformity."""
        return {'variation': 20, 'uniformity_score': 0.8}
    
    def _analyze_gate_locations(self, shape: Any) -> Dict[str, Any]:
        """Analyze optimal gate locations."""
        return {'recommended_gates': 1, 'locations': ['center']}
    
    def _analyze_cooling_requirements(self, shape: Any,
                                   material: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze cooling requirements."""
        return {'cooling_time': 30, 'channels_needed': 2}
    
    def _estimate_injection_cycle_time(self, shape: Any,
                                     material: Dict[str, Any]) -> float:
        """Estimate injection molding cycle time."""
        return 60.0  # Simplified: 60 seconds
    
    # Placeholder methods for other processes
    def analyze_casting(self, obj: Any, material_props: Dict[str, Any],
                       parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze casting feasibility."""
        return {'process': 'casting', 'feasibility': 'good'}
    
    def analyze_sheet_metal(self, obj: Any, material_props: Dict[str, Any],
                          parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze sheet metal fabrication."""
        return {'process': 'sheet_metal', 'feasibility': 'good'}
    
    def analyze_welding(self, obj: Any, material_props: Dict[str, Any],
                       parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze welding requirements."""
        return {'process': 'welding', 'feasibility': 'good'}
    
    def analyze_assembly(self, obj: Any, material_props: Dict[str, Any],
                        parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze assembly requirements."""
        return {'process': 'assembly', 'feasibility': 'good'}
