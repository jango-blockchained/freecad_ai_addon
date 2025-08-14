import pytest
from freecad_ai_addon.advanced_features import (
    ParametricDesignAssistant,
    DesignType,
    DesignOptimizationEngine,
    DesignRuleChecker,
)


def test_bearing_mount_template_generation():
    assistant = ParametricDesignAssistant()
    design = assistant.suggest_design_parameters(
        DesignType.BEARING_MOUNT, {"bearing_diameter": 30.0}
    )
    assert design.name.lower().startswith("configurable")
    assert "bearing_diameter" in design.parameters
    script = assistant.generate_freecad_script(design)
    # Should contain FreeCAD script preamble
    assert "FreeCAD" in script and "bearing_diameter" in script


def test_optimization_opportunity_suggestions():
    engine = DesignOptimizationEngine()
    opportunities = engine.suggest_optimization_opportunities("DemoPart")
    assert "weight_reduction" in opportunities
    assert opportunities["weight_reduction"]["potential_reduction"].endswith("%")


def test_design_rule_checker_mock_report():
    checker = DesignRuleChecker()
    report = checker.check_design("ExamplePart")
    # In headless/mock mode we expect a non-empty violations list or at least a valid report
    assert report.total_rules_checked >= 0
    assert report.overall_score >= 0
    # Ensure summary keys present
    assert report.summary is not None
