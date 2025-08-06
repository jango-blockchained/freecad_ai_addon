"""
Enhanced Parametric Modeling Library for FreeCAD AI Addon.

Provides advanced parametric modeling capabilities with feature trees,
parametric relationships, and design automation.
"""

from typing import Dict, Any, List, Optional
import logging

try:
    import FreeCAD as App
    import FreeCADGui as Gui
    import Part
    import PartDesign
    import Sketcher
except ImportError:
    # Mock for testing outside FreeCAD
    App = None
    Gui = None
    Part = None
    PartDesign = None
    Sketcher = None

logger = logging.getLogger(__name__)


class ParametricFeature:
    """Represents a parametric feature with dependencies and parameters."""
    
    def __init__(self, name: str, feature_type: str,
                 parameters: Dict[str, Any]):
        self.name = name
        self.feature_type = feature_type
        self.parameters = parameters
        self.dependencies = []
        self.dependent_features = []
        self.freecad_object = None
        self.is_suppressed = False
        
    def add_dependency(self, feature: 'ParametricFeature'):
        """Add a feature dependency."""
        if feature not in self.dependencies:
            self.dependencies.append(feature)
            feature.dependent_features.append(self)
    
    def update_parameter(self, param_name: str, value: Any):
        """Update a parameter value and mark for recompute."""
        self.parameters[param_name] = value
        return True
    
    def get_parameter_info(self) -> Dict[str, Any]:
        """Get information about all parameters."""
        return {
            'name': self.name,
            'type': self.feature_type,
            'parameters': self.parameters,
            'dependencies': [dep.name for dep in self.dependencies],
            'dependents': [dep.name for dep in self.dependent_features]
        }


