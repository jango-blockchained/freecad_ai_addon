"""
Intelligent Decision Making Engine for FreeCAD AI Addon

This module implements the decision-making capabilities for AI agents including:
- Design pattern recognition
- Constraint solver integration
- Optimization algorithms
- Error recovery mechanisms
- Design validation tools
- Performance optimization suggestions

Author: FreeCAD AI Addon Development Team
License: MIT
"""

import logging
import math
import json
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import time

# Configure logging
logger = logging.getLogger(__name__)

# Try to import FreeCAD, provide graceful fallback
try:
    import FreeCAD
    import Part
    import Sketcher
    FREECAD_AVAILABLE = True
except ImportError:
    logger.warning("FreeCAD not available. Decision engine will run in simulation mode.")
    FREECAD_AVAILABLE = False
    FreeCAD = None


class PatternType(Enum):
    """Enumeration of recognized design patterns"""
    MOUNTING_BRACKET = "mounting_bracket"
    FLANGE_CONNECTION = "flange_connection"
    HOUSING_ENCLOSURE = "housing_enclosure"
    SHAFT_COUPLING = "shaft_coupling"
    BEARING_MOUNT = "bearing_mount"
    HEAT_SINK = "heat_sink"
    STRUCTURAL_FRAME = "structural_frame"
    GEAR_ASSEMBLY = "gear_assembly"
    CONNECTOR_INTERFACE = "connector_interface"
    CUSTOM_PATTERN = "custom_pattern"


class OptimizationGoal(Enum):
    """Enumeration of optimization objectives"""
    MINIMIZE_WEIGHT = "minimize_weight"
    MAXIMIZE_STRENGTH = "maximize_strength"
    MINIMIZE_COST = "minimize_cost"
    MAXIMIZE_STIFFNESS = "maximize_stiffness"
    OPTIMIZE_FLOW = "optimize_flow"
    MINIMIZE_STRESS = "minimize_stress"
    MAXIMIZE_HEAT_TRANSFER = "maximize_heat_transfer"
    MULTI_OBJECTIVE = "multi_objective"


@dataclass
class DesignPattern:
    """Data class representing a recognized design pattern"""
    pattern_type: PatternType
    confidence: float
    suggested_dimensions: Dict[str, float]
    required_features: List[str]
    optional_features: List[str]
    constraints: List[Dict[str, Any]]
    material_recommendations: List[str]
    manufacturing_notes: List[str]


@dataclass
class OptimizationResult:
    """Data class representing optimization results"""
    objective_value: float
    parameters: Dict[str, float]
    constraints_satisfied: bool
    iterations: int
    convergence_time: float
    suggestions: List[str]


@dataclass
class ValidationIssue:
    """Data class representing a design validation issue"""
    severity: str  # "critical", "warning", "info"
    category: str  # "geometry", "manufacturing", "performance"
    description: str
    location: Optional[Tuple[float, float, float]]
    suggested_fix: str
    auto_fixable: bool


