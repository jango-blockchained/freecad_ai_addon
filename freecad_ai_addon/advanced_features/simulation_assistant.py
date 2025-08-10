"""
Simulation Assistant for FreeCAD AI Addon.

This module provides AI-powered simulation setup assistance for FEA, CFD, thermal,
and other simulation types. Automates mesh generation, boundary conditions,
material assignments, and analysis configuration.
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

# Import FreeCAD modules with error handling
try:
    import FreeCAD as App

    FREECAD_AVAILABLE = True
except ImportError:
    FREECAD_AVAILABLE = False
    logging.warning("FreeCAD modules not available. Running in standalone mode.")

logger = logging.getLogger(__name__)


class SimulationType(Enum):
    """Types of simulations supported."""

    STRUCTURAL_FEA = "structural_fea"
    THERMAL = "thermal"
    CFD = "cfd"
    MODAL = "modal"
    FATIGUE = "fatigue"
    BUCKLING = "buckling"
    VIBRATION = "vibration"
    ELECTROMAGNETICS = "electromagnetics"
    FLUID_STRUCTURE = "fluid_structure"
    TRANSIENT = "transient"


class BoundaryConditionType(Enum):
    """Types of boundary conditions."""

    FIXED_CONSTRAINT = "fixed_constraint"
    FORCE_LOAD = "force_load"
    PRESSURE_LOAD = "pressure_load"
    DISPLACEMENT = "displacement"
    TEMPERATURE = "temperature"
    HEAT_FLUX = "heat_flux"
    CONVECTION = "convection"
    VELOCITY_INLET = "velocity_inlet"
    PRESSURE_OUTLET = "pressure_outlet"
    SYMMETRY = "symmetry"
    CONTACT = "contact"


class MeshQuality(Enum):
    """Mesh quality levels."""

    COARSE = "coarse"
    MEDIUM = "medium"
    FINE = "fine"
    VERY_FINE = "very_fine"
    CUSTOM = "custom"


@dataclass
class MaterialProperties:
    """Material properties for simulation."""

    name: str
    density: float  # kg/m³
    elastic_modulus: float  # Pa
    poisson_ratio: float
    yield_strength: float  # Pa
    thermal_conductivity: float  # W/m·K
    specific_heat: float  # J/kg·K
    thermal_expansion: float  # 1/K


@dataclass
class BoundaryCondition:
    """Represents a boundary condition."""

    bc_type: BoundaryConditionType
    location: str  # Face, edge, or vertex identifier
    magnitude: float
    direction: Optional[List[float]]  # Direction vector [x, y, z]
    description: str


@dataclass
class MeshSettings:
    """Mesh generation settings."""

    quality: MeshQuality
    element_size: float  # mm
    element_type: str  # "tetrahedral", "hexahedral", "mixed"
    refinement_regions: List[str]  # Regions requiring mesh refinement
    growth_rate: float  # Mesh growth rate
    curvature_based: bool  # Use curvature-based refinement


@dataclass
class LoadCase:
    """Represents a load case for analysis."""

    name: str
    description: str
    boundary_conditions: List[BoundaryCondition]
    load_factor: float = 1.0


@dataclass
class SimulationSetup:
    """Complete simulation setup configuration."""

    simulation_type: SimulationType
    object_name: str
    material: MaterialProperties
    mesh_settings: MeshSettings
    load_cases: List[LoadCase]
    analysis_settings: Dict[str, Any]
    expected_results: List[str]
    convergence_criteria: Dict[str, float]


@dataclass
class SimulationRecommendation:
    """Simulation setup recommendations."""

    setup: SimulationSetup
    confidence: float
    reasoning: List[str]
    warnings: List[str]
    estimated_runtime: str
    required_resources: Dict[str, str]


class SimulationAssistant:
    """
    AI-powered simulation setup assistant for CAD models.

    Provides intelligent assistance for:
    - Simulation type selection based on analysis goals
    - Automatic material property assignment
    - Mesh generation optimization
    - Boundary condition recommendations
    - Analysis parameter configuration
    - Result interpretation guidance
    """

    def __init__(self):
        """Initialize the simulation assistant."""
        self.material_database = self._load_material_database()
        self.simulation_templates = self._load_simulation_templates()
        self.mesh_guidelines = self._load_mesh_guidelines()
        self.setup_history = []

    def recommend_simulation_setup(
        self,
        object_name: str,
        analysis_goal: str,
        material_name: str = "steel_1018",
        loading_conditions: Optional[List[str]] = None,
        constraints: Optional[List[str]] = None,
    ) -> SimulationRecommendation:
        """
        Recommend complete simulation setup based on analysis goals.

        Args:
            object_name: Name of the FreeCAD object to analyze
            analysis_goal: Goal of analysis (e.g., "stress analysis", "deflection", "vibration")
            material_name: Material to use for analysis
            loading_conditions: List of loading descriptions
            constraints: List of constraint descriptions

        Returns:
            SimulationRecommendation with complete setup configuration

        Example:
            assistant = SimulationAssistant()

            recommendation = assistant.recommend_simulation_setup(
                "Bracket001",
                "stress analysis under static load",
                "aluminum_6061",
                loading_conditions=["100N downward force on top surface"],
                constraints=["fixed at mounting holes"]
            )
        """
        if not FREECAD_AVAILABLE:
            logger.warning("FreeCAD not available, returning mock simulation setup")
            return self._create_mock_simulation_recommendation(
                object_name, analysis_goal
            )

        logger.info(f"Recommending simulation setup for: {object_name}")
        logger.info(f"Analysis goal: {analysis_goal}")

        try:
            doc = App.activeDocument()
            if not doc:
                raise ValueError("No active document found")

            obj = doc.getObject(object_name)
            if not obj:
                raise ValueError(f"Object '{object_name}' not found")

            # Determine simulation type
            sim_type = self._determine_simulation_type(analysis_goal)

            # Get material properties
            material = self._get_material_properties(material_name)

            # Generate mesh settings
            mesh_settings = self._recommend_mesh_settings(obj, sim_type)

            # Generate boundary conditions
            boundary_conditions = self._recommend_boundary_conditions(
                obj, loading_conditions or [], constraints or []
            )

            # Create load cases
            load_cases = [
                LoadCase(
                    name="Primary Load Case",
                    description="Main loading scenario",
                    boundary_conditions=boundary_conditions,
                )
            ]

            # Configure analysis settings
            analysis_settings = self._get_analysis_settings(sim_type)

            # Create simulation setup
            setup = SimulationSetup(
                simulation_type=sim_type,
                object_name=object_name,
                material=material,
                mesh_settings=mesh_settings,
                load_cases=load_cases,
                analysis_settings=analysis_settings,
                expected_results=self._get_expected_results(sim_type),
                convergence_criteria=self._get_convergence_criteria(sim_type),
            )

            # Generate recommendation
            recommendation = SimulationRecommendation(
                setup=setup,
                confidence=0.85,
                reasoning=self._generate_reasoning(analysis_goal, sim_type),
                warnings=self._generate_warnings(setup),
                estimated_runtime=self._estimate_runtime(setup),
                required_resources=self._estimate_resources(setup),
            )

            self.setup_history.append(recommendation)
            return recommendation

        except Exception as e:
            logger.error(f"Simulation setup recommendation failed: {e}")
            return self._create_error_recommendation(object_name, str(e))

    def optimize_mesh_settings(
        self,
        object_name: str,
        simulation_type: SimulationType,
        accuracy_target: str = "medium",
    ) -> MeshSettings:
        """
        Optimize mesh settings for specific simulation type and accuracy target.

        Args:
            object_name: Name of the FreeCAD object
            simulation_type: Type of simulation to optimize for
            accuracy_target: Desired accuracy level ("low", "medium", "high")

        Returns:
            Optimized MeshSettings
        """
        logger.info(
            f"Optimizing mesh for {simulation_type.value} with {accuracy_target} accuracy"
        )

        # Base mesh settings by accuracy target
        accuracy_settings = {
            "low": {
                "quality": MeshQuality.COARSE,
                "element_size": 5.0,
                "growth_rate": 1.3,
            },
            "medium": {
                "quality": MeshQuality.MEDIUM,
                "element_size": 2.0,
                "growth_rate": 1.2,
            },
            "high": {
                "quality": MeshQuality.FINE,
                "element_size": 1.0,
                "growth_rate": 1.1,
            },
        }

        base_settings = accuracy_settings.get(
            accuracy_target, accuracy_settings["medium"]
        )

        # Simulation-specific adjustments
        if simulation_type == SimulationType.CFD:
            # CFD needs boundary layer refinement
            base_settings["element_type"] = "tetrahedral"
            base_settings["refinement_regions"] = ["boundary_layer", "inlet", "outlet"]
        elif simulation_type == SimulationType.MODAL:
            # Modal analysis needs consistent elements
            base_settings["element_type"] = "hexahedral"
            base_settings["curvature_based"] = True
        else:
            # Default structural analysis
            base_settings["element_type"] = "tetrahedral"
            base_settings["refinement_regions"] = ["stress_concentration_areas"]

        return MeshSettings(
            quality=base_settings["quality"],
            element_size=base_settings["element_size"],
            element_type=base_settings["element_type"],
            refinement_regions=base_settings.get("refinement_regions", []),
            growth_rate=base_settings["growth_rate"],
            curvature_based=base_settings.get("curvature_based", False),
        )

    def suggest_boundary_conditions(
        self,
        object_name: str,
        simulation_type: SimulationType,
        loading_description: List[str],
        constraint_description: List[str],
    ) -> List[BoundaryCondition]:
        """
        Suggest appropriate boundary conditions based on descriptions.

        Args:
            object_name: Name of the FreeCAD object
            simulation_type: Type of simulation
            loading_description: Natural language description of loads
            constraint_description: Natural language description of constraints

        Returns:
            List of recommended BoundaryCondition objects
        """
        boundary_conditions = []

        # Process constraints
        for constraint in constraint_description:
            if "fixed" in constraint.lower() or "clamped" in constraint.lower():
                boundary_conditions.append(
                    BoundaryCondition(
                        bc_type=BoundaryConditionType.FIXED_CONSTRAINT,
                        location="mounting_faces",
                        magnitude=0.0,
                        direction=None,
                        description=f"Fixed constraint: {constraint}",
                    )
                )
            elif "symmetry" in constraint.lower():
                boundary_conditions.append(
                    BoundaryCondition(
                        bc_type=BoundaryConditionType.SYMMETRY,
                        location="symmetry_plane",
                        magnitude=0.0,
                        direction=None,
                        description=f"Symmetry condition: {constraint}",
                    )
                )

        # Process loads
        for load in loading_description:
            if "force" in load.lower():
                # Extract force magnitude if possible
                import re

                force_match = re.search(r"(\\d+(?:\\.\\d+)?)\\s*[nN]", load)
                magnitude = float(force_match.group(1)) if force_match else 100.0

                boundary_conditions.append(
                    BoundaryCondition(
                        bc_type=BoundaryConditionType.FORCE_LOAD,
                        location="loading_surface",
                        magnitude=magnitude,
                        direction=[0, 0, -1]
                        if "downward" in load.lower()
                        else [0, 0, 1],
                        description=f"Applied force: {load}",
                    )
                )
            elif "pressure" in load.lower():
                # Extract pressure magnitude if possible
                import re

                pressure_match = re.search(r"(\\d+(?:\\.\\d+)?)\\s*[pP][aA]", load)
                magnitude = float(pressure_match.group(1)) if pressure_match else 1000.0

                boundary_conditions.append(
                    BoundaryCondition(
                        bc_type=BoundaryConditionType.PRESSURE_LOAD,
                        location="pressure_surface",
                        magnitude=magnitude,
                        direction=None,
                        description=f"Applied pressure: {load}",
                    )
                )

        return boundary_conditions

    def validate_simulation_setup(self, setup: SimulationSetup) -> Dict[str, List[str]]:
        """
        Validate simulation setup and identify potential issues.

        Args:
            setup: SimulationSetup to validate

        Returns:
            Dictionary with validation results: {"errors": [...], "warnings": [...], "info": [...]}
        """
        validation = {"errors": [], "warnings": [], "info": []}

        # Check for essential boundary conditions
        has_constraints = any(
            bc.bc_type == BoundaryConditionType.FIXED_CONSTRAINT
            for load_case in setup.load_cases
            for bc in load_case.boundary_conditions
        )

        if not has_constraints:
            validation["errors"].append(
                "No fixed constraints found - model will be unconstrained"
            )

        # Check for loads
        has_loads = any(
            bc.bc_type
            in [BoundaryConditionType.FORCE_LOAD, BoundaryConditionType.PRESSURE_LOAD]
            for load_case in setup.load_cases
            for bc in load_case.boundary_conditions
        )

        if not has_loads:
            validation["warnings"].append(
                "No applied loads found - only constraint reactions will be analyzed"
            )

        # Check mesh quality vs simulation type
        if (
            setup.simulation_type == SimulationType.CFD
            and setup.mesh_settings.quality == MeshQuality.COARSE
        ):
            validation["warnings"].append(
                "Coarse mesh may not capture CFD flow details accurately"
            )

        if (
            setup.simulation_type == SimulationType.MODAL
            and setup.mesh_settings.element_size > 5.0
        ):
            validation["warnings"].append(
                "Large element size may miss higher frequency modes"
            )

        # Material property checks
        if setup.material.elastic_modulus <= 0:
            validation["errors"].append("Invalid elastic modulus - must be positive")

        if setup.material.poisson_ratio < 0 or setup.material.poisson_ratio > 0.5:
            validation["warnings"].append("Poisson ratio outside typical range (0-0.5)")

        # Provide helpful info
        validation["info"].append(f"Simulation type: {setup.simulation_type.value}")
        validation["info"].append(f"Material: {setup.material.name}")
        validation["info"].append(f"Mesh quality: {setup.mesh_settings.quality.value}")

        return validation

    def _determine_simulation_type(self, analysis_goal: str) -> SimulationType:
        """Determine simulation type from analysis goal description."""
        goal_lower = analysis_goal.lower()

        if any(
            word in goal_lower
            for word in ["stress", "strain", "deflection", "displacement"]
        ):
            return SimulationType.STRUCTURAL_FEA
        elif any(word in goal_lower for word in ["thermal", "temperature", "heat"]):
            return SimulationType.THERMAL
        elif any(
            word in goal_lower
            for word in ["flow", "fluid", "cfd", "velocity", "pressure drop"]
        ):
            return SimulationType.CFD
        elif any(
            word in goal_lower
            for word in ["vibration", "frequency", "modal", "resonance"]
        ):
            return SimulationType.MODAL
        elif any(word in goal_lower for word in ["fatigue", "cyclic", "life"]):
            return SimulationType.FATIGUE
        elif any(word in goal_lower for word in ["buckling", "stability"]):
            return SimulationType.BUCKLING
        else:
            # Default to structural FEA
            return SimulationType.STRUCTURAL_FEA

    def _get_material_properties(self, material_name: str) -> MaterialProperties:
        """Get material properties from database."""
        material_data = self.material_database.get(material_name)
        if not material_data:
            logger.warning(
                f"Material {material_name} not found, using default steel properties"
            )
            material_data = self.material_database["steel_1018"]

        return MaterialProperties(**material_data)

    def _recommend_mesh_settings(self, obj, sim_type: SimulationType) -> MeshSettings:
        """Recommend mesh settings based on object and simulation type."""
        # Simplified geometry analysis - would analyze actual geometry in real implementation
        estimated_size = 100.0  # mm, mock characteristic size

        # Base element size as fraction of characteristic dimension
        if sim_type == SimulationType.CFD:
            element_size = estimated_size / 20  # Finer mesh for CFD
            quality = MeshQuality.FINE
        elif sim_type == SimulationType.MODAL:
            element_size = estimated_size / 15  # Good resolution for modes
            quality = MeshQuality.MEDIUM
        else:
            element_size = estimated_size / 10  # Standard structural mesh
            quality = MeshQuality.MEDIUM

        return MeshSettings(
            quality=quality,
            element_size=element_size,
            element_type="tetrahedral",
            refinement_regions=["fillets", "holes", "stress_concentrations"],
            growth_rate=1.2,
            curvature_based=True,
        )

    def _recommend_boundary_conditions(
        self, obj, loading_conditions: List[str], constraints: List[str]
    ) -> List[BoundaryCondition]:
        """Recommend boundary conditions based on descriptions."""
        boundary_conditions = []

        # Default constraint if none specified
        if not constraints:
            boundary_conditions.append(
                BoundaryCondition(
                    bc_type=BoundaryConditionType.FIXED_CONSTRAINT,
                    location="base_face",
                    magnitude=0.0,
                    direction=None,
                    description="Fixed constraint at base",
                )
            )
        else:
            # Process constraint descriptions
            for constraint in constraints:
                if "fixed" in constraint.lower():
                    boundary_conditions.append(
                        BoundaryCondition(
                            bc_type=BoundaryConditionType.FIXED_CONSTRAINT,
                            location="constraint_face",
                            magnitude=0.0,
                            direction=None,
                            description=constraint,
                        )
                    )

        # Default load if none specified
        if not loading_conditions:
            boundary_conditions.append(
                BoundaryCondition(
                    bc_type=BoundaryConditionType.FORCE_LOAD,
                    location="top_face",
                    magnitude=100.0,  # 100N default
                    direction=[0, 0, -1],
                    description="Default downward force",
                )
            )
        else:
            # Process loading descriptions
            for load in loading_conditions:
                if "force" in load.lower():
                    boundary_conditions.append(
                        BoundaryCondition(
                            bc_type=BoundaryConditionType.FORCE_LOAD,
                            location="loading_face",
                            magnitude=100.0,
                            direction=[0, 0, -1],
                            description=load,
                        )
                    )

        return boundary_conditions

    def _get_analysis_settings(self, sim_type: SimulationType) -> Dict[str, Any]:
        """Get analysis settings for simulation type."""
        settings = {
            SimulationType.STRUCTURAL_FEA: {
                "analysis_type": "static",
                "large_deformation": False,
                "contact_detection": True,
                "solver": "iterative",
            },
            SimulationType.THERMAL: {
                "analysis_type": "steady_state",
                "radiation": False,
                "convection": True,
                "solver": "direct",
            },
            SimulationType.CFD: {
                "turbulence_model": "k_epsilon",
                "compressible": False,
                "viscous": True,
                "solver": "simple",
            },
            SimulationType.MODAL: {
                "number_of_modes": 10,
                "frequency_range": [0, 1000],  # Hz
                "mass_matrix": "consistent",
                "solver": "lanczos",
            },
        }

        return settings.get(sim_type, settings[SimulationType.STRUCTURAL_FEA])

    def _get_expected_results(self, sim_type: SimulationType) -> List[str]:
        """Get list of expected results for simulation type."""
        results = {
            SimulationType.STRUCTURAL_FEA: [
                "von Mises stress",
                "displacement magnitude",
                "strain",
                "safety factor",
                "reaction forces",
            ],
            SimulationType.THERMAL: [
                "temperature distribution",
                "heat flux",
                "thermal gradient",
            ],
            SimulationType.CFD: [
                "velocity field",
                "pressure distribution",
                "turbulence intensity",
                "mass flow rate",
            ],
            SimulationType.MODAL: [
                "natural frequencies",
                "mode shapes",
                "participation factors",
            ],
        }

        return results.get(sim_type, results[SimulationType.STRUCTURAL_FEA])

    def _get_convergence_criteria(self, sim_type: SimulationType) -> Dict[str, float]:
        """Get convergence criteria for simulation type."""
        criteria = {
            SimulationType.STRUCTURAL_FEA: {
                "displacement_tolerance": 1e-6,
                "force_tolerance": 1e-3,
                "max_iterations": 50,
            },
            SimulationType.THERMAL: {
                "temperature_tolerance": 1e-4,
                "heat_flux_tolerance": 1e-3,
                "max_iterations": 100,
            },
            SimulationType.CFD: {
                "residual_tolerance": 1e-4,
                "mass_imbalance": 1e-6,
                "max_iterations": 1000,
            },
            SimulationType.MODAL: {"eigenvalue_tolerance": 1e-8, "max_iterations": 30},
        }

        return criteria.get(sim_type, criteria[SimulationType.STRUCTURAL_FEA])

    def _generate_reasoning(
        self, analysis_goal: str, sim_type: SimulationType
    ) -> List[str]:
        """Generate reasoning for simulation setup choices."""
        reasoning = [
            f"Selected {sim_type.value} based on analysis goal: '{analysis_goal}'",
            "Mesh density balanced for accuracy vs computational cost",
            "Boundary conditions inferred from typical loading scenarios",
        ]

        if sim_type == SimulationType.CFD:
            reasoning.append(
                "CFD mesh refined near boundaries for accurate flow capture"
            )
        elif sim_type == SimulationType.MODAL:
            reasoning.append(
                "Modal analysis configured for first 10 natural frequencies"
            )

        return reasoning

    def _generate_warnings(self, setup: SimulationSetup) -> List[str]:
        """Generate warnings for simulation setup."""
        warnings = []

        if setup.mesh_settings.element_size > 10.0:
            warnings.append("Large element size may reduce accuracy")

        if len(setup.load_cases[0].boundary_conditions) < 2:
            warnings.append(
                "Limited boundary conditions may not represent real loading"
            )

        if (
            setup.simulation_type == SimulationType.CFD
            and setup.mesh_settings.quality == MeshQuality.COARSE
        ):
            warnings.append("Coarse mesh may not capture flow details")

        return warnings

    def _estimate_runtime(self, setup: SimulationSetup) -> str:
        """Estimate simulation runtime."""
        # Simple runtime estimation based on simulation type and mesh
        base_times = {
            SimulationType.STRUCTURAL_FEA: 5,  # minutes
            SimulationType.THERMAL: 3,
            SimulationType.CFD: 30,
            SimulationType.MODAL: 10,
        }

        base_time = base_times.get(setup.simulation_type, 5)

        # Adjust for mesh quality
        quality_multipliers = {
            MeshQuality.COARSE: 0.5,
            MeshQuality.MEDIUM: 1.0,
            MeshQuality.FINE: 3.0,
            MeshQuality.VERY_FINE: 8.0,
        }

        multiplier = quality_multipliers.get(setup.mesh_settings.quality, 1.0)
        estimated_time = base_time * multiplier

        if estimated_time < 60:
            return f"{estimated_time:.0f} minutes"
        else:
            return f"{estimated_time/60:.1f} hours"

    def _estimate_resources(self, setup: SimulationSetup) -> Dict[str, str]:
        """Estimate computational resources required."""
        # Estimate based on mesh quality and simulation type
        memory_gb = 2.0  # Base memory

        quality_memory = {
            MeshQuality.COARSE: 1.0,
            MeshQuality.MEDIUM: 2.0,
            MeshQuality.FINE: 4.0,
            MeshQuality.VERY_FINE: 8.0,
        }

        memory_gb *= quality_memory.get(setup.mesh_settings.quality, 2.0)

        if setup.simulation_type == SimulationType.CFD:
            memory_gb *= 2.0  # CFD requires more memory

        return {
            "memory": f"{memory_gb:.1f} GB RAM",
            "cpu_cores": "4-8 cores recommended",
            "disk_space": "1-5 GB for results storage",
        }

    def _create_mock_simulation_recommendation(
        self, object_name: str, analysis_goal: str
    ) -> SimulationRecommendation:
        """Create mock simulation recommendation when FreeCAD is not available."""
        mock_material = MaterialProperties(
            name="steel_1018",
            density=7870.0,
            elastic_modulus=200e9,
            poisson_ratio=0.29,
            yield_strength=370e6,
            thermal_conductivity=51.9,
            specific_heat=486.0,
            thermal_expansion=11.7e-6,
        )

        mock_mesh = MeshSettings(
            quality=MeshQuality.MEDIUM,
            element_size=2.0,
            element_type="tetrahedral",
            refinement_regions=["stress_concentrations"],
            growth_rate=1.2,
            curvature_based=True,
        )

        mock_bc = [
            BoundaryCondition(
                bc_type=BoundaryConditionType.FIXED_CONSTRAINT,
                location="base_face",
                magnitude=0.0,
                direction=None,
                description="Fixed constraint at base",
            ),
            BoundaryCondition(
                bc_type=BoundaryConditionType.FORCE_LOAD,
                location="top_face",
                magnitude=100.0,
                direction=[0, 0, -1],
                description="100N downward force",
            ),
        ]

        mock_load_case = LoadCase(
            name="Primary Load Case",
            description="Main loading scenario",
            boundary_conditions=mock_bc,
        )

        mock_setup = SimulationSetup(
            simulation_type=SimulationType.STRUCTURAL_FEA,
            object_name=object_name,
            material=mock_material,
            mesh_settings=mock_mesh,
            load_cases=[mock_load_case],
            analysis_settings={"analysis_type": "static", "solver": "iterative"},
            expected_results=["von Mises stress", "displacement"],
            convergence_criteria={"displacement_tolerance": 1e-6},
        )

        return SimulationRecommendation(
            setup=mock_setup,
            confidence=0.85,
            reasoning=[
                "Structural FEA selected for stress analysis",
                "Medium mesh provides good balance of accuracy and speed",
                "Standard boundary conditions for typical loading",
            ],
            warnings=["Verify boundary conditions match actual constraints"],
            estimated_runtime="5 minutes",
            required_resources={"memory": "2.0 GB RAM", "cpu_cores": "4 cores"},
        )

    def _create_error_recommendation(
        self, object_name: str, error_message: str
    ) -> SimulationRecommendation:
        """Create error recommendation for failed setup."""
        # Create minimal setup for error case
        error_material = MaterialProperties(
            name="unknown",
            density=0,
            elastic_modulus=0,
            poisson_ratio=0,
            yield_strength=0,
            thermal_conductivity=0,
            specific_heat=0,
            thermal_expansion=0,
        )

        error_mesh = MeshSettings(
            quality=MeshQuality.MEDIUM,
            element_size=1.0,
            element_type="tetrahedral",
            refinement_regions=[],
            growth_rate=1.2,
            curvature_based=False,
        )

        error_setup = SimulationSetup(
            simulation_type=SimulationType.STRUCTURAL_FEA,
            object_name=object_name,
            material=error_material,
            mesh_settings=error_mesh,
            load_cases=[],
            analysis_settings={},
            expected_results=[],
            convergence_criteria={},
        )

        return SimulationRecommendation(
            setup=error_setup,
            confidence=0.0,
            reasoning=[f"Setup failed: {error_message}"],
            warnings=[],
            estimated_runtime="Unable to estimate",
            required_resources={},
        )

    def _load_material_database(self) -> Dict[str, Dict[str, Any]]:
        """Load material properties database."""
        return {
            "steel_1018": {
                "name": "Steel 1018",
                "density": 7870.0,  # kg/m³
                "elastic_modulus": 200e9,  # Pa
                "poisson_ratio": 0.29,
                "yield_strength": 370e6,  # Pa
                "thermal_conductivity": 51.9,  # W/m·K
                "specific_heat": 486.0,  # J/kg·K
                "thermal_expansion": 11.7e-6,  # 1/K
            },
            "aluminum_6061": {
                "name": "Aluminum 6061",
                "density": 2700.0,
                "elastic_modulus": 69e9,
                "poisson_ratio": 0.33,
                "yield_strength": 276e6,
                "thermal_conductivity": 167.0,
                "specific_heat": 896.0,
                "thermal_expansion": 23.6e-6,
            },
            "stainless_316": {
                "name": "Stainless Steel 316",
                "density": 8000.0,
                "elastic_modulus": 200e9,
                "poisson_ratio": 0.30,
                "yield_strength": 290e6,
                "thermal_conductivity": 16.3,
                "specific_heat": 500.0,
                "thermal_expansion": 16.0e-6,
            },
        }

    def _load_simulation_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load simulation setup templates."""
        return {
            "stress_analysis": {
                "simulation_type": SimulationType.STRUCTURAL_FEA,
                "typical_loads": ["force", "pressure"],
                "typical_constraints": ["fixed", "pinned"],
                "mesh_quality": MeshQuality.MEDIUM,
            },
            "thermal_analysis": {
                "simulation_type": SimulationType.THERMAL,
                "typical_loads": ["temperature", "heat_flux"],
                "typical_constraints": ["fixed_temperature", "convection"],
                "mesh_quality": MeshQuality.MEDIUM,
            },
            "flow_analysis": {
                "simulation_type": SimulationType.CFD,
                "typical_loads": ["velocity_inlet", "pressure_outlet"],
                "typical_constraints": ["wall", "symmetry"],
                "mesh_quality": MeshQuality.FINE,
            },
        }

    def _load_mesh_guidelines(self) -> Dict[str, Dict[str, Any]]:
        """Load mesh generation guidelines."""
        return {
            "structural": {
                "min_elements_per_wavelength": 6,
                "aspect_ratio_limit": 3.0,
                "skewness_limit": 0.9,
            },
            "thermal": {
                "min_elements_per_gradient": 4,
                "aspect_ratio_limit": 5.0,
                "boundary_layer_thickness": 0.1,
            },
            "cfd": {
                "y_plus_target": 1.0,
                "boundary_layer_growth_rate": 1.2,
                "max_aspect_ratio": 100.0,
            },
        }


