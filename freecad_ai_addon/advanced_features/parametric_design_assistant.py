"""
Parametric Design Assistant for FreeCAD AI Addon.

This module provides intelligent assistance for creating parametric designs,
offering suggestions for configurable parameters, design patterns, and
optimization strategies.
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

# Import FreeCAD modules with error handling
try:
    import FreeCAD as App
    import Part
    import Sketcher
    import PartDesign

    FREECAD_AVAILABLE = True
except ImportError:
    FREECAD_AVAILABLE = False
    logging.warning("FreeCAD modules not available. Running in standalone mode.")

logger = logging.getLogger(__name__)


class DesignType(Enum):
    """Types of parametric designs the assistant can help with."""

    MECHANICAL_PART = "mechanical_part"
    STRUCTURAL_ELEMENT = "structural_element"
    ENCLOSURE = "enclosure"
    FASTENER = "fastener"
    BEARING_MOUNT = "bearing_mount"
    BRACKET = "bracket"
    HOUSING = "housing"
    CONNECTOR = "connector"
    GEAR = "gear"
    CUSTOM = "custom"


@dataclass
class Parameter:
    """Represents a parametric design parameter."""

    name: str
    value: float
    min_value: float
    max_value: float
    unit: str
    description: str
    is_driving: bool = True  # Whether this parameter drives other parameters
    dependencies: Optional[List[str]] = None  # Other parameters this depends on

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class DesignConstraint:
    """Represents a design constraint or rule."""

    name: str
    constraint_type: str  # 'ratio', 'minimum', 'maximum', 'formula'
    parameters: List[str]
    formula: str
    description: str
    severity: str = "warning"  # 'error', 'warning', 'info'


@dataclass
class DesignSuggestion:
    """Represents a design improvement suggestion."""

    title: str
    description: str
    parameters_affected: List[str]
    estimated_improvement: str
    implementation_steps: List[str]
    confidence: float  # 0.0 to 1.0


@dataclass
class ParametricDesign:
    """Represents a complete parametric design configuration."""

    name: str
    design_type: DesignType
    parameters: Dict[str, Parameter]
    constraints: List[DesignConstraint]
    creation_steps: List[str]
    validation_rules: List[str]
    suggested_materials: List[str]
    manufacturing_notes: List[str]


class ParametricDesignAssistant:
    """
    AI-powered assistant for creating and optimizing parametric designs.

    Features:
    - Suggests optimal parameter sets for common designs
    - Validates design constraints
    - Provides manufacturing recommendations
    - Offers design optimization suggestions
    """

    def __init__(self):
        """Initialize the parametric design assistant."""
        self.design_templates = self._load_design_templates()
        self.parameter_relationships = self._load_parameter_relationships()
        self.manufacturing_rules = self._load_manufacturing_rules()

    def suggest_design_parameters(
        self, design_type: DesignType, requirements: Dict[str, Any]
    ) -> ParametricDesign:
        """
        Suggest optimal parameters for a given design type and requirements.

        Args:
            design_type: Type of design to create
            requirements: Dictionary of design requirements (load, size, material, etc.)

        Returns:
            ParametricDesign object with suggested parameters and constraints
        """
        logger.info(f"Suggesting parameters for {design_type.value} design")

        if design_type == DesignType.BEARING_MOUNT:
            return self._create_bearing_mount_design(requirements)
        elif design_type == DesignType.BRACKET:
            return self._create_bracket_design(requirements)
        elif design_type == DesignType.ENCLOSURE:
            return self._create_enclosure_design(requirements)
        elif design_type == DesignType.GEAR:
            return self._create_gear_design(requirements)
        else:
            return self._create_generic_design(design_type, requirements)

    def _create_bearing_mount_design(
        self, requirements: Dict[str, Any]
    ) -> ParametricDesign:
        """Create a configurable bearing mount design."""
        bearing_diameter = requirements.get("bearing_diameter", 20.0)
        load_capacity = requirements.get("load_capacity", 1000.0)  # N
        mounting_style = requirements.get("mounting_style", "flange")

        # Calculate derived parameters based on engineering rules
        outer_diameter = bearing_diameter * 2.5
        flange_diameter = outer_diameter * 1.4
        thickness = max(bearing_diameter * 0.3, 5.0)
        bolt_circle_diameter = flange_diameter * 0.8
        bolt_count = 4 if flange_diameter < 80 else 6
        bolt_diameter = max(bearing_diameter * 0.2, 4.0)

        parameters = {
            "bearing_diameter": Parameter(
                name="bearing_diameter",
                value=bearing_diameter,
                min_value=6.0,
                max_value=200.0,
                unit="mm",
                description="Inner diameter for bearing",
                is_driving=True,
            ),
            "outer_diameter": Parameter(
                name="outer_diameter",
                value=outer_diameter,
                min_value=bearing_diameter * 2.0,
                max_value=bearing_diameter * 3.0,
                unit="mm",
                description="Outer diameter of mount",
                dependencies=["bearing_diameter"],
            ),
            "flange_diameter": Parameter(
                name="flange_diameter",
                value=flange_diameter,
                min_value=outer_diameter * 1.2,
                max_value=outer_diameter * 1.6,
                unit="mm",
                description="Flange mounting diameter",
                dependencies=["outer_diameter"],
            ),
            "thickness": Parameter(
                name="thickness",
                value=thickness,
                min_value=3.0,
                max_value=bearing_diameter * 0.5,
                unit="mm",
                description="Mount thickness",
                dependencies=["bearing_diameter"],
            ),
            "bolt_circle_diameter": Parameter(
                name="bolt_circle_diameter",
                value=bolt_circle_diameter,
                min_value=flange_diameter * 0.6,
                max_value=flange_diameter * 0.9,
                unit="mm",
                description="Bolt circle diameter",
                dependencies=["flange_diameter"],
            ),
            "bolt_count": Parameter(
                name="bolt_count",
                value=bolt_count,
                min_value=3,
                max_value=12,
                unit="count",
                description="Number of mounting bolts",
                dependencies=["flange_diameter"],
            ),
            "bolt_diameter": Parameter(
                name="bolt_diameter",
                value=bolt_diameter,
                min_value=3.0,
                max_value=20.0,
                unit="mm",
                description="Bolt hole diameter",
                dependencies=["bearing_diameter", "load_capacity"],
            ),
        }

        constraints = [
            DesignConstraint(
                name="bearing_clearance",
                constraint_type="minimum",
                parameters=["outer_diameter", "bearing_diameter"],
                formula="outer_diameter >= bearing_diameter * 2.0",
                description="Ensure adequate wall thickness around bearing",
            ),
            DesignConstraint(
                name="flange_ratio",
                constraint_type="ratio",
                parameters=["flange_diameter", "outer_diameter"],
                formula="flange_diameter <= outer_diameter * 1.6",
                description="Maintain reasonable flange proportions",
            ),
            DesignConstraint(
                name="bolt_clearance",
                constraint_type="minimum",
                parameters=["bolt_circle_diameter", "bolt_diameter"],
                formula="bolt_circle_diameter >= bolt_diameter * 8",
                description="Ensure adequate bolt edge distance",
            ),
        ]

        creation_steps = [
            "1. Create base cylinder with outer_diameter and thickness",
            "2. Create bearing bore with bearing_diameter",
            "3. Create flange with flange_diameter",
            "4. Create bolt pattern on bolt_circle_diameter",
            "5. Add fillets and chamfers for stress relief",
            "6. Apply material properties and validate design",
        ]

        return ParametricDesign(
            name="Configurable Bearing Mount",
            design_type=DesignType.BEARING_MOUNT,
            parameters=parameters,
            constraints=constraints,
            creation_steps=creation_steps,
            validation_rules=[
                "Check bearing fit tolerance (H7/h6)",
                "Verify bolt torque specifications",
                "Calculate maximum allowable load",
                "Check for stress concentrations",
            ],
            suggested_materials=[
                "Aluminum 6061-T6",
                "Steel 1018",
                "Stainless Steel 304",
            ],
            manufacturing_notes=[
                "Machine bearing bore to H7 tolerance",
                "Deburr all edges, especially bolt holes",
                "Consider anodizing for aluminum parts",
                "Specify surface roughness for bearing surface",
            ],
        )

    def _create_bracket_design(self, requirements: Dict[str, Any]) -> ParametricDesign:
        """Create a configurable bracket design."""
        load = requirements.get("load", 500.0)  # N
        span = requirements.get("span", 100.0)  # mm
        mounting_holes = requirements.get("mounting_holes", 4)

        # Calculate parameters based on structural requirements
        thickness = max(span * 0.05, 3.0)
        width = span * 0.4
        height = span * 0.6
        hole_diameter = max(load / 200.0, 5.0)
        gusset_radius = min(width * 0.3, 20.0)

        parameters = {
            "span": Parameter(
                name="span",
                value=span,
                min_value=20.0,
                max_value=500.0,
                unit="mm",
                description="Distance between mounting points",
                is_driving=True,
            ),
            "thickness": Parameter(
                name="thickness",
                value=thickness,
                min_value=2.0,
                max_value=20.0,
                unit="mm",
                description="Bracket material thickness",
                dependencies=["span", "load"],
            ),
            "width": Parameter(
                name="width",
                value=width,
                min_value=10.0,
                max_value=200.0,
                unit="mm",
                description="Bracket width",
                dependencies=["span"],
            ),
            "height": Parameter(
                name="height",
                value=height,
                min_value=15.0,
                max_value=300.0,
                unit="mm",
                description="Bracket height",
                dependencies=["span"],
            ),
            "hole_diameter": Parameter(
                name="hole_diameter",
                value=hole_diameter,
                min_value=3.0,
                max_value=25.0,
                unit="mm",
                description="Mounting hole diameter",
                dependencies=["load"],
            ),
            "gusset_radius": Parameter(
                name="gusset_radius",
                value=gusset_radius,
                min_value=5.0,
                max_value=50.0,
                unit="mm",
                description="Gusset fillet radius",
                dependencies=["width"],
            ),
        }

        constraints = [
            DesignConstraint(
                name="thickness_ratio",
                constraint_type="ratio",
                parameters=["thickness", "span"],
                formula="thickness >= span * 0.02",
                description="Ensure adequate thickness for structural integrity",
            ),
            DesignConstraint(
                name="hole_edge_distance",
                constraint_type="minimum",
                parameters=["hole_diameter", "width"],
                formula="width >= hole_diameter * 3",
                description="Maintain minimum edge distance for holes",
            ),
        ]

        creation_steps = [
            "1. Create base plate with width x height x thickness",
            "2. Create gusset triangles for reinforcement",
            "3. Add mounting holes at specified locations",
            "4. Apply fillets with gusset_radius",
            "5. Add chamfers to reduce stress concentrations",
            "6. Optimize for weight while maintaining strength",
        ]

        return ParametricDesign(
            name="Configurable L-Bracket",
            design_type=DesignType.BRACKET,
            parameters=parameters,
            constraints=constraints,
            creation_steps=creation_steps,
            validation_rules=[
                "Perform FEA analysis for maximum load",
                "Check bolt shear and bearing stress",
                "Verify buckling resistance",
                "Calculate safety factor",
            ],
            suggested_materials=["Aluminum 5052", "Steel A36", "Stainless Steel 316"],
            manufacturing_notes=[
                "Laser cut or waterjet recommended",
                "Deburr all cut edges",
                "Consider powder coating for corrosion resistance",
                "Specify hole tolerances based on fastener type",
            ],
        )

    def _create_enclosure_design(
        self, requirements: Dict[str, Any]
    ) -> ParametricDesign:
        """Create a configurable enclosure design."""
        # Implementation for enclosure design
        internal_width = requirements.get("internal_width", 100.0)
        internal_height = requirements.get("internal_height", 80.0)
        internal_depth = requirements.get("internal_depth", 60.0)
        wall_thickness = requirements.get("wall_thickness", 2.0)

        # Calculate external dimensions
        external_width = internal_width + 2 * wall_thickness
        external_height = internal_height + 2 * wall_thickness
        external_depth = internal_depth + 2 * wall_thickness

        parameters = {
            "internal_width": Parameter(
                name="internal_width",
                value=internal_width,
                min_value=20.0,
                max_value=500.0,
                unit="mm",
                description="Internal cavity width",
                is_driving=True,
            ),
            "internal_height": Parameter(
                name="internal_height",
                value=internal_height,
                min_value=15.0,
                max_value=400.0,
                unit="mm",
                description="Internal cavity height",
                is_driving=True,
            ),
            "internal_depth": Parameter(
                name="internal_depth",
                value=internal_depth,
                min_value=10.0,
                max_value=300.0,
                unit="mm",
                description="Internal cavity depth",
                is_driving=True,
            ),
            "wall_thickness": Parameter(
                name="wall_thickness",
                value=wall_thickness,
                min_value=1.0,
                max_value=10.0,
                unit="mm",
                description="Wall thickness",
                is_driving=True,
            ),
        }

        creation_steps = [
            "1. Create outer shell box",
            "2. Create inner cavity",
            "3. Add mounting features",
            "4. Create lid with gasket groove",
            "5. Add ventilation holes if needed",
            "6. Apply finishing features",
        ]

        return ParametricDesign(
            name="Configurable Enclosure",
            design_type=DesignType.ENCLOSURE,
            parameters=parameters,
            constraints=[],
            creation_steps=creation_steps,
            validation_rules=[
                "Check IP rating requirements",
                "Verify thermal management",
            ],
            suggested_materials=["ABS Plastic", "Aluminum", "Polycarbonate"],
            manufacturing_notes=[
                "Consider draft angles for molding",
                "Add gasket grooves for sealing",
            ],
        )

    def _create_gear_design(self, requirements: Dict[str, Any]) -> ParametricDesign:
        """Create a configurable gear design."""
        # Implementation for gear design
        module = requirements.get("module", 2.0)
        teeth_count = requirements.get("teeth_count", 20)
        pressure_angle = requirements.get("pressure_angle", 20.0)

        # Calculate gear parameters
        pitch_diameter = module * teeth_count
        outside_diameter = pitch_diameter + 2 * module
        root_diameter = pitch_diameter - 2.5 * module

        parameters = {
            "module": Parameter(
                name="module",
                value=module,
                min_value=0.5,
                max_value=10.0,
                unit="mm",
                description="Gear module (tooth size)",
                is_driving=True,
            ),
            "teeth_count": Parameter(
                name="teeth_count",
                value=teeth_count,
                min_value=8,
                max_value=200,
                unit="count",
                description="Number of teeth",
                is_driving=True,
            ),
            "pressure_angle": Parameter(
                name="pressure_angle",
                value=pressure_angle,
                min_value=14.5,
                max_value=25.0,
                unit="degrees",
                description="Pressure angle",
                is_driving=True,
            ),
        }

        creation_steps = [
            "1. Calculate gear geometry parameters",
            "2. Create involute tooth profile",
            "3. Create circular pattern of teeth",
            "4. Add central hub and keyway",
            "5. Apply finishing operations",
            "6. Validate gear mesh compatibility",
        ]

        return ParametricDesign(
            name="Configurable Spur Gear",
            design_type=DesignType.GEAR,
            parameters=parameters,
            constraints=[],
            creation_steps=creation_steps,
            validation_rules=[
                "Check gear ratio compatibility",
                "Verify contact stress",
            ],
            suggested_materials=["Steel 4140", "Brass", "Nylon"],
            manufacturing_notes=[
                "Hobbing or gear cutting required",
                "Heat treatment for steel gears",
            ],
        )

    def _create_generic_design(
        self, design_type: DesignType, requirements: Dict[str, Any]
    ) -> ParametricDesign:
        """Create a generic parametric design template."""
        return ParametricDesign(
            name=f"Generic {design_type.value.replace('_', ' ').title()}",
            design_type=design_type,
            parameters={},
            constraints=[],
            creation_steps=[
                "1. Define design requirements",
                "2. Create parametric model",
            ],
            validation_rules=["Validate design against requirements"],
            suggested_materials=["Material TBD"],
            manufacturing_notes=["Manufacturing process TBD"],
        )

    def validate_design(self, design: ParametricDesign) -> List[str]:
        """
        Validate a parametric design against its constraints.

        Args:
            design: ParametricDesign to validate

        Returns:
            List of validation issues (empty if valid)
        """
        issues = []

        # Check parameter constraints
        for param_name, param in design.parameters.items():
            if param.value < param.min_value:
                issues.append(
                    f"{param_name} value {param.value} is below minimum {param.min_value}"
                )
            if param.value > param.max_value:
                issues.append(
                    f"{param_name} value {param.value} exceeds maximum {param.max_value}"
                )

        # Check design constraints
        for constraint in design.constraints:
            if not self._evaluate_constraint(constraint, design.parameters):
                issues.append(f"Constraint violated: {constraint.description}")

        return issues

    def _evaluate_constraint(
        self, constraint: DesignConstraint, parameters: Dict[str, Parameter]
    ) -> bool:
        """Evaluate if a constraint is satisfied."""
        # Minimal safe evaluator: only allow parameter names, numbers, operators
        # Supported operators: + - * / <= >= < > == and parentheses
        expr = constraint.formula
        # Build a local namespace of parameter values
        local_vals = {name: p.value for name, p in parameters.items()}
        # Reject any disallowed characters (very conservative)
        import re

        if not re.fullmatch(r"[\w\d_\s+\-*/().><=]*", expr):
            logger.warning(
                "Constraint '%s' contains disallowed characters", constraint.name
            )
            return False
        try:
            result = eval(
                expr, {"__builtins__": {}}, local_vals
            )  # nosec: constrained context
            return bool(result)
        except Exception as e:  # noqa: BLE001
            logger.error("Constraint '%s' evaluation failed: %s", constraint.name, e)
            return False

    def suggest_improvements(
        self, design: ParametricDesign, optimization_goals: List[str]
    ) -> List[DesignSuggestion]:
        """
        Suggest improvements to a parametric design.

        Args:
            design: Current design to improve
            optimization_goals: List of goals ('weight', 'strength', 'cost', 'manufacturability')

        Returns:
            List of improvement suggestions
        """
        suggestions = []

        if "weight" in optimization_goals:
            suggestions.append(
                DesignSuggestion(
                    title="Weight Optimization",
                    description="Reduce material usage while maintaining structural integrity",
                    parameters_affected=["thickness", "width"],
                    estimated_improvement="15-25% weight reduction",
                    implementation_steps=[
                        "Perform topology optimization analysis",
                        "Identify areas for material removal",
                        "Add ribs for local stiffening",
                        "Validate with FEA analysis",
                    ],
                    confidence=0.8,
                )
            )

        if "manufacturability" in optimization_goals:
            suggestions.append(
                DesignSuggestion(
                    title="Manufacturing Optimization",
                    description="Improve design for easier manufacturing",
                    parameters_affected=["gusset_radius", "hole_diameter"],
                    estimated_improvement="20-30% reduction in manufacturing time",
                    implementation_steps=[
                        "Add draft angles for molding/casting",
                        "Standardize hole sizes",
                        "Minimize number of operations",
                        "Consider tooling accessibility",
                    ],
                    confidence=0.9,
                )
            )

        return suggestions

    def generate_freecad_script(self, design: ParametricDesign) -> str:
        """
        Generate FreeCAD Python script to create the parametric design.

        Args:
            design: ParametricDesign to implement

        Returns:
            Python script string for FreeCAD
        """
        script_lines = [
            "# Generated FreeCAD script for parametric design",
            "import FreeCAD as App",
            "import Part",
            "import Sketcher",
            "",
            "# Create new document",
            "doc = App.newDocument('ParametricDesign')",
            "",
            "# Parameters",
        ]

        # Add parameter definitions
        for param_name, param in design.parameters.items():
            script_lines.append(f"{param_name} = {param.value}  # {param.description}")

        script_lines.extend(
            [
                "",
                "# Design creation steps",
                "# " + "\\n# ".join(design.creation_steps),
                "",
                "# Implementation based on design type",
            ]
        )

        if design.design_type == DesignType.BEARING_MOUNT:
            script_lines.extend(self._generate_bearing_mount_script(design))
        elif design.design_type == DesignType.BRACKET:
            script_lines.extend(self._generate_bracket_script(design))

        script_lines.extend(
            [
                "",
                "# Recompute document",
                "doc.recompute()",
                "",
                "# Save document",
                "# doc.saveAs('parametric_design.FCStd')",
            ]
        )

        return "\\n".join(script_lines)

    def _generate_bearing_mount_script(self, design: ParametricDesign) -> List[str]:
        """Generate specific script for bearing mount."""
        return [
            "# Create bearing mount",
            "mount = doc.addObject('Part::Cylinder', 'BearingMount')",
            "mount.Radius = outer_diameter / 2",
            "mount.Height = thickness",
            "",
            "# Create bearing bore",
            "bore = doc.addObject('Part::Cylinder', 'BearingBore')",
            "bore.Radius = bearing_diameter / 2",
            "bore.Height = thickness * 1.1",
            "",
            "# Cut bore from mount",
            "cut = doc.addObject('Part::Cut', 'Mount_Cut')",
            "cut.Base = mount",
            "cut.Tool = bore",
        ]

    def _generate_bracket_script(self, design: ParametricDesign) -> List[str]:
        """Generate specific script for bracket."""
        return [
            "# Create bracket base",
            "base = doc.addObject('Part::Box', 'BracketBase')",
            "base.Length = width",
            "base.Width = height",
            "base.Height = thickness",
        ]

    def _load_design_templates(self) -> Dict[str, Any]:
        """Load predefined design templates."""
        return {
            "bearing_mount": {
                "default_parameters": {
                    "bearing_diameter": 20.0,
                    "load_capacity": 1000.0,
                }
            },
            "bracket": {"default_parameters": {"load": 500.0, "span": 100.0}},
        }

    def _load_parameter_relationships(self) -> Dict[str, Any]:
        """Load parameter relationship rules."""
        return {
            "bearing_mount": {
                "outer_diameter": "bearing_diameter * 2.5",
                "thickness": "max(bearing_diameter * 0.3, 5.0)",
            }
        }

    def _load_manufacturing_rules(self) -> Dict[str, Any]:
        """Load manufacturing constraint rules."""
        return {
            "minimum_wall_thickness": {"aluminum": 1.5, "steel": 1.0, "plastic": 0.8},
            "minimum_hole_diameter": {
                "drilling": 1.0,
                "laser_cutting": 0.5,
                "waterjet": 0.8,
            },
        }


def create_bearing_mount_example():
    """Example function showing how to use the parametric design assistant."""
    assistant = ParametricDesignAssistant()

    requirements = {
        "bearing_diameter": 25.0,
        "load_capacity": 1500.0,
        "mounting_style": "flange",
    }

    design = assistant.suggest_design_parameters(DesignType.BEARING_MOUNT, requirements)

    print(f"Created design: {design.name}")
    print("Parameters:")
    for name, param in design.parameters.items():
        print(f"  {name}: {param.value} {param.unit} - {param.description}")

    # Validate design
    issues = assistant.validate_design(design)
    if issues:
        print("Validation issues:", issues)
    else:
        print("Design validation passed!")

    # Get improvement suggestions
    suggestions = assistant.suggest_improvements(
        design, ["weight", "manufacturability"]
    )
    print(f"\\nImprovement suggestions: {len(suggestions)}")
    for suggestion in suggestions:
        print(f"  - {suggestion.title}: {suggestion.description}")

    # Generate FreeCAD script
    script = assistant.generate_freecad_script(design)
    print("\\nGenerated FreeCAD script:")
    print(script[:500] + "..." if len(script) > 500 else script)


if __name__ == "__main__":
    create_bearing_mount_example()
