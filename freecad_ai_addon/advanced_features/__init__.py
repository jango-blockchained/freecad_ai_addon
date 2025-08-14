"""Advanced AI / CAD feature toolkit for the FreeCAD AI Addon.

This package aggregates higher-level, domain-specific assistants used by
the agent framework and UI commands. They are intentionally designed to:

* Degrade gracefully when FreeCAD isn't available (unit‑test friendly)
* Provide pure‑Python data structures (dataclasses / dict output helpers)
* Offer light service facades for JSON serialization & conversation export

Exported categories:
  Manufacturing   – ``ManufacturingAdvisor`` (DFM, cost, materials)
  Parametrics     – ``ParametricDesignAssistant`` (configurable design templates)
  Optimization    – ``DesignOptimizationEngine`` (weight/stress/etc. suggestions)
  Feature Recon   – ``FeatureRecognitionAI`` + ``FeatureRecognitionService``
  Rule Checking   – ``DesignRuleChecker`` (DFM / standards / safety rules)
  Simulation      – ``SimulationAssistant`` (FEA/thermal recommendations)
"""

from .manufacturing_advisor import (
    ManufacturingAdvisor,
    ManufacturingProcess,
    MaterialCategory,
    CostCategory,
    MaterialProperties,
    ProcessRecommendation,
    CostEstimate,
    ManufacturingAdvice,
)
from .parametric_design_assistant import (
    ParametricDesignAssistant,
    ParametricDesign,
    Parameter,
    DesignType,
)
from .design_optimization import (
    DesignOptimizationEngine,
    OptimizationGoal,
    OptimizationMethod,
    OptimizationVariable,
    OptimizationConstraint,
)
from .feature_recognition import (
    FeatureRecognitionAI,
    FeatureType,
    GeometricFeature,
    AnalysisResult,
)
from .feature_recognition_service import FeatureRecognitionService
from .design_rule_checker import (
    DesignRuleChecker,
    DesignRule,
    DesignRuleReport,
    RuleCategory,
    RuleSeverity,
    ManufacturingProcess as DRCManufacturingProcess,
)
from .simulation_assistant import (
    SimulationAssistant,
    SimulationType,
    SimulationRecommendation,
)

__all__ = [
    # Manufacturing
    "ManufacturingAdvisor",
    "ManufacturingProcess",
    "MaterialCategory",
    "CostCategory",
    "MaterialProperties",
    "ProcessRecommendation",
    "CostEstimate",
    "ManufacturingAdvice",
    # Parametric design
    "ParametricDesignAssistant",
    "ParametricDesign",
    "Parameter",
    "DesignType",
    # Optimization
    "DesignOptimizationEngine",
    "OptimizationGoal",
    "OptimizationMethod",
    "OptimizationVariable",
    "OptimizationConstraint",
    # Feature recognition
    "FeatureRecognitionAI",
    "FeatureRecognitionService",
    "FeatureType",
    "GeometricFeature",
    "AnalysisResult",
    # Design rule checking
    "DesignRuleChecker",
    "DesignRule",
    "DesignRuleReport",
    "RuleCategory",
    "RuleSeverity",
    "DRCManufacturingProcess",
    # Simulation
    "SimulationAssistant",
    "SimulationType",
    "SimulationRecommendation",
]