def demo_simulation_assistant():
    """Demonstrate simulation assistant capabilities."""
    print("Simulation Assistant Demo")
    print("=" * 40)

    assistant = SimulationAssistant()

    # Get simulation recommendation
    recommendation = assistant.recommend_simulation_setup(
        "demo_bracket",
        "stress analysis under static load",
        "aluminum_6061",
        loading_conditions=["100N downward force on top surface"],
        constraints=["fixed at mounting holes"],
    )

    print(f"Simulation Type: {recommendation.setup.simulation_type.value}")
    print(f"Material: {recommendation.setup.material.name}")
    print(f"Confidence: {recommendation.confidence:.2f}")
    print(f"Estimated Runtime: {recommendation.estimated_runtime}")

    print("\\nMesh Settings:")
    mesh = recommendation.setup.mesh_settings
    print(f"  Quality: {mesh.quality.value}")
    print(f"  Element Size: {mesh.element_size:.1f} mm")
    print(f"  Element Type: {mesh.element_type}")

    print("\\nBoundary Conditions:")
    for i, bc in enumerate(recommendation.setup.load_cases[0].boundary_conditions, 1):
        print(f"  {i}. {bc.bc_type.value}")
        print(f"     Location: {bc.location}")
        print(f"     Description: {bc.description}")

    print("\\nReasoning:")
    for reason in recommendation.reasoning:
        print(f"  • {reason}")

    if recommendation.warnings:
        print("\\nWarnings:")
        for warning in recommendation.warnings:
            print(f"  ⚠ {warning}")

    # Test mesh optimization
    print("\\n" + "=" * 40)
    print("MESH OPTIMIZATION")
    print("=" * 40)

    optimized_mesh = assistant.optimize_mesh_settings(
        "demo_bracket", SimulationType.CFD, "high"
    )

    print("Optimized Mesh for CFD:")
    print(f"  Quality: {optimized_mesh.quality.value}")
    print(f"  Element Size: {optimized_mesh.element_size:.1f} mm")
    print(f"  Refinement Regions: {', '.join(optimized_mesh.refinement_regions)}")

    # Test validation
    print("\\n" + "=" * 40)
    print("SETUP VALIDATION")
    print("=" * 40)

    validation = assistant.validate_simulation_setup(recommendation.setup)

    for category, issues in validation.items():
        if issues and category != "info":
            print(f"\\n{category.upper()}:")
            for issue in issues:
                print(f"  • {issue}")


if __name__ == "__main__":
    demo_simulation_assistant()