class DesignPatternRecognizer:
    """Recognizes standard design patterns from geometry and context"""
    
    def __init__(self):
        self.pattern_library = self._initialize_pattern_library()
        self.recognition_history = []
    
    def _initialize_pattern_library(self) -> Dict[PatternType, Dict[str, Any]]:
        """Initialize the design pattern library with standard patterns"""
        return {
            PatternType.MOUNTING_BRACKET: {
                "features": ["base_plate", "mounting_holes", "vertical_support"],
                "dimensions": {
                    "base_length": (20.0, 200.0),
                    "base_width": (15.0, 150.0),
                    "base_thickness": (2.0, 20.0),
                    "hole_diameter": (3.0, 20.0),
                    "hole_spacing": (10.0, 100.0)
                },
                "constraints": [
                    {"type": "minimum_edge_distance", "value": 1.5},
                    {"type": "hole_pattern", "value": "rectangular_grid"},
                    {"type": "material_thickness", "min": 2.0}
                ]
            },
            PatternType.FLANGE_CONNECTION: {
                "features": ["circular_base", "bolt_circle", "central_bore"],
                "dimensions": {
                    "outer_diameter": (30.0, 500.0),
                    "bolt_circle_diameter": (20.0, 450.0),
                    "central_bore": (5.0, 300.0),
                    "flange_thickness": (5.0, 50.0),
                    "bolt_holes": (4, 24)
                },
                "constraints": [
                    {"type": "bolt_circle_ratio", "value": 0.8},
                    {"type": "minimum_bolt_spacing", "value": 15.0},
                    {"type": "central_bore_ratio", "value": 0.6}
                ]
            },
            PatternType.HOUSING_ENCLOSURE: {
                "features": ["wall_structure", "mounting_tabs", "access_ports"],
                "dimensions": {
                    "wall_thickness": (1.5, 10.0),
                    "corner_radius": (2.0, 20.0),
                    "mounting_hole_size": (3.0, 8.0)
                },
                "constraints": [
                    {"type": "draft_angle", "min": 0.5},
                    {"type": "minimum_wall_thickness", "value": 1.5},
                    {"type": "boss_height", "max": 3.0}
                ]
            }
        }
    
    def recognize_pattern(self, geometry_info: Dict[str, Any], 
                         context: Dict[str, Any] = None) -> List[DesignPattern]:
        """
        Recognize design patterns from geometry information
        
        Args:
            geometry_info: Dictionary containing geometric features and dimensions
            context: Optional context information (material, application, etc.)
            
        Returns:
            List of recognized patterns with confidence scores
        """
        patterns = []
        
        try:
            for pattern_type, pattern_data in self.pattern_library.items():
                confidence = self._calculate_pattern_confidence(
                    geometry_info, pattern_data, context
                )
                
                if confidence > 0.3:  # Threshold for pattern recognition
                    pattern = DesignPattern(
                        pattern_type=pattern_type,
                        confidence=confidence,
                        suggested_dimensions=self._suggest_dimensions(
                            pattern_type, geometry_info
                        ),
                        required_features=pattern_data["features"],
                        optional_features=[],
                        constraints=pattern_data["constraints"],
                        material_recommendations=self._suggest_materials(pattern_type),
                        manufacturing_notes=self._get_manufacturing_notes(pattern_type)
                    )
                    patterns.append(pattern)
            
            # Sort by confidence
            patterns.sort(key=lambda p: p.confidence, reverse=True)
            
            # Store in history
            self.recognition_history.append({
                "timestamp": time.time(),
                "geometry_info": geometry_info,
                "patterns": patterns
            })
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error in pattern recognition: {e}")
            return []
    
    def _calculate_pattern_confidence(self, geometry_info: Dict[str, Any],
                                    pattern_data: Dict[str, Any],
                                    context: Dict[str, Any] = None) -> float:
        """Calculate confidence score for pattern match"""
        confidence = 0.0
        
        # Check feature matches
        features_present = geometry_info.get("features", [])
        required_features = pattern_data["features"]
        
        feature_match_ratio = len(set(features_present) & set(required_features)) / len(required_features)
        confidence += feature_match_ratio * 0.6
        
        # Check dimension ranges
        dimensions = geometry_info.get("dimensions", {})
        pattern_dims = pattern_data.get("dimensions", {})
        
        dim_matches = 0
        for dim_name, dim_range in pattern_dims.items():
            if dim_name in dimensions:
                value = dimensions[dim_name]
                if isinstance(dim_range, tuple) and len(dim_range) == 2:
                    if dim_range[0] <= value <= dim_range[1]:
                        dim_matches += 1
                elif isinstance(dim_range, (int, float)):
                    if abs(value - dim_range) / dim_range < 0.2:  # 20% tolerance
                        dim_matches += 1
        
        if pattern_dims:
            confidence += (dim_matches / len(pattern_dims)) * 0.3
        
        # Context bonus
        if context:
            application = context.get("application", "")
            if "bracket" in application.lower() and "mounting" in str(pattern_data["features"]):
                confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _suggest_dimensions(self, pattern_type: PatternType, 
                          geometry_info: Dict[str, Any]) -> Dict[str, float]:
        """Suggest optimal dimensions for a recognized pattern"""
        suggestions = {}
        
        pattern_data = self.pattern_library.get(pattern_type, {})
        dimension_ranges = pattern_data.get("dimensions", {})
        
        for dim_name, dim_range in dimension_ranges.items():
            if isinstance(dim_range, tuple) and len(dim_range) == 2:
                # Suggest middle of range as starting point
                suggestions[dim_name] = (dim_range[0] + dim_range[1]) / 2
            elif isinstance(dim_range, (int, float)):
                suggestions[dim_name] = dim_range
        
        return suggestions
    
    def _suggest_materials(self, pattern_type: PatternType) -> List[str]:
        """Suggest appropriate materials for the pattern"""
        material_map = {
            PatternType.MOUNTING_BRACKET: ["Steel", "Aluminum", "Stainless Steel"],
            PatternType.FLANGE_CONNECTION: ["Steel", "Cast Iron", "Stainless Steel"],
            PatternType.HOUSING_ENCLOSURE: ["Aluminum", "Plastic (ABS)", "Steel"],
            PatternType.BEARING_MOUNT: ["Steel", "Cast Iron", "Bronze"],
            PatternType.HEAT_SINK: ["Aluminum", "Copper", "Thermal Plastic"]
        }
        return material_map.get(pattern_type, ["Steel", "Aluminum"])
    
    def _get_manufacturing_notes(self, pattern_type: PatternType) -> List[str]:
        """Get manufacturing considerations for the pattern"""
        notes_map = {
            PatternType.MOUNTING_BRACKET: [
                "Consider CNC machining for precision holes",
                "Add chamfers to mounting holes for easy assembly",
                "Ensure adequate clearance for fasteners"
            ],
            PatternType.FLANGE_CONNECTION: [
                "Machine bolt circle accurately",
                "Consider O-ring groove if sealing required",
                "Maintain flatness of mating surface"
            ],
            PatternType.HOUSING_ENCLOSURE: [
                "Add draft angles for molding",
                "Consider wall thickness for injection molding",
                "Add ribs for structural reinforcement"
            ]
        }
        return notes_map.get(pattern_type, [])


