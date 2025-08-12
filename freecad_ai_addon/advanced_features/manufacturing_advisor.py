"""
Manufacturing Advisor for FreeCAD AI Addon.

This module provides AI-powered manufacturing advice including material selection,
process recommendations, cost estimation, and design for manufacturing (DFM) guidance.
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


class ManufacturingProcess(Enum):
    """Types of manufacturing processes."""

    MACHINING = "machining"
    CASTING = "casting"
    FORGING = "forging"
    STAMPING = "stamping"
    WELDING = "welding"
    SHEET_METAL = "sheet_metal"
    INJECTION_MOLDING = "injection_molding"
    ADDITIVE_MANUFACTURING = "additive_manufacturing"
    ASSEMBLY = "assembly"
    GRINDING = "grinding"
    TURNING = "turning"
    MILLING = "milling"


class MaterialCategory(Enum):
    """Categories of materials."""

    METALS = "metals"
    POLYMERS = "polymers"
    CERAMICS = "ceramics"
    COMPOSITES = "composites"
    ELASTOMERS = "elastomers"
    NATURAL = "natural"


class CostCategory(Enum):
    """Cost analysis categories."""

    MATERIAL_COST = "material_cost"
    TOOLING_COST = "tooling_cost"
    LABOR_COST = "labor_cost"
    SETUP_COST = "setup_cost"
    FINISHING_COST = "finishing_cost"
    QUALITY_COST = "quality_cost"


@dataclass
class MaterialProperties:
    """Material properties and characteristics."""

    name: str
    category: MaterialCategory
    density: float  # kg/m³
    tensile_strength: float  # MPa
    yield_strength: float  # MPa
    elastic_modulus: float  # GPa
    cost_per_kg: float  # $/kg
    machinability_rating: float  # 0-10 scale
    weldability_rating: float  # 0-10 scale
    corrosion_resistance: float  # 0-10 scale
    availability: str  # "high", "medium", "low"
    applications: List[str]


@dataclass
class ProcessRecommendation:
    """Manufacturing process recommendation."""

    process: ManufacturingProcess
    suitability_score: float  # 0-10 scale
    estimated_cost: float
    lead_time_days: int
    quality_rating: float  # 0-10 scale
    advantages: List[str]
    disadvantages: List[str]
    considerations: List[str]


@dataclass
class CostEstimate:
    """Manufacturing cost estimation."""

    total_cost: float
    cost_breakdown: Dict[CostCategory, float]
    quantity: int
    cost_per_unit: float
    material_utilization: float  # percentage
    assumptions: List[str]


@dataclass
class ManufacturingAdvice:
    """Complete manufacturing advice package."""

    recommended_materials: List[MaterialProperties]
    recommended_processes: List[ProcessRecommendation]
    cost_estimates: List[CostEstimate]
    dfm_recommendations: List[str]
    quality_considerations: List[str]
    risk_factors: List[str]
    timeline_estimate: str


def advice_to_dict(advice: ManufacturingAdvice) -> Dict[str, Any]:
    """Serialize ManufacturingAdvice to a JSON-safe dict (enums to strings).

    This is useful for rendering advice in the conversation widget or exporting.
    """

    def _material(m: MaterialProperties) -> Dict[str, Any]:
        return {
            "name": m.name,
            "category": m.category.value
            if isinstance(m.category, MaterialCategory)
            else m.category,
            "density": m.density,
            "tensile_strength": m.tensile_strength,
            "yield_strength": m.yield_strength,
            "elastic_modulus": m.elastic_modulus,
            "cost_per_kg": m.cost_per_kg,
            "machinability_rating": m.machinability_rating,
            "weldability_rating": m.weldability_rating,
            "corrosion_resistance": m.corrosion_resistance,
            "availability": m.availability,
            "applications": list(m.applications),
        }

    def _proc(p: ProcessRecommendation) -> Dict[str, Any]:
        return {
            "process": p.process.value
            if isinstance(p.process, ManufacturingProcess)
            else p.process,
            "suitability_score": p.suitability_score,
            "estimated_cost": p.estimated_cost,
            "lead_time_days": p.lead_time_days,
            "quality_rating": p.quality_rating,
            "advantages": list(p.advantages),
            "disadvantages": list(p.disadvantages),
            "considerations": list(p.considerations),
        }

    def _cost(c: CostEstimate) -> Dict[str, Any]:
        return {
            "total_cost": c.total_cost,
            "cost_breakdown": {
                k.value if isinstance(k, CostCategory) else k: v
                for k, v in c.cost_breakdown.items()
            },
            "quantity": c.quantity,
            "cost_per_unit": c.cost_per_unit,
            "material_utilization": c.material_utilization,
            "assumptions": list(c.assumptions),
        }

    return {
        "recommended_materials": [_material(m) for m in advice.recommended_materials],
        "recommended_processes": [_proc(p) for p in advice.recommended_processes],
        "cost_estimates": [_cost(c) for c in advice.cost_estimates],
        "dfm_recommendations": list(advice.dfm_recommendations),
        "quality_considerations": list(advice.quality_considerations),
        "risk_factors": list(advice.risk_factors),
        "timeline_estimate": advice.timeline_estimate,
    }


class ManufacturingAdvisor:
    """
    AI-powered manufacturing advisor for CAD designs.

    Provides comprehensive manufacturing guidance including:
    - Material selection recommendations
    - Manufacturing process optimization
    - Cost estimation and analysis
    - Design for Manufacturing (DFM) advice
    - Quality and risk assessment
    """

    def __init__(self):
        """Initialize the manufacturing advisor."""
        self.materials_database = self._load_materials_database()
        self.processes_database = self._load_processes_database()
        self.cost_models = self._load_cost_models()
        self.advice_history = []

    def analyze_manufacturability(
        self,
        object_name: str,
        quantity: int = 1,
        requirements: Optional[Dict[str, Any]] = None,
    ) -> ManufacturingAdvice:
        """
        Analyze manufacturability of a CAD design and provide comprehensive advice.

        Args:
            object_name: Name of the FreeCAD object to analyze
            quantity: Production quantity for cost estimation
            requirements: Optional requirements dict (strength, cost_target, lead_time, etc.)

        Returns:
            ManufacturingAdvice with complete manufacturing guidance

        Example:
            advisor = ManufacturingAdvisor()

            requirements = {
                'strength_requirement': 'high',
                'cost_target': 50.0,  # $50 target
                'lead_time_days': 30,
                'surface_finish': 'standard'
            }

            advice = advisor.analyze_manufacturability("Bracket001", quantity=100, requirements=requirements)
        """
        if not FREECAD_AVAILABLE:
            logger.warning("FreeCAD not available, returning mock advice")
            return self._create_mock_manufacturing_advice(object_name, quantity)

        logger.info(f"Analyzing manufacturability for: {object_name}")
        logger.info(f"Quantity: {quantity}")

        try:
            doc = App.activeDocument()
            if not doc:
                raise ValueError("No active document found")

            obj = doc.getObject(object_name)
            if not obj:
                raise ValueError(f"Object '{object_name}' not found")

            # Analyze the design
            design_characteristics = self._analyze_design_characteristics(obj)

            # Generate recommendations
            recommended_materials = self._recommend_materials(
                design_characteristics, requirements
            )
            recommended_processes = self._recommend_processes(
                design_characteristics, quantity
            )
            cost_estimates = self._estimate_costs(
                design_characteristics, quantity, recommended_processes
            )
            dfm_recommendations = self._generate_dfm_recommendations(
                design_characteristics
            )
            # Optionally integrate Design Rule Checker insights
            try:
                dfm_recommendations.extend(self._get_drc_recommendations(object_name))
            except Exception as _e:
                logger.debug(f"DRC integration skipped: {_e}")

            advice = ManufacturingAdvice(
                recommended_materials=recommended_materials,
                recommended_processes=recommended_processes,
                cost_estimates=cost_estimates,
                dfm_recommendations=dfm_recommendations,
                quality_considerations=self._assess_quality_considerations(
                    design_characteristics
                ),
                risk_factors=self._identify_risk_factors(design_characteristics),
                timeline_estimate=self._estimate_timeline(
                    recommended_processes, quantity
                ),
            )

            self.advice_history.append(advice)
            return advice

        except Exception as e:
            logger.error(f"Manufacturability analysis failed: {e}")
            return self._create_error_advice(str(e))

    def recommend_materials(
        self, application: str, requirements: Dict[str, Any]
    ) -> List[MaterialProperties]:
        """
        Recommend materials based on application and requirements.

        Args:
            application: Application type (e.g., "structural", "electrical", "automotive")
            requirements: Requirements dict with strength, weight, cost constraints

        Returns:
            List of recommended MaterialProperties
        """
        logger.info(f"Recommending materials for application: {application}")

        # Filter materials based on requirements
        suitable_materials = []

        for material in self.materials_database.values():
            if self._material_meets_requirements(material, requirements):
                suitable_materials.append(material)

        # Sort by suitability score
        suitable_materials.sort(
            key=lambda m: self._calculate_material_score(m, requirements), reverse=True
        )

        return suitable_materials[:5]  # Return top 5 recommendations

    def estimate_manufacturing_cost(
        self,
        object_name: str,
        quantity: int,
        process: ManufacturingProcess,
        material_name: str,
    ) -> CostEstimate:
        """
        Estimate manufacturing cost for specific process and material.

        Args:
            object_name: Name of the FreeCAD object
            quantity: Production quantity
            process: Manufacturing process to use
            material_name: Material to use

        Returns:
            CostEstimate with detailed cost breakdown
        """
        logger.info(
            f"Estimating cost for {object_name}: {quantity} units, {process.value}, {material_name}"
        )

        # Get material properties
        material = self.materials_database.get(material_name)
        if not material:
            raise ValueError(f"Material '{material_name}' not found in database")

        # Get process parameters
        process_params = self.processes_database.get(process)
        if not process_params:
            raise ValueError(f"Process '{process.value}' not found in database")

        # Calculate costs
        if FREECAD_AVAILABLE:
            volume = self._calculate_object_volume(object_name)
            mass = volume * material.density / 1e9  # Convert mm³ to m³ then to kg
        else:
            volume = 1000.0  # Mock volume in mm³
            mass = 0.002  # Mock mass in kg

        material_cost = mass * material.cost_per_kg * quantity

        # Process-specific cost calculations
        if process == ManufacturingProcess.MACHINING:
            labor_cost = self._calculate_machining_cost(
                volume, quantity, material.machinability_rating
            )
        elif process == ManufacturingProcess.INJECTION_MOLDING:
            labor_cost = self._calculate_molding_cost(volume, quantity)
        elif process == ManufacturingProcess.ADDITIVE_MANUFACTURING:
            labor_cost = self._calculate_3d_printing_cost(
                volume, quantity, material_name
            )
        else:
            labor_cost = material_cost * 0.5  # Default labor cost estimate

        setup_cost = process_params.get("setup_cost", 100.0)
        tooling_cost = (
            process_params.get("tooling_cost", 500.0) if quantity > 10 else 0.0
        )
        finishing_cost = material_cost * 0.1  # 10% of material cost
        quality_cost = (material_cost + labor_cost) * 0.05  # 5% for quality control

        total_cost = (
            material_cost
            + labor_cost
            + setup_cost
            + tooling_cost
            + finishing_cost
            + quality_cost
        )

        return CostEstimate(
            total_cost=total_cost,
            cost_breakdown={
                CostCategory.MATERIAL_COST: material_cost,
                CostCategory.LABOR_COST: labor_cost,
                CostCategory.SETUP_COST: setup_cost,
                CostCategory.TOOLING_COST: tooling_cost,
                CostCategory.FINISHING_COST: finishing_cost,
                CostCategory.QUALITY_COST: quality_cost,
            },
            quantity=quantity,
            cost_per_unit=total_cost / quantity,
            material_utilization=85.0,  # Assume 85% material utilization
            assumptions=[
                f"Material: {material_name}",
                f"Process: {process.value}",
                f"Volume: {volume:.2f} mm³",
                f"Mass: {mass:.3f} kg per unit",
                "Standard tolerances assumed",
                "No special finishing requirements",
            ],
        )

    def _analyze_design_characteristics(self, obj) -> Dict[str, Any]:
        """Analyze design characteristics for manufacturability."""
        # Simplified analysis - in reality would analyze geometry, features, etc.
        return {
            "volume": 1000.0,  # mm³
            "surface_area": 600.0,  # mm²
            "complexity": "medium",
            "features": ["holes", "fillets"],
            "min_wall_thickness": 2.0,  # mm
            "aspect_ratio": 2.5,
            "symmetry": "partial",
            "tolerances": "standard",
        }

    def _recommend_materials(
        self,
        design_characteristics: Dict[str, Any],
        requirements: Optional[Dict[str, Any]],
    ) -> List[MaterialProperties]:
        """Recommend materials based on design and requirements."""
        recommended = []

        # Default requirements if none provided
        if not requirements:
            requirements = {"strength_requirement": "medium", "cost_target": 100.0}

        # Get suitable materials from database
        for material_name, material in self.materials_database.items():
            if self._material_meets_requirements(material, requirements):
                recommended.append(material)

        # Sort by suitability
        recommended.sort(
            key=lambda m: self._calculate_material_score(m, requirements), reverse=True
        )

        return recommended[:3]  # Return top 3

    def _recommend_processes(
        self, design_characteristics: Dict[str, Any], quantity: int
    ) -> List[ProcessRecommendation]:
        """Recommend manufacturing processes."""
        recommendations = []

        # Machining recommendation
        machining_score = 8.0 if design_characteristics["complexity"] != "high" else 6.0
        recommendations.append(
            ProcessRecommendation(
                process=ManufacturingProcess.MACHINING,
                suitability_score=machining_score,
                estimated_cost=50.0 * quantity,
                lead_time_days=7,
                quality_rating=9.0,
                advantages=["High precision", "Good surface finish", "Flexible"],
                disadvantages=["Higher cost for large quantities", "Material waste"],
                considerations=["Consider batch processing", "Tool wear management"],
            )
        )

        # Additive Manufacturing for complex geometries
        if design_characteristics["complexity"] == "high":
            recommendations.append(
                ProcessRecommendation(
                    process=ManufacturingProcess.ADDITIVE_MANUFACTURING,
                    suitability_score=9.0,
                    estimated_cost=30.0 * quantity,
                    lead_time_days=3,
                    quality_rating=7.0,
                    advantages=["Complex geometries", "No tooling", "Fast prototyping"],
                    disadvantages=[
                        "Surface finish",
                        "Material limitations",
                        "Post-processing",
                    ],
                    considerations=[
                        "Layer orientation",
                        "Support structures",
                        "Post-processing requirements",
                    ],
                )
            )

        # Injection molding for high quantities
        if quantity > 100:
            recommendations.append(
                ProcessRecommendation(
                    process=ManufacturingProcess.INJECTION_MOLDING,
                    suitability_score=8.5,
                    estimated_cost=5.0 * quantity + 2000.0,  # High tooling cost
                    lead_time_days=21,
                    quality_rating=9.5,
                    advantages=[
                        "Low unit cost",
                        "High volume",
                        "Excellent repeatability",
                    ],
                    disadvantages=[
                        "High tooling cost",
                        "Design constraints",
                        "Long lead time",
                    ],
                    considerations=[
                        "Draft angles required",
                        "Uniform wall thickness",
                        "Gate location",
                    ],
                )
            )

        return sorted(recommendations, key=lambda r: r.suitability_score, reverse=True)

    def _estimate_costs(
        self,
        design_characteristics: Dict[str, Any],
        quantity: int,
        processes: List[ProcessRecommendation],
    ) -> List[CostEstimate]:
        """Estimate costs for recommended processes."""
        estimates = []

        for process_rec in processes[:2]:  # Top 2 processes
            # Use steel as default material for estimation
            try:
                estimate = self.estimate_manufacturing_cost(
                    "mock_object", quantity, process_rec.process, "steel_1018"
                )
                estimates.append(estimate)
            except Exception as e:
                logger.warning(f"Cost estimation failed for {process_rec.process}: {e}")

        return estimates

    def _generate_dfm_recommendations(
        self, design_characteristics: Dict[str, Any]
    ) -> List[str]:
        """Generate Design for Manufacturing recommendations."""
        recommendations = []

        if design_characteristics["min_wall_thickness"] < 1.0:
            recommendations.append(
                "Increase minimum wall thickness to at least 1.0mm for manufacturability"
            )

        if "sharp_corners" in design_characteristics.get("features", []):
            recommendations.append(
                "Add fillets to sharp corners to reduce stress concentrations and improve machinability"
            )

        if design_characteristics["aspect_ratio"] > 5.0:
            recommendations.append(
                "Consider reducing aspect ratio to improve stability during manufacturing"
            )

        recommendations.extend(
            [
                "Use standard hole sizes where possible to reduce tooling costs",
                "Avoid deep pockets with small openings",
                "Consider split-line placement for molded parts",
                "Minimize the number of different fastener types",
                "Design for standard surface finishes",
            ]
        )

        # Additional manufacturing rules per Week 2 plan
        # Minimum fillet radius guidance (generic)
        recommendations.append(
            "Apply fillets: avoid sharp internal corners; min radius typically >= 0.5 mm for machining"
        )

        # Drilling depth-to-diameter guideline
        recommendations.append(
            "For drilled holes, keep depth <= 10x diameter when possible; beyond that consider peck drilling or alternate processes"
        )

        # Overhang guideline for FDM 3D printing
        recommendations.append(
            "For FDM printing, limit unsupported overhangs to <= 45 degrees or add support structures"
        )

        return recommendations

    def _get_drc_recommendations(self, object_name: str) -> List[str]:
        """Integrate recommendations from the Design Rule Checker when available.

        Returns an empty list if the checker is unavailable or FreeCAD is not active.
        """
        if not FREECAD_AVAILABLE:
            return []
        try:
            # Local import to avoid hard dependency and enum collisions
            from freecad_ai_addon.advanced_features.design_rule_checker import (
                DesignRuleChecker,
                ManufacturingProcess as DRCProcess,
            )

            checker = DesignRuleChecker()
            # Use a generic process for broader coverage
            report = checker.check_design(
                object_name, DRCProcess.MACHINING, "steel_1018"
            )
            recs = list(report.recommendations)
            # Also surface top violation fixes
            for v in report.violations_found[:3]:
                if getattr(v, "suggested_fix", None):
                    recs.append(f"Fix: {v.suggested_fix}")
            return recs
        except Exception as e:
            logger.debug(f"DRC recommendations not available: {e}")
            return []

    def _assess_quality_considerations(
        self, design_characteristics: Dict[str, Any]
    ) -> List[str]:
        """Assess quality considerations for the design."""
        return [
            "Implement statistical process control for critical dimensions",
            "Consider inspection points during manufacturing",
            "Document critical material properties and certifications",
            "Plan for dimensional verification at key stages",
            "Consider non-destructive testing for critical applications",
        ]

    def _identify_risk_factors(
        self, design_characteristics: Dict[str, Any]
    ) -> List[str]:
        """Identify manufacturing risk factors."""
        risks = []

        if design_characteristics["complexity"] == "high":
            risks.append("High complexity may lead to manufacturing difficulties")

        if design_characteristics["min_wall_thickness"] < 2.0:
            risks.append("Thin walls may cause distortion during manufacturing")

        risks.extend(
            [
                "Material availability fluctuations",
                "Potential for dimensional variations",
                "Setup and fixturing challenges",
                "Quality control complexity",
            ]
        )

        return risks

    def _estimate_timeline(
        self, processes: List[ProcessRecommendation], quantity: int
    ) -> str:
        """Estimate manufacturing timeline."""
        if not processes:
            return "Unable to estimate timeline"

        primary_process = processes[0]
        base_time = primary_process.lead_time_days

        if quantity > 100:
            additional_time = (quantity - 100) // 50  # Additional day per 50 units
            total_time = base_time + additional_time
        else:
            total_time = base_time

        return f"{total_time} days (including setup and quality verification)"

    def _material_meets_requirements(
        self, material: MaterialProperties, requirements: Dict[str, Any]
    ) -> bool:
        """Check if material meets specified requirements."""
        strength_req = requirements.get("strength_requirement", "medium")
        cost_target = requirements.get("cost_target", float("inf"))

        # Check strength requirement
        if strength_req == "high" and material.yield_strength < 300:
            return False
        elif strength_req == "medium" and material.yield_strength < 150:
            return False

        # Check cost target
        if material.cost_per_kg > cost_target:
            return False

        return True

    def _calculate_material_score(
        self, material: MaterialProperties, requirements: Dict[str, Any]
    ) -> float:
        """Calculate material suitability score."""
        score = 0.0

        # Strength score (0-3 points)
        strength_req = requirements.get("strength_requirement", "medium")
        if strength_req == "high":
            score += min(3.0, material.yield_strength / 200)
        else:
            score += min(3.0, material.yield_strength / 100)

        # Cost score (0-2 points)
        cost_target = requirements.get("cost_target", 10.0)
        if material.cost_per_kg <= cost_target:
            score += 2.0 - (material.cost_per_kg / cost_target)

        # Machinability score (0-2 points)
        score += material.machinability_rating / 5.0

        # Availability score (0-1 point)
        availability_scores = {"high": 1.0, "medium": 0.7, "low": 0.3}
        score += availability_scores.get(material.availability, 0.0)

        return score

    def _calculate_object_volume(self, object_name: str) -> float:
        """Calculate object volume."""
        return 1000.0  # Placeholder volume in mm³

    def _calculate_machining_cost(
        self, volume: float, quantity: int, machinability: float
    ) -> float:
        """Calculate machining cost based on volume and machinability."""
        base_rate = 60.0  # $/hour
        removal_rate = (
            1000.0 * machinability / 10.0
        )  # mm³/min adjusted for machinability
        machining_time = volume / removal_rate  # minutes
        cost_per_unit = (machining_time / 60.0) * base_rate
        return cost_per_unit * quantity

    def _calculate_molding_cost(self, volume: float, quantity: int) -> float:
        """Calculate injection molding cost."""
        cycle_time = 30.0 + volume / 1000.0  # seconds
        cost_per_cycle = 2.0  # $
        return cost_per_cycle * quantity * cycle_time / 60.0

    def _calculate_3d_printing_cost(
        self, volume: float, quantity: int, material_name: str
    ) -> float:
        """Calculate 3D printing cost."""
        print_speed = 50.0  # mm³/min
        print_time = volume / print_speed  # minutes
        cost_per_minute = 0.5  # $
        return print_time * cost_per_minute * quantity

    def _create_mock_manufacturing_advice(
        self, object_name: str, quantity: int
    ) -> ManufacturingAdvice:
        """Create mock manufacturing advice when FreeCAD is not available."""
        mock_material = MaterialProperties(
            name="aluminum_6061",
            category=MaterialCategory.METALS,
            density=2700.0,
            tensile_strength=310.0,
            yield_strength=276.0,
            elastic_modulus=69.0,
            cost_per_kg=4.0,
            machinability_rating=8.0,
            weldability_rating=7.0,
            corrosion_resistance=8.0,
            availability="high",
            applications=["General purpose", "Structural", "Automotive"],
        )

        mock_process = ProcessRecommendation(
            process=ManufacturingProcess.MACHINING,
            suitability_score=8.5,
            estimated_cost=50.0 * quantity,
            lead_time_days=7,
            quality_rating=9.0,
            advantages=["High precision", "Good surface finish"],
            disadvantages=["Higher cost", "Material waste"],
            considerations=["Tool selection", "Cutting parameters"],
        )

        mock_cost = CostEstimate(
            total_cost=75.0 * quantity,
            cost_breakdown={
                CostCategory.MATERIAL_COST: 20.0 * quantity,
                CostCategory.LABOR_COST: 35.0 * quantity,
                CostCategory.SETUP_COST: 100.0,
                CostCategory.TOOLING_COST: 0.0,
                CostCategory.FINISHING_COST: 5.0 * quantity,
                CostCategory.QUALITY_COST: 15.0 * quantity,
            },
            quantity=quantity,
            cost_per_unit=75.0,
            material_utilization=85.0,
            assumptions=["Mock analysis", "Standard tolerances"],
        )

        return ManufacturingAdvice(
            recommended_materials=[mock_material],
            recommended_processes=[mock_process],
            cost_estimates=[mock_cost],
            dfm_recommendations=[
                "Add fillets to sharp corners",
                "Use standard hole sizes",
                "Consider manufacturing tolerances",
            ],
            quality_considerations=[
                "Implement inspection checkpoints",
                "Document critical dimensions",
            ],
            risk_factors=["Material availability", "Dimensional variations"],
            timeline_estimate="7 days",
        )

    def _create_error_advice(self, error_message: str) -> ManufacturingAdvice:
        """Create error advice for failed analysis."""
        return ManufacturingAdvice(
            recommended_materials=[],
            recommended_processes=[],
            cost_estimates=[],
            dfm_recommendations=[f"Analysis failed: {error_message}"],
            quality_considerations=[],
            risk_factors=[],
            timeline_estimate="Unable to estimate",
        )

    def _load_materials_database(self) -> Dict[str, MaterialProperties]:
        """Load materials database."""
        return {
            "steel_1018": MaterialProperties(
                name="Steel 1018",
                category=MaterialCategory.METALS,
                density=7870.0,
                tensile_strength=440.0,
                yield_strength=370.0,
                elastic_modulus=200.0,
                cost_per_kg=2.5,
                machinability_rating=7.0,
                weldability_rating=9.0,
                corrosion_resistance=4.0,
                availability="high",
                applications=["General purpose", "Structural", "Mechanical"],
            ),
            "aluminum_6061": MaterialProperties(
                name="Aluminum 6061",
                category=MaterialCategory.METALS,
                density=2700.0,
                tensile_strength=310.0,
                yield_strength=276.0,
                elastic_modulus=69.0,
                cost_per_kg=4.0,
                machinability_rating=8.0,
                weldability_rating=7.0,
                corrosion_resistance=8.0,
                availability="high",
                applications=["Aerospace", "Automotive", "General purpose"],
            ),
            "stainless_316": MaterialProperties(
                name="Stainless Steel 316",
                category=MaterialCategory.METALS,
                density=8000.0,
                tensile_strength=620.0,
                yield_strength=290.0,
                elastic_modulus=200.0,
                cost_per_kg=8.0,
                machinability_rating=6.0,
                weldability_rating=8.0,
                corrosion_resistance=9.0,
                availability="high",
                applications=["Chemical", "Marine", "Food processing"],
            ),
            "aluminum_5052": MaterialProperties(
                name="Aluminum 5052",
                category=MaterialCategory.METALS,
                density=2680.0,
                tensile_strength=228.0,
                yield_strength=193.0,
                elastic_modulus=70.0,
                cost_per_kg=3.8,
                machinability_rating=7.0,
                weldability_rating=8.0,
                corrosion_resistance=8.0,
                availability="high",
                applications=["Sheet metal", "Enclosures", "Automotive panels"],
            ),
            "abs_plastic": MaterialProperties(
                name="ABS Plastic",
                category=MaterialCategory.POLYMERS,
                density=1050.0,
                tensile_strength=40.0,
                yield_strength=35.0,
                elastic_modulus=2.3,
                cost_per_kg=2.2,
                machinability_rating=6.0,
                weldability_rating=0.0,
                corrosion_resistance=9.0,
                availability="high",
                applications=["Injection molding", "Consumer products"],
            ),
            "nylon_pa12": MaterialProperties(
                name="Nylon PA12",
                category=MaterialCategory.POLYMERS,
                density=1010.0,
                tensile_strength=48.0,
                yield_strength=45.0,
                elastic_modulus=1.5,
                cost_per_kg=6.0,
                machinability_rating=5.0,
                weldability_rating=0.0,
                corrosion_resistance=9.0,
                availability="medium",
                applications=["SLS printing", "Gears", "Bushings"],
            ),
            "pla_3d_print": MaterialProperties(
                name="PLA (3D Print)",
                category=MaterialCategory.POLYMERS,
                density=1240.0,
                tensile_strength=60.0,
                yield_strength=50.0,
                elastic_modulus=3.5,
                cost_per_kg=2.0,
                machinability_rating=3.0,
                weldability_rating=0.0,
                corrosion_resistance=9.0,
                availability="high",
                applications=["Rapid prototyping", "Additive manufacturing"],
            ),
        }

    def _load_processes_database(self) -> Dict[ManufacturingProcess, Dict[str, Any]]:
        """Load manufacturing processes database."""
        return {
            ManufacturingProcess.MACHINING: {
                "setup_cost": 100.0,
                "tooling_cost": 200.0,
                "min_quantity": 1,
                "max_quantity": 1000,
                "typical_tolerance": 0.1,  # mm
            },
            ManufacturingProcess.INJECTION_MOLDING: {
                "setup_cost": 500.0,
                "tooling_cost": 5000.0,
                "min_quantity": 100,
                "max_quantity": 100000,
                "typical_tolerance": 0.2,
            },
            ManufacturingProcess.ADDITIVE_MANUFACTURING: {
                "setup_cost": 50.0,
                "tooling_cost": 0.0,
                "min_quantity": 1,
                "max_quantity": 50,
                "typical_tolerance": 0.3,
            },
            ManufacturingProcess.SHEET_METAL: {
                "setup_cost": 150.0,
                "tooling_cost": 300.0,
                "min_quantity": 1,
                "max_quantity": 5000,
                "typical_tolerance": 0.2,
            },
            ManufacturingProcess.CASTING: {
                "setup_cost": 800.0,
                "tooling_cost": 4000.0,
                "min_quantity": 50,
                "max_quantity": 50000,
                "typical_tolerance": 0.5,
            },
        }

    def _load_cost_models(self) -> Dict[str, Any]:
        """Load cost estimation models."""
        return {
            "labor_rates": {
                "machining": 60.0,  # $/hour
                "assembly": 40.0,
                "inspection": 45.0,
            },
            "overhead_factors": {
                "facility_overhead": 1.2,
                "administrative_overhead": 1.1,
                "profit_margin": 1.15,
            },
        }


def demo_manufacturing_advisor():
    """Demonstrate manufacturing advisor capabilities."""
    print("Manufacturing Advisor Demo")
    print("=" * 40)

    advisor = ManufacturingAdvisor()

    # Define requirements
    requirements = {
        "strength_requirement": "medium",
        "cost_target": 50.0,
        "lead_time_days": 14,
        "surface_finish": "standard",
    }

    # Get manufacturing advice
    advice = advisor.analyze_manufacturability(
        "demo_bracket", quantity=50, requirements=requirements
    )

    print(f"Analysis successful: {len(advice.recommended_materials) > 0}")

    print("\\nRecommended Materials:")
    for i, material in enumerate(advice.recommended_materials[:2], 1):
        print(f"  {i}. {material.name}")
        print(f"     Yield Strength: {material.yield_strength} MPa")
        print(f"     Cost: ${material.cost_per_kg:.2f}/kg")
        print(f"     Availability: {material.availability}")

    print("\\nRecommended Processes:")
    for i, process in enumerate(advice.recommended_processes[:2], 1):
        print(f"  {i}. {process.process.value.title()}")
        print(f"     Suitability Score: {process.suitability_score:.1f}/10")
        print(f"     Lead Time: {process.lead_time_days} days")
        print(
            f"     Key Advantage: {process.advantages[0] if process.advantages else 'N/A'}"
        )

    print("\\nCost Estimates:")
    for i, cost in enumerate(advice.cost_estimates[:1], 1):
        print(
            f"  Option {i}: ${cost.total_cost:.2f} total (${cost.cost_per_unit:.2f}/unit)"
        )
        print(f"     Material: ${cost.cost_breakdown[CostCategory.MATERIAL_COST]:.2f}")
        print(f"     Labor: ${cost.cost_breakdown[CostCategory.LABOR_COST]:.2f}")

    print("\\nDFM Recommendations:")
    for rec in advice.dfm_recommendations[:3]:
        print(f"  • {rec}")

    print(f"\\nTimeline Estimate: {advice.timeline_estimate}")


if __name__ == "__main__":
    demo_manufacturing_advisor()
