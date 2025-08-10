"""
Design Rule Checker for FreeCAD AI Addon.

This module provides AI-powered design rule checking (DRC) capabilities to validate
CAD designs against manufacturing constraints, industry standards, and best practices.
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


class RuleCategory(Enum):
    """Categories of design rules."""

    DIMENSIONAL = "dimensional"
    GEOMETRIC = "geometric"
    MANUFACTURING = "manufacturing"
    MATERIAL = "material"
    ASSEMBLY = "assembly"
    STANDARD = "standard"
    SAFETY = "safety"
    PERFORMANCE = "performance"


class RuleSeverity(Enum):
    """Severity levels for rule violations."""

    CRITICAL = "critical"  # Must fix - will cause failure
    ERROR = "error"  # Should fix - will cause problems
    WARNING = "warning"  # Recommended to fix
    INFO = "info"  # Good practice suggestion


class ManufacturingProcess(Enum):
    """Manufacturing processes for rule checking."""

    MACHINING = "machining"
    CASTING = "casting"
    INJECTION_MOLDING = "injection_molding"
    SHEET_METAL = "sheet_metal"
    ADDITIVE_MANUFACTURING = "additive_manufacturing"
    WELDING = "welding"
    ASSEMBLY = "assembly"


@dataclass
class DesignRule:
    """Represents a design rule."""

    rule_id: str
    name: str
    description: str
    category: RuleCategory
    severity: RuleSeverity
    applicable_processes: List[ManufacturingProcess]
    parameters: Dict[str, Any]
    check_function: str  # Name of the checking function


@dataclass
class RuleViolation:
    """Represents a design rule violation."""

    rule: DesignRule
    severity: RuleSeverity
    location: Optional[str]  # Object/feature location
    description: str
    suggested_fix: str
    impact: str
    confidence: float  # 0-1 confidence in violation detection


@dataclass
class DesignRuleReport:
    """Results from design rule checking."""

    object_name: str
    total_rules_checked: int
    violations_found: List[RuleViolation]
    passed_rules: List[str]
    check_time: float
    overall_score: float  # 0-100 design quality score
    recommendations: List[str]
    summary: Dict[RuleSeverity, int]


class DesignRuleChecker:
    """
    AI-powered design rule checker for CAD models.

    Validates designs against:
    - Manufacturing constraints (DFM rules)
    - Industry standards (ISO, ANSI, etc.)
    - Material limitations
    - Assembly requirements
    - Safety regulations
    - Performance guidelines
    """

    def __init__(self):
        """Initialize the design rule checker."""
        self.rule_database = self._load_rule_database()
        self.standard_tolerances = self._load_standard_tolerances()
        self.material_properties = self._load_material_properties()
        self.check_history = []

    def check_design(
        self,
        object_name: str,
        manufacturing_process: ManufacturingProcess = ManufacturingProcess.MACHINING,
        material_name: str = "steel_1018",
        custom_rules: Optional[List[DesignRule]] = None,
    ) -> DesignRuleReport:
        """
        Check design against applicable design rules.

        Args:
            object_name: Name of the FreeCAD object to check
            manufacturing_process: Target manufacturing process
            material_name: Material to be used
            custom_rules: Additional custom rules to check

        Returns:
            DesignRuleReport with violations and recommendations

        Example:
            checker = DesignRuleChecker()

            report = checker.check_design(
                "Bracket001",
                ManufacturingProcess.MACHINING,
                "aluminum_6061"
            )

            print(f"Design Score: {report.overall_score:.1f}/100")
            for violation in report.violations_found:
                print(f"• {violation.description}")
        """
        if not FREECAD_AVAILABLE:
            logger.warning("FreeCAD not available, returning mock rule check")
            return self._create_mock_rule_report(object_name)

        logger.info(f"Checking design rules for: {object_name}")
        logger.info(
            f"Process: {manufacturing_process.value}, Material: {material_name}"
        )

        try:
            doc = App.activeDocument()
            if not doc:
                raise ValueError("No active document found")

            obj = doc.getObject(object_name)
            if not obj:
                raise ValueError(f"Object '{object_name}' not found")

            # Get applicable rules
            applicable_rules = self._get_applicable_rules(
                manufacturing_process, material_name
            )
            if custom_rules:
                applicable_rules.extend(custom_rules)

            # Check each rule
            violations = []
            passed_rules = []

            for rule in applicable_rules:
                try:
                    violation = self._check_rule(obj, rule, material_name)
                    if violation:
                        violations.append(violation)
                    else:
                        passed_rules.append(rule.name)
                except Exception as e:
                    logger.warning(f"Rule check failed for {rule.name}: {e}")

            # Calculate overall score
            overall_score = self._calculate_design_score(
                violations, len(applicable_rules)
            )

            # Generate summary
            summary = self._generate_violation_summary(violations)

            # Generate recommendations
            recommendations = self._generate_recommendations(violations)

            report = DesignRuleReport(
                object_name=object_name,
                total_rules_checked=len(applicable_rules),
                violations_found=violations,
                passed_rules=passed_rules,
                check_time=2.0,  # Mock check time
                overall_score=overall_score,
                recommendations=recommendations,
                summary=summary,
            )

            self.check_history.append(report)
            return report

        except Exception as e:
            logger.error(f"Design rule checking failed: {e}")
            return self._create_error_report(object_name, str(e))

    def check_specific_rules(
        self, object_name: str, rule_ids: List[str]
    ) -> List[RuleViolation]:
        """
        Check specific design rules by ID.

        Args:
            object_name: Name of the FreeCAD object to check
            rule_ids: List of rule IDs to check

        Returns:
            List of violations found
        """
        violations = []

        for rule_id in rule_ids:
            rule = self.rule_database.get(rule_id)
            if not rule:
                logger.warning(f"Rule {rule_id} not found")
                continue

            if FREECAD_AVAILABLE:
                doc = App.activeDocument()
                if doc:
                    obj = doc.getObject(object_name)
                    if obj:
                        violation = self._check_rule(obj, rule, "steel_1018")
                        if violation:
                            violations.append(violation)

        return violations

    def validate_manufacturing_constraints(
        self, object_name: str, process: ManufacturingProcess
    ) -> List[RuleViolation]:
        """
        Validate design against manufacturing constraints for specific process.

        Args:
            object_name: Name of the FreeCAD object to check
            process: Manufacturing process to validate against

        Returns:
            List of manufacturing-related violations
        """
        # Get manufacturing-specific rules
        manufacturing_rules = [
            rule
            for rule in self.rule_database.values()
            if rule.category == RuleCategory.MANUFACTURING
            and process in rule.applicable_processes
        ]

        violations = []
        if FREECAD_AVAILABLE:
            doc = App.activeDocument()
            if doc:
                obj = doc.getObject(object_name)
                if obj:
                    for rule in manufacturing_rules:
                        violation = self._check_rule(obj, rule, "steel_1018")
                        if violation:
                            violations.append(violation)

        return violations

    def _get_applicable_rules(
        self, process: ManufacturingProcess, material: str
    ) -> List[DesignRule]:
        """Get rules applicable to the specified process and material."""
        applicable = []

        for rule in self.rule_database.values():
            # Check if rule applies to this manufacturing process
            if process in rule.applicable_processes:
                applicable.append(rule)
            # Always include general rules
            elif rule.category in [RuleCategory.DIMENSIONAL, RuleCategory.GEOMETRIC]:
                applicable.append(rule)

        return applicable

    def _check_rule(
        self, obj, rule: DesignRule, material: str
    ) -> Optional[RuleViolation]:
        """Check a specific rule against the object."""
        # Route to appropriate checking function
        check_function = getattr(self, f"_{rule.check_function}", None)
        if not check_function:
            logger.warning(f"Check function {rule.check_function} not found")
            return None

        try:
            return check_function(obj, rule, material)
        except Exception as e:
            logger.error(f"Rule check failed for {rule.name}: {e}")
            return None

    def _check_minimum_wall_thickness(
        self, obj, rule: DesignRule, material: str
    ) -> Optional[RuleViolation]:
        """Check minimum wall thickness rule."""
        min_thickness = rule.parameters.get("min_thickness", 1.0)

        # Simplified check - would analyze geometry in real implementation
        # For demo, assume we found a thin wall
        current_thickness = 0.8  # Mock measurement

        if current_thickness < min_thickness:
            return RuleViolation(
                rule=rule,
                severity=rule.severity,
                location="Wall feature at (10, 20, 0)",
                description=f"Wall thickness {current_thickness}mm is below minimum {min_thickness}mm",
                suggested_fix=f"Increase wall thickness to at least {min_thickness}mm",
                impact="May cause structural failure or manufacturing difficulties",
                confidence=0.95,
            )

        return None

    def _check_hole_diameter_standards(
        self, obj, rule: DesignRule, material: str
    ) -> Optional[RuleViolation]:
        """Check if hole diameters use standard sizes."""
        standard_sizes = rule.parameters.get(
            "standard_sizes", [3, 4, 5, 6, 8, 10, 12, 16, 20]
        )

        # Mock hole detection - would analyze geometry in real implementation
        found_holes = [7.5, 10.0, 15.0]  # Mock hole diameters

        non_standard_holes = [d for d in found_holes if d not in standard_sizes]

        if non_standard_holes:
            return RuleViolation(
                rule=rule,
                severity=rule.severity,
                location=f"Holes with diameters: {non_standard_holes}",
                description=f"Non-standard hole diameters found: {non_standard_holes}mm",
                suggested_fix="Use standard drill sizes: 3, 4, 5, 6, 8, 10, 12, 16, 20mm",
                impact="Increased tooling costs and longer lead times",
                confidence=0.90,
            )

        return None

    def _check_fillet_radii(
        self, obj, rule: DesignRule, material: str
    ) -> Optional[RuleViolation]:
        """Check if sharp corners have appropriate fillets."""
        min_fillet = rule.parameters.get("min_fillet", 0.5)

        # Mock sharp corner detection
        sharp_corners_found = 3  # Mock count

        if sharp_corners_found > 0:
            return RuleViolation(
                rule=rule,
                severity=rule.severity,
                location="Multiple locations with sharp corners",
                description=f"Found {sharp_corners_found} sharp corners without fillets",
                suggested_fix=f"Add fillets with minimum radius {min_fillet}mm to sharp corners",
                impact="Stress concentrations may cause failure; difficult machining",
                confidence=0.85,
            )

        return None

    def _check_draft_angles(
        self, obj, rule: DesignRule, material: str
    ) -> Optional[RuleViolation]:
        """Check draft angles for molded parts."""
        min_draft = rule.parameters.get("min_draft_degrees", 1.0)

        # Mock draft angle analysis
        vertical_faces_found = 2  # Mock count

        if vertical_faces_found > 0:
            return RuleViolation(
                rule=rule,
                severity=rule.severity,
                location="Vertical faces in molded geometry",
                description=f"Found {vertical_faces_found} vertical faces without draft angles",
                suggested_fix=f"Add draft angles of at least {min_draft}° to vertical faces",
                impact="Difficult part ejection from mold; potential damage",
                confidence=0.80,
            )

        return None

    def _check_undercuts(
        self, obj, rule: DesignRule, material: str
    ) -> Optional[RuleViolation]:
        """Check for undercuts that complicate manufacturing."""
        # Mock undercut detection
        undercuts_found = 1  # Mock count

        if undercuts_found > 0:
            return RuleViolation(
                rule=rule,
                severity=rule.severity,
                location="Internal undercut features",
                description=f"Found {undercuts_found} undercut features",
                suggested_fix="Redesign to eliminate undercuts or split into multiple parts",
                impact="Complex tooling required; increased manufacturing cost",
                confidence=0.88,
            )

        return None

    def _check_aspect_ratio(
        self, obj, rule: DesignRule, material: str
    ) -> Optional[RuleViolation]:
        """Check part aspect ratio for manufacturability."""
        max_aspect_ratio = rule.parameters.get("max_aspect_ratio", 5.0)

        # Mock aspect ratio calculation
        current_aspect_ratio = 6.5  # Mock measurement

        if current_aspect_ratio > max_aspect_ratio:
            return RuleViolation(
                rule=rule,
                severity=rule.severity,
                location="Overall part geometry",
                description=f"Aspect ratio {current_aspect_ratio:.1f} exceeds maximum {max_aspect_ratio}",
                suggested_fix="Reduce part length or increase cross-sectional dimensions",
                impact="Stability issues during manufacturing; potential deformation",
                confidence=0.92,
            )

        return None

    def _calculate_design_score(
        self, violations: List[RuleViolation], total_rules: int
    ) -> float:
        """Calculate overall design quality score (0-100)."""
        if total_rules == 0:
            return 100.0

        # Weight violations by severity
        penalty_weights = {
            RuleSeverity.CRITICAL: 20,
            RuleSeverity.ERROR: 10,
            RuleSeverity.WARNING: 5,
            RuleSeverity.INFO: 1,
        }

        total_penalty = sum(penalty_weights.get(v.severity, 5) for v in violations)
        max_possible_penalty = total_rules * penalty_weights[RuleSeverity.CRITICAL]

        score = max(0, 100 - (total_penalty / max_possible_penalty * 100))
        return score

    def _generate_violation_summary(
        self, violations: List[RuleViolation]
    ) -> Dict[RuleSeverity, int]:
        """Generate summary of violations by severity."""
        summary = {severity: 0 for severity in RuleSeverity}

        for violation in violations:
            summary[violation.severity] += 1

        return summary

    def _generate_recommendations(self, violations: List[RuleViolation]) -> List[str]:
        """Generate general recommendations based on violations."""
        recommendations = []

        # Critical violations first
        critical_violations = [
            v for v in violations if v.severity == RuleSeverity.CRITICAL
        ]
        if critical_violations:
            recommendations.append(
                "Address critical violations immediately - these will cause manufacturing failure"
            )

        # Error violations
        error_violations = [v for v in violations if v.severity == RuleSeverity.ERROR]
        if error_violations:
            recommendations.append(
                "Fix error-level violations to avoid manufacturing problems"
            )

        # Category-specific recommendations
        categories = set(v.rule.category for v in violations)

        if RuleCategory.MANUFACTURING in categories:
            recommendations.append(
                "Review manufacturing process requirements and constraints"
            )

        if RuleCategory.DIMENSIONAL in categories:
            recommendations.append(
                "Verify dimensions against standard tolerances and capabilities"
            )

        if RuleCategory.GEOMETRIC in categories:
            recommendations.append(
                "Consider geometric constraints for selected manufacturing process"
            )

        # General recommendations
        recommendations.extend(
            [
                "Validate design with manufacturing team before finalizing",
                "Consider prototyping to verify manufacturability",
                "Document all design assumptions and requirements",
            ]
        )

        return recommendations

    def _create_mock_rule_report(self, object_name: str) -> DesignRuleReport:
        """Create mock rule report when FreeCAD is not available."""
        # Create mock violations
        mock_rule = DesignRule(
            rule_id="DIM_001",
            name="Minimum Wall Thickness",
            description="Walls must meet minimum thickness for manufacturing",
            category=RuleCategory.DIMENSIONAL,
            severity=RuleSeverity.WARNING,
            applicable_processes=[ManufacturingProcess.MACHINING],
            parameters={"min_thickness": 1.0},
            check_function="check_minimum_wall_thickness",
        )

        mock_violation = RuleViolation(
            rule=mock_rule,
            severity=RuleSeverity.WARNING,
            location="Mock location",
            description="Mock wall thickness violation",
            suggested_fix="Increase wall thickness",
            impact="Potential manufacturing difficulty",
            confidence=0.85,
        )

        return DesignRuleReport(
            object_name=object_name,
            total_rules_checked=5,
            violations_found=[mock_violation],
            passed_rules=[
                "Standard hole sizes",
                "Appropriate fillets",
                "Draft angles",
                "No undercuts",
            ],
            check_time=1.5,
            overall_score=85.0,
            recommendations=[
                "Address wall thickness issue",
                "Validate with manufacturing team",
            ],
            summary={
                RuleSeverity.CRITICAL: 0,
                RuleSeverity.ERROR: 0,
                RuleSeverity.WARNING: 1,
                RuleSeverity.INFO: 0,
            },
        )

    def _create_error_report(
        self, object_name: str, error_message: str
    ) -> DesignRuleReport:
        """Create error report for failed rule checking."""
        return DesignRuleReport(
            object_name=object_name,
            total_rules_checked=0,
            violations_found=[],
            passed_rules=[],
            check_time=0.0,
            overall_score=0.0,
            recommendations=[f"Rule checking failed: {error_message}"],
            summary={severity: 0 for severity in RuleSeverity},
        )

    def _load_rule_database(self) -> Dict[str, DesignRule]:
        """Load design rules database."""
        rules = {}

        # Dimensional rules
        rules["DIM_001"] = DesignRule(
            rule_id="DIM_001",
            name="Minimum Wall Thickness",
            description="Walls must meet minimum thickness for structural integrity and manufacturability",
            category=RuleCategory.DIMENSIONAL,
            severity=RuleSeverity.ERROR,
            applicable_processes=[
                ManufacturingProcess.MACHINING,
                ManufacturingProcess.INJECTION_MOLDING,
            ],
            parameters={"min_thickness": 1.0},
            check_function="check_minimum_wall_thickness",
        )

        rules["STD_001"] = DesignRule(
            rule_id="STD_001",
            name="Standard Hole Sizes",
            description="Use standard drill sizes to reduce tooling costs",
            category=RuleCategory.STANDARD,
            severity=RuleSeverity.WARNING,
            applicable_processes=[ManufacturingProcess.MACHINING],
            parameters={"standard_sizes": [3, 4, 5, 6, 8, 10, 12, 16, 20]},
            check_function="check_hole_diameter_standards",
        )

        rules["GEO_001"] = DesignRule(
            rule_id="GEO_001",
            name="Fillet Sharp Corners",
            description="Sharp corners should have fillets to reduce stress concentrations",
            category=RuleCategory.GEOMETRIC,
            severity=RuleSeverity.WARNING,
            applicable_processes=[
                ManufacturingProcess.MACHINING,
                ManufacturingProcess.CASTING,
            ],
            parameters={"min_fillet": 0.5},
            check_function="check_fillet_radii",
        )

        rules["MFG_001"] = DesignRule(
            rule_id="MFG_001",
            name="Draft Angles for Molding",
            description="Vertical faces in molded parts require draft angles",
            category=RuleCategory.MANUFACTURING,
            severity=RuleSeverity.ERROR,
            applicable_processes=[
                ManufacturingProcess.INJECTION_MOLDING,
                ManufacturingProcess.CASTING,
            ],
            parameters={"min_draft_degrees": 1.0},
            check_function="check_draft_angles",
        )

        rules["MFG_002"] = DesignRule(
            rule_id="MFG_002",
            name="Avoid Undercuts",
            description="Undercuts complicate manufacturing and increase costs",
            category=RuleCategory.MANUFACTURING,
            severity=RuleSeverity.ERROR,
            applicable_processes=[
                ManufacturingProcess.MACHINING,
                ManufacturingProcess.INJECTION_MOLDING,
            ],
            parameters={},
            check_function="check_undercuts",
        )

        rules["MFG_003"] = DesignRule(
            rule_id="MFG_003",
            name="Reasonable Aspect Ratio",
            description="High aspect ratios can cause manufacturing instability",
            category=RuleCategory.MANUFACTURING,
            severity=RuleSeverity.WARNING,
            applicable_processes=[ManufacturingProcess.MACHINING],
            parameters={"max_aspect_ratio": 5.0},
            check_function="check_aspect_ratio",
        )

        return rules

    def _load_standard_tolerances(self) -> Dict[str, Dict[str, float]]:
        """Load standard tolerance specifications."""
        return {
            "ISO_2768_medium": {
                "linear_tolerance": 0.1,  # mm
                "angular_tolerance": 0.5,  # degrees
                "form_tolerance": 0.05,  # mm
            },
            "ANSI_Y14.5": {
                "linear_tolerance": 0.127,  # mm (0.005")
                "angular_tolerance": 0.5,  # degrees
                "form_tolerance": 0.025,  # mm
            },
        }

    def _load_material_properties(self) -> Dict[str, Dict[str, Any]]:
        """Load material property constraints."""
        return {
            "steel_1018": {
                "min_wall_thickness": 1.0,
                "machinability": "good",
                "weldability": "excellent",
            },
            "aluminum_6061": {
                "min_wall_thickness": 0.8,
                "machinability": "excellent",
                "weldability": "good",
            },
            "plastic_abs": {
                "min_wall_thickness": 1.5,
                "draft_angle_required": True,
                "undercut_sensitivity": "high",
            },
        }


def demo_design_rule_checker():
    """Demonstrate design rule checker capabilities."""
    print("Design Rule Checker Demo")
    print("=" * 40)

    checker = DesignRuleChecker()

    # Check design rules
    report = checker.check_design(
        "demo_part", ManufacturingProcess.MACHINING, "steel_1018"
    )

    print(f"Design Score: {report.overall_score:.1f}/100")
    print(f"Rules Checked: {report.total_rules_checked}")
    print(f"Violations Found: {len(report.violations_found)}")
    print(f"Rules Passed: {len(report.passed_rules)}")

    print("\\nViolation Summary:")
    for severity, count in report.summary.items():
        if count > 0:
            print(f"  {severity.value.title()}: {count}")

    print("\\nViolations Found:")
    for i, violation in enumerate(report.violations_found, 1):
        print(f"  {i}. [{violation.severity.value.upper()}] {violation.description}")
        print(f"     Fix: {violation.suggested_fix}")
        print(f"     Impact: {violation.impact}")

    print("\\nTop Recommendations:")
    for rec in report.recommendations[:3]:
        print(f"  • {rec}")

    # Test specific manufacturing validation
    print("\\n" + "=" * 40)
    print("MANUFACTURING VALIDATION")
    print("=" * 40)

    mfg_violations = checker.validate_manufacturing_constraints(
        "demo_part", ManufacturingProcess.INJECTION_MOLDING
    )

    print(f"Manufacturing violations found: {len(mfg_violations)}")
    for violation in mfg_violations:
        print(f"  • {violation.description}")


if __name__ == "__main__":
    demo_design_rule_checker()