class ConstraintSolverIntegration:
    """Integrates with FreeCAD's constraint solver for intelligent constraint placement"""
    
    def __init__(self):
        self.solver_cache = {}
        self.constraint_suggestions = []
    
    def analyze_sketch_constraints(self, sketch_name: str) -> Dict[str, Any]:
        """
        Analyze sketch constraints and suggest improvements
        
        Args:
            sketch_name: Name of the sketch to analyze
            
        Returns:
            Dictionary containing constraint analysis and suggestions
        """
        analysis = {
            "degrees_of_freedom": 0,
            "conflicting_constraints": [],
            "missing_constraints": [],
            "redundant_constraints": [],
            "suggestions": []
        }
        
        if not FREECAD_AVAILABLE:
            logger.warning("FreeCAD not available for constraint analysis")
            return analysis
        
        try:
            doc = FreeCAD.ActiveDocument
            if not doc:
                return analysis
            
            sketch = doc.getObject(sketch_name)
            if not sketch or not hasattr(sketch, 'Constraints'):
                return analysis
            
            # Analyze degrees of freedom
            if hasattr(sketch, 'solve'):
                solver_result = sketch.solve()
                analysis["solver_status"] = solver_result
            
            # Count constraints by type
            constraint_types = {}
            for constraint in sketch.Constraints:
                constraint_type = constraint.Type
                constraint_types[constraint_type] = constraint_types.get(constraint_type, 0) + 1
            
            analysis["constraint_distribution"] = constraint_types
            
            # Suggest missing constraints
            geometry_count = len([g for g in sketch.Geometry if g.TypeId != 'Part::GeomPoint'])
            constraint_count = len(sketch.Constraints)
            
            if constraint_count < geometry_count * 2:  # Rough heuristic
                analysis["suggestions"].append(
                    "Consider adding more constraints for full constraint"
                )
            
            # Check for common constraint patterns
            self._suggest_constraint_patterns(sketch, analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing sketch constraints: {e}")
            return analysis
    
    def suggest_auto_constraints(self, sketch_name: str) -> List[Dict[str, Any]]:
        """
        Suggest automatic constraints based on geometry analysis
        
        Args:
            sketch_name: Name of the sketch to analyze
            
        Returns:
            List of suggested constraints
        """
        suggestions = []
        
        if not FREECAD_AVAILABLE:
            return suggestions
        
        try:
            doc = FreeCAD.ActiveDocument
            if not doc:
                return suggestions
            
            sketch = doc.getObject(sketch_name)
            if not sketch:
                return suggestions
            
            # Analyze geometry for auto-constraint opportunities
            for i, geom in enumerate(sketch.Geometry):
                if hasattr(geom, 'StartPoint') and hasattr(geom, 'EndPoint'):
                    # Check for horizontal/vertical lines
                    start = geom.StartPoint
                    end = geom.EndPoint
                    
                    dx = abs(end.x - start.x)
                    dy = abs(end.y - start.y)
                    
                    if dx < 0.01:  # Vertical line
                        suggestions.append({
                            "type": "Vertical",
                            "geometry_index": i,
                            "confidence": 0.9,
                            "description": f"Line {i} appears to be vertical"
                        })
                    elif dy < 0.01:  # Horizontal line
                        suggestions.append({
                            "type": "Horizontal",
                            "geometry_index": i,
                            "confidence": 0.9,
                            "description": f"Line {i} appears to be horizontal"
                        })
            
            # Check for coincident points
            points = []
            for i, geom in enumerate(sketch.Geometry):
                if hasattr(geom, 'StartPoint'):
                    points.append((i, 'start', geom.StartPoint))
                if hasattr(geom, 'EndPoint'):
                    points.append((i, 'end', geom.EndPoint))
            
            for i, (idx1, pt1_type, pt1) in enumerate(points):
                for idx2, pt2_type, pt2 in points[i+1:]:
                    if idx1 != idx2:  # Different geometry elements
                        distance = pt1.distanceToPoint(pt2)
                        if distance < 0.01:  # Points are very close
                            suggestions.append({
                                "type": "Coincident",
                                "geometry1": idx1,
                                "point1": pt1_type,
                                "geometry2": idx2,
                                "point2": pt2_type,
                                "confidence": 0.8,
                                "description": f"Points appear coincident"
                            })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error suggesting auto constraints: {e}")
            return suggestions
    
    def _suggest_constraint_patterns(self, sketch, analysis: Dict[str, Any]):
        """Suggest common constraint patterns"""
        # Check for rectangular patterns
        line_count = sum(1 for g in sketch.Geometry if g.TypeId == 'Part::GeomLineSegment')
        if line_count == 4:
            analysis["suggestions"].append(
                "Consider creating a rectangular constraint pattern"
            )
        
        # Check for symmetric patterns
        circle_count = sum(1 for g in sketch.Geometry if g.TypeId == 'Part::GeomCircle')
        if circle_count >= 2:
            analysis["suggestions"].append(
                "Consider adding symmetry constraints for circular patterns"
            )


class OptimizationEngine:
    """Implements optimization algorithms for design parameter optimization"""
    
    def __init__(self):
        self.optimization_history = []
        self.convergence_tolerance = 1e-6
        self.max_iterations = 100
    
    def optimize_parameters(self, objective: OptimizationGoal,
                          parameters: Dict[str, Dict[str, float]],
                          constraints: List[Dict[str, Any]] = None) -> OptimizationResult:
        """
        Optimize design parameters based on specified objective
        
        Args:
            objective: Optimization goal (weight, strength, etc.)
            parameters: Dictionary of parameters with bounds
            constraints: List of constraint definitions
            
        Returns:
            OptimizationResult with optimal parameters and metrics
        """
        start_time = time.time()
        
        try:
            # Simple gradient descent implementation for demonstration
            current_params = {}
            for param_name, param_data in parameters.items():
                # Initialize at middle of range
                min_val = param_data.get('min', 0.0)
                max_val = param_data.get('max', 100.0)
                current_params[param_name] = (min_val + max_val) / 2
            
            best_params = current_params.copy()
            best_value = self._evaluate_objective(objective, current_params)
            
            # Simple optimization loop
            learning_rate = 0.1
            for iteration in range(self.max_iterations):
                # Calculate gradients numerically
                gradients = {}
                for param_name in current_params:
                    delta = current_params[param_name] * 0.01  # 1% perturbation
                    
                    # Forward difference
                    perturbed_params = current_params.copy()
                    perturbed_params[param_name] += delta
                    
                    value_plus = self._evaluate_objective(objective, perturbed_params)
                    gradient = (value_plus - best_value) / delta
                    gradients[param_name] = gradient
                
                # Update parameters
                improved = False
                for param_name in current_params:
                    param_bounds = parameters[param_name]
                    min_val = param_bounds.get('min', 0.0)
                    max_val = param_bounds.get('max', 100.0)
                    
                    # Gradient descent step
                    if objective in [OptimizationGoal.MINIMIZE_WEIGHT, OptimizationGoal.MINIMIZE_COST]:
                        new_value = current_params[param_name] - learning_rate * gradients[param_name]
                    else:  # Maximization objectives
                        new_value = current_params[param_name] + learning_rate * gradients[param_name]
                    
                    # Apply bounds
                    new_value = max(min_val, min(max_val, new_value))
                    
                    if abs(new_value - current_params[param_name]) > self.convergence_tolerance:
                        improved = True
                    
                    current_params[param_name] = new_value
                
                # Evaluate new parameters
                current_value = self._evaluate_objective(objective, current_params)
                
                # Check if improved
                if self._is_better_value(objective, current_value, best_value):
                    best_value = current_value
                    best_params = current_params.copy()
                
                # Check convergence
                if not improved:
                    break
            
            # Check constraints
            constraints_satisfied = self._check_constraints(best_params, constraints or [])
            
            # Generate suggestions
            suggestions = self._generate_optimization_suggestions(
                objective, best_params, best_value
            )
            
            result = OptimizationResult(
                objective_value=best_value,
                parameters=best_params,
                constraints_satisfied=constraints_satisfied,
                iterations=iteration + 1,
                convergence_time=time.time() - start_time,
                suggestions=suggestions
            )
            
            # Store in history
            self.optimization_history.append({
                "timestamp": time.time(),
                "objective": objective,
                "result": result
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Error in parameter optimization: {e}")
            return OptimizationResult(
                objective_value=0.0,
                parameters=parameters,
                constraints_satisfied=False,
                iterations=0,
                convergence_time=0.0,
                suggestions=[f"Optimization failed: {e}"]
            )
    
    def _evaluate_objective(self, objective: OptimizationGoal, 
                          parameters: Dict[str, float]) -> float:
        """Evaluate objective function for given parameters"""
        
        # Simplified objective functions for demonstration
        if objective == OptimizationGoal.MINIMIZE_WEIGHT:
            # Assume weight is proportional to volume
            length = parameters.get('length', 50.0)
            width = parameters.get('width', 30.0)
            height = parameters.get('height', 10.0)
            return length * width * height
        
        elif objective == OptimizationGoal.MAXIMIZE_STRENGTH:
            # Simplified strength model based on section modulus
            width = parameters.get('width', 30.0)
            height = parameters.get('height', 10.0)
            return width * height ** 2 / 6  # Simplified section modulus
        
        elif objective == OptimizationGoal.MINIMIZE_COST:
            # Cost based on material volume and complexity
            volume = parameters.get('length', 50) * parameters.get('width', 30) * parameters.get('height', 10)
            complexity_factor = len(parameters)  # More parameters = more complexity
            return volume * 0.01 + complexity_factor * 5.0
        
        else:
            # Default: minimize sum of squares
            return sum(v ** 2 for v in parameters.values())
    
    def _is_better_value(self, objective: OptimizationGoal, new_value: float, 
                        current_value: float) -> bool:
        """Determine if new value is better than current for given objective"""
        if objective in [OptimizationGoal.MINIMIZE_WEIGHT, OptimizationGoal.MINIMIZE_COST, 
                        OptimizationGoal.MINIMIZE_STRESS]:
            return new_value < current_value
        else:  # Maximization objectives
            return new_value > current_value
    
    def _check_constraints(self, parameters: Dict[str, float], 
                          constraints: List[Dict[str, Any]]) -> bool:
        """Check if parameters satisfy all constraints"""
        for constraint in constraints:
            constraint_type = constraint.get('type', '')
            
            if constraint_type == 'maximum_value':
                param_name = constraint.get('parameter')
                max_value = constraint.get('value')
                if parameters.get(param_name, 0) > max_value:
                    return False
            
            elif constraint_type == 'minimum_value':
                param_name = constraint.get('parameter')
                min_value = constraint.get('value')
                if parameters.get(param_name, 0) < min_value:
                    return False
            
            elif constraint_type == 'ratio_constraint':
                param1 = constraint.get('parameter1')
                param2 = constraint.get('parameter2')
                required_ratio = constraint.get('ratio')
                
                if param2 in parameters and parameters[param2] != 0:
                    actual_ratio = parameters.get(param1, 0) / parameters[param2]
                    tolerance = constraint.get('tolerance', 0.1)
                    if abs(actual_ratio - required_ratio) > tolerance:
                        return False
        
        return True
    
    def _generate_optimization_suggestions(self, objective: OptimizationGoal,
                                         parameters: Dict[str, float],
                                         objective_value: float) -> List[str]:
        """Generate human-readable optimization suggestions"""
        suggestions = []
        
        if objective == OptimizationGoal.MINIMIZE_WEIGHT:
            suggestions.append(f"Optimized for minimum weight: {objective_value:.2f} cubic units")
            
            # Check for thin walls
            height = parameters.get('height', 10.0)
            if height < 2.0:
                suggestions.append("Consider increasing height for better structural integrity")
        
        elif objective == OptimizationGoal.MAXIMIZE_STRENGTH:
            suggestions.append(f"Optimized section modulus: {objective_value:.2f}")
            
            width = parameters.get('width', 30.0)
            height = parameters.get('height', 10.0)
            
            if height > width:
                suggestions.append("Tall cross-section optimized for bending strength")
            else:
                suggestions.append("Wide cross-section may be better for torsional strength")
        
        suggestions.append("Consider manufacturing constraints in final design")
        suggestions.append("Validate results with FEA analysis")
        
        return suggestions


class ErrorRecoveryMechanism:
    """Implements error recovery and alternative approach strategies"""
    
    def __init__(self):
        self.error_history = []
        self.recovery_strategies = self._initialize_recovery_strategies()
    
    def _initialize_recovery_strategies(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize error recovery strategies for common failure modes"""
        return {
            "boolean_operation_failed": [
                {
                    "strategy": "adjust_tolerance",
                    "description": "Increase boolean operation tolerance",
                    "parameters": {"tolerance": 0.01}
                },
                {
                    "strategy": "separate_operations",
                    "description": "Split complex boolean into simpler operations",
                    "parameters": {"split_threshold": 3}
                },
                {
                    "strategy": "fix_geometry",
                    "description": "Clean geometry before boolean operation",
                    "parameters": {"fix_tolerance": 0.001}
                }
            ],
            "sketch_constraint_conflict": [
                {
                    "strategy": "remove_redundant_constraints",
                    "description": "Remove conflicting or redundant constraints",
                    "parameters": {"conflict_tolerance": 0.01}
                },
                {
                    "strategy": "adjust_constraint_values",
                    "description": "Modify constraint values to resolve conflicts",
                    "parameters": {"adjustment_factor": 0.9}
                }
            ],
            "geometry_creation_failed": [
                {
                    "strategy": "validate_parameters",
                    "description": "Check and adjust input parameters",
                    "parameters": {"validation_rules": "strict"}
                },
                {
                    "strategy": "alternative_approach",
                    "description": "Try different geometric construction method",
                    "parameters": {"method": "alternative"}
                }
            ]
        }
    
    def handle_error(self, error_type: str, error_details: Dict[str, Any],
                    context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Handle errors and provide recovery suggestions
        
        Args:
            error_type: Type of error encountered
            error_details: Specific error information
            context: Context in which error occurred
            
        Returns:
            List of recovery strategies to attempt
        """
        recovery_options = []
        
        try:
            # Record error in history
            error_record = {
                "timestamp": time.time(),
                "error_type": error_type,
                "error_details": error_details,
                "context": context
            }
            self.error_history.append(error_record)
            
            # Get base recovery strategies
            base_strategies = self.recovery_strategies.get(error_type, [])
            
            # Customize strategies based on context
            for strategy in base_strategies:
                customized_strategy = self._customize_strategy(
                    strategy, error_details, context
                )
                recovery_options.append(customized_strategy)
            
            # Add general fallback strategies
            if not recovery_options:
                recovery_options.extend(self._get_fallback_strategies(error_type))
            
            # Sort by likelihood of success
            recovery_options.sort(key=lambda s: s.get('success_probability', 0.5), reverse=True)
            
            return recovery_options
            
        except Exception as e:
            logger.error(f"Error in error recovery handling: {e}")
            return [{
                "strategy": "manual_intervention",
                "description": "Manual intervention required",
                "success_probability": 0.1
            }]
    
    def _customize_strategy(self, strategy: Dict[str, Any], 
                          error_details: Dict[str, Any],
                          context: Dict[str, Any]) -> Dict[str, Any]:
        """Customize recovery strategy based on specific error context"""
        customized = strategy.copy()
        
        # Adjust parameters based on error specifics
        if strategy["strategy"] == "adjust_tolerance":
            current_tolerance = error_details.get("tolerance", 0.01)
            customized["parameters"]["tolerance"] = current_tolerance * 2
        
        elif strategy["strategy"] == "adjust_constraint_values":
            conflicting_value = error_details.get("conflicting_value", 10.0)
            adjustment = customized["parameters"]["adjustment_factor"]
            customized["parameters"]["suggested_value"] = conflicting_value * adjustment
        
        # Estimate success probability based on past experience
        similar_errors = [e for e in self.error_history 
                         if e["error_type"] == error_details.get("type", "")]
        
        if similar_errors:
            # Simple success rate calculation
            customized["success_probability"] = min(0.9, 0.5 + len(similar_errors) * 0.1)
        else:
            customized["success_probability"] = 0.5  # Default
        
        return customized
    
    def _get_fallback_strategies(self, error_type: str) -> List[Dict[str, Any]]:
        """Get general fallback strategies when specific ones aren't available"""
        return [
            {
                "strategy": "retry_operation",
                "description": "Retry the failed operation",
                "success_probability": 0.3
            },
            {
                "strategy": "simplify_approach",
                "description": "Use simpler geometric approach",
                "success_probability": 0.6
            },
            {
                "strategy": "manual_intervention",
                "description": "Request user intervention",
                "success_probability": 0.9
            }
        ]


class DesignValidator:
    """Validates designs against manufacturing and engineering rules"""
    
    def __init__(self):
        self.validation_rules = self._initialize_validation_rules()
        self.validation_history = []
    
    def _initialize_validation_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize design validation rules"""
        return {
            "minimum_wall_thickness": {
                "category": "manufacturing",
                "severity": "critical",
                "default_threshold": 1.5,  # mm
                "materials": {
                    "plastic": 0.8,
                    "aluminum": 1.0,
                    "steel": 1.5
                }
            },
            "draft_angle": {
                "category": "manufacturing",
                "severity": "warning",
                "default_threshold": 0.5,  # degrees
                "processes": {
                    "injection_molding": 1.0,
                    "die_casting": 1.5,
                    "machining": 0.0
                }
            },
            "corner_radius": {
                "category": "manufacturing",
                "severity": "warning",
                "default_threshold": 0.5,  # mm
                "materials": {
                    "plastic": 0.3,
                    "metal": 0.1
                }
            },
            "hole_edge_distance": {
                "category": "structural",
                "severity": "critical",
                "default_threshold": 1.5,  # times hole diameter
            },
            "aspect_ratio": {
                "category": "structural",
                "severity": "warning",
                "default_threshold": 10.0,  # length/width ratio
            }
        }
    
    def validate_design(self, geometry_info: Dict[str, Any],
                       material: str = "steel",
                       manufacturing_process: str = "machining") -> List[ValidationIssue]:
        """
        Validate design against manufacturing and engineering rules
        
        Args:
            geometry_info: Dictionary containing geometric information
            material: Material type for material-specific rules
            manufacturing_process: Manufacturing process for process-specific rules
            
        Returns:
            List of validation issues found
        """
        issues = []
        
        try:
            # Validate wall thickness
            wall_thickness_issues = self._check_wall_thickness(
                geometry_info, material
            )
            issues.extend(wall_thickness_issues)
            
            # Validate draft angles
            if manufacturing_process in ["injection_molding", "die_casting"]:
                draft_issues = self._check_draft_angles(
                    geometry_info, manufacturing_process
                )
                issues.extend(draft_issues)
            
            # Validate corner radii
            corner_issues = self._check_corner_radii(geometry_info, material)
            issues.extend(corner_issues)
            
            # Validate hole positions
            hole_issues = self._check_hole_positions(geometry_info)
            issues.extend(hole_issues)
            
            # Validate aspect ratios
            aspect_issues = self._check_aspect_ratios(geometry_info)
            issues.extend(aspect_issues)
            
            # Store validation results
            self.validation_history.append({
                "timestamp": time.time(),
                "geometry_info": geometry_info,
                "material": material,
                "process": manufacturing_process,
                "issues": issues
            })
            
            return issues
            
        except Exception as e:
            logger.error(f"Error in design validation: {e}")
            return [ValidationIssue(
                severity="critical",
                category="validation",
                description=f"Validation failed: {e}",
                location=None,
                suggested_fix="Check input parameters and try again",
                auto_fixable=False
            )]
    
    def _check_wall_thickness(self, geometry_info: Dict[str, Any], 
                            material: str) -> List[ValidationIssue]:
        """Check wall thickness against minimum requirements"""
        issues = []
        
        rule = self.validation_rules["minimum_wall_thickness"]
        min_thickness = rule["materials"].get(material, rule["default_threshold"])
        
        # Check if wall thickness information is available
        thickness = geometry_info.get("wall_thickness", 0)
        if thickness > 0 and thickness < min_thickness:
            issues.append(ValidationIssue(
                severity=rule["severity"],
                category=rule["category"],
                description=f"Wall thickness {thickness:.2f}mm below minimum {min_thickness:.2f}mm for {material}",
                location=None,
                suggested_fix=f"Increase wall thickness to at least {min_thickness:.2f}mm",
                auto_fixable=True
            ))
        
        return issues
    
    def _check_draft_angles(self, geometry_info: Dict[str, Any],
                          process: str) -> List[ValidationIssue]:
        """Check draft angles for manufacturing process"""
        issues = []
        
        rule = self.validation_rules["draft_angle"]
        required_angle = rule["processes"].get(process, rule["default_threshold"])
        
        draft_angle = geometry_info.get("draft_angle", 0)
        if draft_angle < required_angle:
            issues.append(ValidationIssue(
                severity=rule["severity"],
                category=rule["category"],
                description=f"Draft angle {draft_angle:.1f}° below required {required_angle:.1f}° for {process}",
                location=None,
                suggested_fix=f"Add minimum {required_angle:.1f}° draft angle to vertical surfaces",
                auto_fixable=True
            ))
        
        return issues
    
    def _check_corner_radii(self, geometry_info: Dict[str, Any],
                          material: str) -> List[ValidationIssue]:
        """Check corner radii for stress concentration"""
        issues = []
        
        rule = self.validation_rules["corner_radius"]
        min_radius = rule["materials"].get(material, rule["default_threshold"])
        
        corners = geometry_info.get("sharp_corners", [])
        for corner in corners:
            if corner.get("radius", 0) < min_radius:
                issues.append(ValidationIssue(
                    severity=rule["severity"],
                    category=rule["category"],
                    description=f"Sharp corner detected, radius {corner.get('radius', 0):.2f}mm",
                    location=corner.get("location"),
                    suggested_fix=f"Add minimum {min_radius:.2f}mm radius to reduce stress concentration",
                    auto_fixable=True
                ))
        
        return issues
    
    def _check_hole_positions(self, geometry_info: Dict[str, Any]) -> List[ValidationIssue]:
        """Check hole edge distances for structural integrity"""
        issues = []
        
        rule = self.validation_rules["hole_edge_distance"]
        
        holes = geometry_info.get("holes", [])
        for hole in holes:
            diameter = hole.get("diameter", 0)
            edge_distance = hole.get("edge_distance", 0)
            
            if edge_distance < diameter * rule["default_threshold"]:
                issues.append(ValidationIssue(
                    severity=rule["severity"],
                    category=rule["category"],
                    description=f"Hole too close to edge: {edge_distance:.2f}mm < {diameter * rule['default_threshold']:.2f}mm",
                    location=hole.get("location"),
                    suggested_fix=f"Move hole at least {diameter * rule['default_threshold']:.2f}mm from edge",
                    auto_fixable=True
                ))
        
        return issues
    
    def _check_aspect_ratios(self, geometry_info: Dict[str, Any]) -> List[ValidationIssue]:
        """Check geometric aspect ratios for manufacturability"""
        issues = []
        
        rule = self.validation_rules["aspect_ratio"]
        max_ratio = rule["default_threshold"]
        
        dimensions = geometry_info.get("dimensions", {})
        length = dimensions.get("length", 0)
        width = dimensions.get("width", 0)
        
        if width > 0 and length / width > max_ratio:
            issues.append(ValidationIssue(
                severity=rule["severity"],
                category=rule["category"],
                description=f"High aspect ratio {length/width:.1f}:1 may cause manufacturing issues",
                location=None,
                suggested_fix="Consider breaking into smaller sections or adding supports",
                auto_fixable=False
            ))
        
        return issues


class IntelligentDecisionEngine:
    """Main decision engine coordinating all intelligent decision-making capabilities"""
    
    def __init__(self):
        self.pattern_recognizer = DesignPatternRecognizer()
        self.constraint_solver = ConstraintSolverIntegration()
        self.optimizer = OptimizationEngine()
        self.error_recovery = ErrorRecoveryMechanism()
        self.validator = DesignValidator()
        
        self.decision_history = []
        self.performance_metrics = {
            "decisions_made": 0,
            "successful_optimizations": 0,
            "errors_recovered": 0,
            "patterns_recognized": 0
        }
    
    def make_design_decision(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make an intelligent design decision based on request context
        
        Args:
            request: Dictionary containing design request and context
            
        Returns:
            Dictionary containing decision results and recommendations
        """
        decision_start = time.time()
        
        try:
            decision_result = {
                "timestamp": decision_start,
                "request": request,
                "patterns_recognized": [],
                "optimization_results": None,
                "validation_issues": [],
                "recommendations": [],
                "execution_plan": [],
                "success": False
            }
            
            # Step 1: Recognize design patterns
            geometry_info = request.get("geometry_info", {})
            context = request.get("context", {})
            
            patterns = self.pattern_recognizer.recognize_pattern(geometry_info, context)
            decision_result["patterns_recognized"] = patterns
            self.performance_metrics["patterns_recognized"] += len(patterns)
            
            # Step 2: Generate recommendations based on patterns
            if patterns:
                best_pattern = patterns[0]  # Highest confidence
                decision_result["recommendations"].extend([
                    f"Recognized {best_pattern.pattern_type.value} pattern with {best_pattern.confidence:.1%} confidence",
                    f"Suggested dimensions: {best_pattern.suggested_dimensions}",
                    f"Required features: {best_pattern.required_features}",
                    f"Material recommendations: {best_pattern.material_recommendations}"
                ])
            
            # Step 3: Optimize parameters if requested
            optimization_request = request.get("optimization", {})
            if optimization_request:
                objective = OptimizationGoal(optimization_request.get("objective", "minimize_weight"))
                parameters = optimization_request.get("parameters", {})
                constraints = optimization_request.get("constraints", [])
                
                optimization_result = self.optimizer.optimize_parameters(
                    objective, parameters, constraints
                )
                decision_result["optimization_results"] = optimization_result
                
                if optimization_result.constraints_satisfied:
                    self.performance_metrics["successful_optimizations"] += 1
                    decision_result["recommendations"].extend(optimization_result.suggestions)
            
            # Step 4: Validate design
            material = request.get("material", "steel")
            process = request.get("manufacturing_process", "machining")
            
            validation_issues = self.validator.validate_design(
                geometry_info, material, process
            )
            decision_result["validation_issues"] = validation_issues
            
            # Step 5: Generate execution plan
            execution_plan = self._generate_execution_plan(
                patterns, optimization_result if 'optimization_result' in locals() else None,
                validation_issues, request
            )
            decision_result["execution_plan"] = execution_plan
            
            # Step 6: Final recommendations
            final_recommendations = self._generate_final_recommendations(
                patterns, validation_issues, context
            )
            decision_result["recommendations"].extend(final_recommendations)
            
            decision_result["success"] = True
            decision_result["processing_time"] = time.time() - decision_start
            
            # Update metrics
            self.performance_metrics["decisions_made"] += 1
            
            # Store in history
            self.decision_history.append(decision_result)
            
            return decision_result
            
        except Exception as e:
            logger.error(f"Error in intelligent decision making: {e}")
            return {
                "timestamp": decision_start,
                "success": False,
                "error": str(e),
                "recommendations": ["Manual intervention required due to decision engine error"]
            }
    
    def handle_operation_error(self, operation: str, error: Exception,
                             context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Handle operation errors with intelligent recovery
        
        Args:
            operation: Name of the failed operation
            error: Exception that occurred
            context: Operation context
            
        Returns:
            List of recovery strategies
        """
        error_details = {
            "operation": operation,
            "error_message": str(error),
            "error_type": type(error).__name__
        }
        
        recovery_strategies = self.error_recovery.handle_error(
            operation, error_details, context
        )
        
        if recovery_strategies:
            self.performance_metrics["errors_recovered"] += 1
        
        return recovery_strategies
    
    def _generate_execution_plan(self, patterns: List[DesignPattern],
                               optimization_result: OptimizationResult = None,
                               validation_issues: List[ValidationIssue] = None,
                               request: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Generate step-by-step execution plan"""
        plan = []
        
        # Start with pattern-based steps
        if patterns:
            best_pattern = patterns[0]
            
            # Add geometry creation steps
            plan.append({
                "step": 1,
                "action": "create_base_geometry",
                "description": f"Create base geometry for {best_pattern.pattern_type.value}",
                "parameters": best_pattern.suggested_dimensions,
                "estimated_time": 30  # seconds
            })
            
            # Add feature creation steps
            for i, feature in enumerate(best_pattern.required_features):
                plan.append({
                    "step": i + 2,
                    "action": f"add_{feature}",
                    "description": f"Add {feature.replace('_', ' ')}",
                    "parameters": {},
                    "estimated_time": 15
                })
        
        # Add optimization steps
        if optimization_result:
            plan.append({
                "step": len(plan) + 1,
                "action": "apply_optimization",
                "description": "Apply optimized parameters",
                "parameters": optimization_result.parameters,
                "estimated_time": 10
            })
        
        # Add validation fixes
        if validation_issues:
            auto_fixable_issues = [issue for issue in validation_issues if issue.auto_fixable]
            for issue in auto_fixable_issues:
                plan.append({
                    "step": len(plan) + 1,
                    "action": "fix_validation_issue",
                    "description": issue.suggested_fix,
                    "parameters": {"issue_type": issue.category},
                    "estimated_time": 20
                })
        
        return plan
    
    def _generate_final_recommendations(self, patterns: List[DesignPattern],
                                      validation_issues: List[ValidationIssue],
                                      context: Dict[str, Any]) -> List[str]:
        """Generate final design recommendations"""
        recommendations = []
        
        # Pattern-based recommendations
        if patterns:
            best_pattern = patterns[0]
            recommendations.extend(best_pattern.manufacturing_notes)
        
        # Validation-based recommendations
        critical_issues = [issue for issue in validation_issues if issue.severity == "critical"]
        if critical_issues:
            recommendations.append(f"Address {len(critical_issues)} critical design issues before manufacturing")
        
        warning_issues = [issue for issue in validation_issues if issue.severity == "warning"]
        if warning_issues:
            recommendations.append(f"Consider addressing {len(warning_issues)} design warnings for improved quality")
        
        # Context-based recommendations
        application = context.get("application", "")
        if "structural" in application.lower():
            recommendations.append("Consider FEA analysis for structural applications")
        
        if "high volume" in application.lower():
            recommendations.append("Optimize design for manufacturing efficiency and automation")
        
        return recommendations
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary of the decision engine"""
        total_decisions = self.performance_metrics["decisions_made"]
        
        return {
            "total_decisions": total_decisions,
            "successful_optimizations": self.performance_metrics["successful_optimizations"],
            "errors_recovered": self.performance_metrics["errors_recovered"],
            "patterns_recognized": self.performance_metrics["patterns_recognized"],
            "success_rate": (self.performance_metrics["successful_optimizations"] / 
                           max(1, total_decisions)) * 100,
            "average_patterns_per_decision": (self.performance_metrics["patterns_recognized"] / 
                                            max(1, total_decisions)),
            "recent_decisions": len(self.decision_history[-10:]),  # Last 10 decisions
        }


# Example usage and testing
if __name__ == "__main__":
    # Initialize decision engine
    engine = IntelligentDecisionEngine()
    
    # Example design request
    test_request = {
        "geometry_info": {
            "features": ["base_plate", "mounting_holes", "vertical_support"],
            "dimensions": {
                "length": 80.0,
                "width": 50.0,
                "height": 5.0,
                "hole_diameter": 6.0
            },
            "holes": [
                {"diameter": 6.0, "edge_distance": 8.0, "location": (10, 10, 0)}
            ]
        },
        "context": {
            "application": "structural mounting bracket",
            "environment": "industrial"
        },
        "optimization": {
            "objective": "minimize_weight",
            "parameters": {
                "length": {"min": 50.0, "max": 120.0},
                "width": {"min": 30.0, "max": 80.0},
                "height": {"min": 3.0, "max": 15.0}
            },
            "constraints": [
                {"type": "minimum_value", "parameter": "height", "value": 4.0}
            ]
        },
        "material": "aluminum",
        "manufacturing_process": "cnc_machining"
    }
    
    # Make design decision
    result = engine.make_design_decision(test_request)
    
    # Print results
    print("=== Intelligent Decision Engine Results ===")
    print(f"Success: {result['success']}")
    print(f"Processing time: {result.get('processing_time', 0):.2f} seconds")
    print(f"Patterns recognized: {len(result['patterns_recognized'])}")
    print(f"Validation issues: {len(result['validation_issues'])}")
    print(f"Execution steps: {len(result['execution_plan'])}")
    print(f"Recommendations: {len(result['recommendations'])}")
    
    if result['patterns_recognized']:
        best_pattern = result['patterns_recognized'][0]
        print(f"\nBest pattern: {best_pattern.pattern_type.value} ({best_pattern.confidence:.1%} confidence)")
    
    if result['optimization_results']:
        opt_result = result['optimization_results']
        print(f"\nOptimization: {opt_result.objective_value:.2f} (converged in {opt_result.iterations} iterations)")
    
    print(f"\nPerformance summary: {engine.get_performance_summary()}")
    
    print("\n=== Decision Engine Validation Complete ===")