class ParametricModelBuilder:
    """
    Advanced parametric modeling system with feature trees and relationships.
    
    Provides intelligent parametric modeling capabilities including:
    - Feature tree management
    - Parametric relationships and dependencies
    - Design automation and templates
    - Parameter optimization
    """
    
    def __init__(self):
        """Initialize the parametric model builder."""
        self.logger = logging.getLogger(f"{__name__}.ParametricModelBuilder")
        self.features = {}
        self.feature_tree = []
        self.parameters = {}
        self.relationships = {}
        self.design_intent = {}
        
        # Feature templates
        self.feature_templates = {
            'mounting_bracket': self._create_mounting_bracket_template,
            'bearing_mount': self._create_bearing_mount_template,
            'flange': self._create_flange_template,
            'shaft': self._create_shaft_template,
            'housing': self._create_housing_template,
            'gear': self._create_gear_template,
        }
        
        self.logger.info("Parametric Model Builder initialized")
    
    def create_parametric_feature(self, name: str, feature_type: str,
                                  parameters: Dict[str, Any],
                                  dependencies: Optional[List[str]] = None
                                  ) -> Dict[str, Any]:
        """
        Create a new parametric feature with dependencies.
        
        Args:
            name: Feature name
            feature_type: Type of feature (box, cylinder, extrude, etc.)
            parameters: Feature parameters
            dependencies: List of dependent feature names
            
        Returns:
            Feature creation result
        """
        try:
            # Create feature object
            feature = ParametricFeature(name, feature_type, parameters)
            
            # Add dependencies
            if dependencies:
                for dep_name in dependencies:
                    if dep_name in self.features:
                        feature.add_dependency(self.features[dep_name])
            
            # Create FreeCAD object based on feature type
            freecad_obj = self._create_freecad_feature(feature)
            feature.freecad_object = freecad_obj
            
            # Store feature
            self.features[name] = feature
            self.feature_tree.append(feature)
            
            return {
                'status': 'success',
                'feature_name': name,
                'freecad_object': freecad_obj.Name if freecad_obj else None,
                'parameters': parameters,
                'dependencies': dependencies or []
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create parametric feature {name}: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'feature_name': name
            }
    
    def update_feature_parameter(self, feature_name: str, parameter: str, 
                               value: Any) -> Dict[str, Any]:
        """
        Update a feature parameter and propagate changes.
        
        Args:
            feature_name: Name of the feature to update
            parameter: Parameter name
            value: New parameter value
            
        Returns:
            Update result with affected features
        """
        if feature_name not in self.features:
            return {
                'status': 'failed',
                'error': f"Feature {feature_name} not found"
            }
        
        try:
            feature = self.features[feature_name]
            old_value = feature.parameters.get(parameter)
            
            # Update parameter
            feature.update_parameter(parameter, value)
            
            # Update FreeCAD object
            if feature.freecad_object:
                self._update_freecad_object_parameter(feature.freecad_object, 
                                                    parameter, value)
            
            # Propagate changes to dependent features
            affected_features = self._propagate_parameter_changes(feature)
            
            # Recompute document
            if App and App.ActiveDocument:
                App.ActiveDocument.recompute()
            
            return {
                'status': 'success',
                'feature_name': feature_name,
                'parameter': parameter,
                'old_value': old_value,
                'new_value': value,
                'affected_features': [f.name for f in affected_features]
            }
            
        except Exception as e:
            self.logger.error(f"Failed to update parameter {parameter} for {feature_name}: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    def create_design_template(self, template_name: str, 
                             parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a design from a predefined template.
        
        Args:
            template_name: Name of the template
            parameters: Template parameters
            
        Returns:
            Template creation result
        """
        if template_name not in self.feature_templates:
            return {
                'status': 'failed',
                'error': f"Template {template_name} not found",
                'available_templates': list(self.feature_templates.keys())
            }
        
        try:
            template_func = self.feature_templates[template_name]
            result = template_func(parameters)
            
            return {
                'status': 'success',
                'template_name': template_name,
                'created_features': result.get('features', []),
                'parameters': parameters
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create template {template_name}: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    def get_feature_tree_info(self) -> Dict[str, Any]:
        """Get information about the current feature tree."""
        return {
            'total_features': len(self.features),
            'feature_list': [f.get_parameter_info() for f in self.feature_tree],
            'relationships': self._get_dependency_graph(),
            'parameters': self.parameters
        }
    
    def optimize_parameters(self, objective: str, constraints: Dict[str, Any],
                          variables: List[str]) -> Dict[str, Any]:
        """
        Optimize design parameters based on objective and constraints.
        
        Args:
            objective: Optimization objective (minimize_weight, maximize_strength, etc.)
            constraints: Design constraints
            variables: List of parameter names to optimize
            
        Returns:
            Optimization result
        """
        try:
            # Simple optimization example - can be enhanced with scipy or other optimizers
            original_values = {}
            best_values = {}
            best_objective = float('inf') if 'minimize' in objective else 0
            
            # Store original values
            for var in variables:
                feature_name, param_name = var.split('.')
                if feature_name in self.features:
                    original_values[var] = self.features[feature_name].parameters[param_name]
            
            # Simple grid search optimization (placeholder for advanced optimization)
            optimization_steps = 10
            for step in range(optimization_steps):
                # Generate test values
                test_values = self._generate_test_values(variables, constraints, step)
                
                # Apply test values
                for var, value in test_values.items():
                    feature_name, param_name = var.split('.')
                    self.update_feature_parameter(feature_name, param_name, value)
                
                # Evaluate objective
                objective_value = self._evaluate_objective(objective)
                
                # Check if better
                if self._is_better_objective(objective_value, best_objective, objective):
                    best_objective = objective_value
                    best_values = test_values.copy()
            
            # Apply best values
            for var, value in best_values.items():
                feature_name, param_name = var.split('.')
                self.update_feature_parameter(feature_name, param_name, value)
            
            return {
                'status': 'success',
                'objective': objective,
                'best_objective_value': best_objective,
                'optimized_parameters': best_values,
                'original_parameters': original_values,
                'improvement': self._calculate_improvement(best_objective, original_values, objective)
            }
            
        except Exception as e:
            self.logger.error(f"Parameter optimization failed: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    # ========================================================================
    # PRIVATE HELPER METHODS
    # ========================================================================
    
    def _create_freecad_feature(self, feature: ParametricFeature) -> Optional[Any]:
        """Create the corresponding FreeCAD object for a parametric feature."""
        if not App or not App.ActiveDocument:
            return None
        
        doc = App.ActiveDocument
        feature_type = feature.feature_type
        params = feature.parameters
        
        try:
            if feature_type == 'box':
                obj = doc.addObject("Part::Box", feature.name)
                obj.Length = params.get('length', 10.0)
                obj.Width = params.get('width', 10.0)
                obj.Height = params.get('height', 10.0)
                
            elif feature_type == 'cylinder':
                obj = doc.addObject("Part::Cylinder", feature.name)
                obj.Radius = params.get('radius', 5.0)
                obj.Height = params.get('height', 10.0)
                
            elif feature_type == 'extrude':
                # Assumes sketch exists
                sketch_name = params.get('sketch')
                if sketch_name and hasattr(doc, sketch_name):
                    obj = doc.addObject("PartDesign::Pad", feature.name)
                    obj.Profile = getattr(doc, sketch_name)
                    obj.Length = params.get('length', 10.0)
                else:
                    raise ValueError(f"Sketch {sketch_name} not found for extrusion")
                    
            else:
                raise ValueError(f"Unknown feature type: {feature_type}")
            
            doc.recompute()
            return obj
            
        except Exception as e:
            self.logger.error(f"Failed to create FreeCAD object for {feature.name}: {e}")
            return None
    
    def _update_freecad_object_parameter(self, obj: Any, parameter: str, value: Any):
        """Update a parameter on a FreeCAD object."""
        if hasattr(obj, parameter.capitalize()):
            setattr(obj, parameter.capitalize(), value)
        elif hasattr(obj, parameter):
            setattr(obj, parameter, value)
    
    def _propagate_parameter_changes(self, feature: ParametricFeature) -> List[ParametricFeature]:
        """Propagate parameter changes to dependent features."""
        affected = []
        
        for dependent in feature.dependent_features:
            # Update dependent feature based on relationships
            self._update_dependent_feature(dependent, feature)
            affected.append(dependent)
            
            # Recursively propagate
            affected.extend(self._propagate_parameter_changes(dependent))
        
        return affected
    
    def _update_dependent_feature(self, dependent: ParametricFeature, 
                                changed_feature: ParametricFeature):
        """Update a dependent feature based on changed feature."""
        # Implement relationship logic here
        # This is a placeholder for sophisticated dependency updates
        pass
    
    def _get_dependency_graph(self) -> Dict[str, List[str]]:
        """Get the dependency graph of features."""
        graph = {}
        for feature in self.features.values():
            graph[feature.name] = [dep.name for dep in feature.dependencies]
        return graph
    
    # ========================================================================
    # DESIGN TEMPLATES
    # ========================================================================
    
    def _create_mounting_bracket_template(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a mounting bracket template."""
        # Default parameters
        base_length = params.get('base_length', 50.0)
        base_width = params.get('base_width', 30.0)
        base_thickness = params.get('base_thickness', 5.0)
        bracket_height = params.get('bracket_height', 40.0)
        hole_diameter = params.get('hole_diameter', 6.5)
        hole_spacing = params.get('hole_spacing', 25.0)
        
        created_features = []
        
        # Create base plate
        base_result = self.create_parametric_feature(
            'base_plate',
            'box',
            {
                'length': base_length,
                'width': base_width,
                'height': base_thickness
            }
        )
        created_features.append('base_plate')
        
        # Create bracket arm
        arm_result = self.create_parametric_feature(
            'bracket_arm',
            'box',
            {
                'length': base_thickness,
                'width': base_width,
                'height': bracket_height
            },
            dependencies=['base_plate']
        )
        created_features.append('bracket_arm')
        
        return {
            'features': created_features,
            'template_type': 'mounting_bracket',
            'parameters': params
        }
    
    def _create_bearing_mount_template(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a bearing mount template."""
        bearing_diameter = params.get('bearing_diameter', 20.0)
        mount_height = params.get('mount_height', 30.0)
        base_diameter = params.get('base_diameter', bearing_diameter * 2)
        
        created_features = []
        
        # Create base cylinder
        base_result = self.create_parametric_feature(
            'bearing_base',
            'cylinder',
            {
                'radius': base_diameter / 2,
                'height': mount_height
            }
        )
        created_features.append('bearing_base')
        
        return {
            'features': created_features,
            'template_type': 'bearing_mount',
            'parameters': params
        }
    
    def _create_flange_template(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a flange template."""
        # Implementation for flange template
        return {'features': [], 'template_type': 'flange', 'parameters': params}
    
    def _create_shaft_template(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a shaft template."""
        # Implementation for shaft template
        return {'features': [], 'template_type': 'shaft', 'parameters': params}
    
    def _create_housing_template(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a housing template."""
        # Implementation for housing template
        return {'features': [], 'template_type': 'housing', 'parameters': params}
    
    def _create_gear_template(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a gear template."""
        # Implementation for gear template
        return {'features': [], 'template_type': 'gear', 'parameters': params}
    
    # ========================================================================
    # OPTIMIZATION HELPERS
    # ========================================================================
    
    def _generate_test_values(self, variables: List[str], constraints: Dict[str, Any], 
                            step: int) -> Dict[str, Any]:
        """Generate test values for optimization."""
        test_values = {}
        for var in variables:
            # Simple linear interpolation between min/max
            var_constraints = constraints.get(var, {})
            min_val = var_constraints.get('min', 0.1)
            max_val = var_constraints.get('max', 100.0)
            
            # Generate value based on step
            ratio = step / 10.0  # 10 steps
            value = min_val + ratio * (max_val - min_val)
            test_values[var] = value
        
        return test_values
    
    def _evaluate_objective(self, objective: str) -> float:
        """Evaluate the current objective function."""
        if not App or not App.ActiveDocument:
            return 0.0
        
        total_volume = 0.0
        total_area = 0.0
        
        for obj in App.ActiveDocument.Objects:
            if hasattr(obj, 'Shape') and obj.Shape.Volume > 0:
                total_volume += obj.Shape.Volume
                total_area += obj.Shape.Area
        
        if 'weight' in objective or 'volume' in objective:
            return total_volume
        elif 'surface' in objective or 'area' in objective:
            return total_area
        else:
            return total_volume  # Default
    
    def _is_better_objective(self, current: float, best: float, objective: str) -> bool:
        """Check if current objective value is better than best."""
        if 'minimize' in objective:
            return current < best
        else:
            return current > best
    
    def _calculate_improvement(self, best_value: float, original_params: Dict[str, Any],
                             objective: str) -> float:
        """Calculate improvement percentage."""
        # Placeholder implementation
        return 0.0
