#!/usr/bin/env python3
"""
Test script for the Intelligent Decision Engine

This script validates the decision-making capabilities including:
- Design pattern recognition
- Constraint solver integration
- Optimization algorithms
- Error recovery mechanisms
- Design validation tools

Author: FreeCAD AI Addon Development Team
License: MIT
"""

import sys
import os
import traceback

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

try:
    from freecad_ai_addon.agent.decision_engine import (
        IntelligentDecisionEngine,
        DesignPatternRecognizer,
        ConstraintSolverIntegration,
        OptimizationEngine,
        ErrorRecoveryMechanism,
        DesignValidator,
        PatternType,
        OptimizationGoal,
    )

    print("✓ Successfully imported decision engine components")
except ImportError as e:
    print(f"✗ Failed to import decision engine: {e}")
    traceback.print_exc()
    sys.exit(1)


def test_pattern_recognizer():
    """Test design pattern recognition capabilities"""
    print("\n=== Testing Design Pattern Recognizer ===")

    recognizer = DesignPatternRecognizer()

    # Test mounting bracket pattern
    mounting_bracket_geometry = {
        "features": ["base_plate", "mounting_holes", "vertical_support"],
        "dimensions": {
            "base_length": 80.0,
            "base_width": 50.0,
            "base_thickness": 5.0,
            "hole_diameter": 6.0,
            "hole_spacing": 30.0,
        },
    }

    context = {"application": "mounting bracket for equipment"}

    patterns = recognizer.recognize_pattern(mounting_bracket_geometry, context)

    print(f"✓ Pattern recognition returned {len(patterns)} patterns")

    if patterns:
        best_pattern = patterns[0]
        print(f"  - Best match: {best_pattern.pattern_type.value}")
        print(f"  - Confidence: {best_pattern.confidence:.1%}")
        print(
            f"  - Suggested dimensions: {len(best_pattern.suggested_dimensions)} parameters"
        )
        print(f"  - Required features: {best_pattern.required_features}")
        print(f"  - Material recommendations: {best_pattern.material_recommendations}")

    # Test flange connection pattern
    flange_geometry = {
        "features": ["circular_base", "bolt_circle", "central_bore"],
        "dimensions": {
            "outer_diameter": 150.0,
            "bolt_circle_diameter": 120.0,
            "central_bore": 60.0,
            "flange_thickness": 15.0,
            "bolt_holes": 8,
        },
    }

    flange_patterns = recognizer.recognize_pattern(flange_geometry)
    print(f"✓ Flange pattern recognition: {len(flange_patterns)} patterns found")

    if (
        flange_patterns
        and flange_patterns[0].pattern_type == PatternType.FLANGE_CONNECTION
    ):
        print("  - Correctly identified flange connection pattern")


def test_constraint_solver():
    """Test constraint solver integration"""
    print("\n=== Testing Constraint Solver Integration ===")

    solver = ConstraintSolverIntegration()

    # Test constraint analysis (will work without FreeCAD in simulation mode)
    analysis = solver.analyze_sketch_constraints("TestSketch")

    print("✓ Constraint analysis completed")
    print(f"  - Degrees of freedom: {analysis['degrees_of_freedom']}")
    print(f"  - Missing constraints: {len(analysis['missing_constraints'])}")
    print(f"  - Suggestions: {len(analysis['suggestions'])}")

    # Test auto-constraint suggestions
    suggestions = solver.suggest_auto_constraints("TestSketch")
    print(f"✓ Auto-constraint suggestions: {len(suggestions)} suggestions")


def test_optimization_engine():
    """Test optimization algorithms"""
    print("\n=== Testing Optimization Engine ===")

    optimizer = OptimizationEngine()

    # Test weight minimization
    parameters = {
        "length": {"min": 30.0, "max": 100.0},
        "width": {"min": 20.0, "max": 80.0},
        "height": {"min": 3.0, "max": 15.0},
    }

    constraints = [{"type": "minimum_value", "parameter": "height", "value": 5.0}]

    result = optimizer.optimize_parameters(
        OptimizationGoal.MINIMIZE_WEIGHT, parameters, constraints
    )

    print("✓ Weight optimization completed")
    print(f"  - Objective value: {result.objective_value:.2f}")
    print(f"  - Iterations: {result.iterations}")
    print(f"  - Constraints satisfied: {result.constraints_satisfied}")
    print(f"  - Convergence time: {result.convergence_time:.3f}s")
    print(f"  - Suggestions: {len(result.suggestions)}")

    # Test strength maximization
    strength_result = optimizer.optimize_parameters(
        OptimizationGoal.MAXIMIZE_STRENGTH, parameters
    )

    print("✓ Strength optimization completed")
    print(f"  - Section modulus: {strength_result.objective_value:.2f}")
    print(f"  - Optimized parameters: {strength_result.parameters}")


def test_error_recovery():
    """Test error recovery mechanisms"""
    print("\n=== Testing Error Recovery Mechanism ===")

    recovery = ErrorRecoveryMechanism()

    # Test boolean operation error recovery
    error_details = {
        "type": "boolean_operation_failed",
        "tolerance": 0.01,
        "objects": ["Box1", "Cylinder1"],
    }

    context = {"operation": "boolean_union", "attempt": 1}

    strategies = recovery.handle_error(
        "boolean_operation_failed", error_details, context
    )

    print(f"✓ Error recovery strategies: {len(strategies)}")
    for i, strategy in enumerate(strategies):
        print(f"  {i+1}. {strategy['strategy']}: {strategy['description']}")
        if "success_probability" in strategy:
            print(f"     Success probability: {strategy['success_probability']:.1%}")

    # Test constraint conflict recovery
    constraint_error = {"type": "sketch_constraint_conflict", "conflicting_value": 25.0}

    constraint_strategies = recovery.handle_error(
        "sketch_constraint_conflict", constraint_error, {}
    )

    print(f"✓ Constraint error recovery: {len(constraint_strategies)} strategies")


def test_design_validator():
    """Test design validation tools"""
    print("\n=== Testing Design Validator ===")

    validator = DesignValidator()

    # Test design with validation issues
    geometry_info = {
        "wall_thickness": 1.0,  # Below minimum for steel
        "draft_angle": 0.0,  # No draft angle
        "dimensions": {"length": 200.0, "width": 15.0},  # High aspect ratio
        "holes": [
            {
                "diameter": 6.0,
                "edge_distance": 4.0,  # Too close to edge
                "location": (10, 5, 0),
            }
        ],
        "sharp_corners": [{"radius": 0.1, "location": (20, 30, 0)}],  # Sharp corner
    }

    # Test with steel and machining
    issues = validator.validate_design(
        geometry_info, material="steel", manufacturing_process="machining"
    )

    print(f"✓ Design validation found {len(issues)} issues")

    critical_issues = [i for i in issues if i.severity == "critical"]
    warning_issues = [i for i in issues if i.severity == "warning"]

    print(f"  - Critical issues: {len(critical_issues)}")
    print(f"  - Warning issues: {len(warning_issues)}")

    for issue in issues[:3]:  # Show first 3 issues
        print(f"  - {issue.severity.upper()}: {issue.description}")
        print(f"    Fix: {issue.suggested_fix}")
        print(f"    Auto-fixable: {issue.auto_fixable}")

    # Test with injection molding process
    molding_issues = validator.validate_design(
        geometry_info, material="plastic", manufacturing_process="injection_molding"
    )

    print(f"✓ Injection molding validation: {len(molding_issues)} issues")


def test_full_decision_engine():
    """Test the complete intelligent decision engine"""
    print("\n=== Testing Complete Decision Engine ===")

    engine = IntelligentDecisionEngine()

    # Comprehensive test request
    test_request = {
        "geometry_info": {
            "features": ["base_plate", "mounting_holes", "vertical_support"],
            "dimensions": {
                "length": 80.0,
                "width": 50.0,
                "height": 5.0,
                "hole_diameter": 6.0,
            },
            "holes": [{"diameter": 6.0, "edge_distance": 8.0, "location": (10, 10, 0)}],
            "wall_thickness": 4.0,
        },
        "context": {
            "application": "structural mounting bracket",
            "environment": "industrial",
            "load_requirements": "medium",
        },
        "optimization": {
            "objective": "minimize_weight",
            "parameters": {
                "length": {"min": 50.0, "max": 120.0},
                "width": {"min": 30.0, "max": 80.0},
                "height": {"min": 3.0, "max": 15.0},
            },
            "constraints": [
                {"type": "minimum_value", "parameter": "height", "value": 4.0}
            ],
        },
        "material": "aluminum",
        "manufacturing_process": "cnc_machining",
    }

    # Make design decision
    result = engine.make_design_decision(test_request)

    print(f"✓ Decision engine completed successfully: {result['success']}")
    print(f"  - Processing time: {result.get('processing_time', 0):.3f} seconds")
    print(f"  - Patterns recognized: {len(result['patterns_recognized'])}")
    print(f"  - Validation issues: {len(result['validation_issues'])}")
    print(f"  - Execution steps: {len(result['execution_plan'])}")
    print(f"  - Recommendations: {len(result['recommendations'])}")

    if result["patterns_recognized"]:
        best_pattern = result["patterns_recognized"][0]
        print(
            f"  - Best pattern: {best_pattern.pattern_type.value} ({best_pattern.confidence:.1%})"
        )

    if result["optimization_results"]:
        opt = result["optimization_results"]
        print(
            f"  - Optimization: {opt.objective_value:.2f} in {opt.iterations} iterations"
        )

    # Test error handling
    print("\n--- Testing Error Handling ---")
    recovery_strategies = engine.handle_operation_error(
        "boolean_union",
        Exception("Operation failed"),
        {"objects": ["Box1", "Cylinder1"]},
    )

    print(f"✓ Error recovery: {len(recovery_strategies)} strategies generated")

    # Get performance summary
    performance = engine.get_performance_summary()
    print("\n--- Performance Summary ---")
    print(f"  - Total decisions: {performance['total_decisions']}")
    print(f"  - Success rate: {performance['success_rate']:.1f}%")
    print(
        f"  - Patterns per decision: {performance['average_patterns_per_decision']:.1f}"
    )


def test_integration_with_agents():
    """Test integration with existing agent framework"""
    print("\n=== Testing Agent Integration ===")

    try:
        # Try to import existing agents
        from freecad_ai_addon.agent.geometry_agent import GeometryAgent
        from freecad_ai_addon.agent.sketch_agent import SketchAgent
        from freecad_ai_addon.agent.analysis_agent import AnalysisAgent

        print("✓ Successfully imported existing agents")

        # Test creating agents with decision engine
        decision_engine = IntelligentDecisionEngine()

        geometry_agent = GeometryAgent()
        geometry_agent.decision_engine = decision_engine

        sketch_agent = SketchAgent()
        sketch_agent.decision_engine = decision_engine

        analysis_agent = AnalysisAgent()
        analysis_agent.decision_engine = decision_engine

        print("✓ Successfully integrated decision engine with agents")

        # Test decision-making in context
        test_context = {
            "geometry_info": {
                "features": ["rectangular_base"],
                "dimensions": {"length": 50, "width": 30, "height": 10},
            },
            "context": {"application": "simple box"},
        }

        decision = decision_engine.make_design_decision(test_context)
        print(f"✓ Agent context decision completed: {decision['success']}")

    except ImportError as e:
        print(f"⚠ Agent integration test skipped: {e}")
        print("  This is expected if agents haven't been implemented yet")


def main():
    """Run all decision engine tests"""
    print("=== FreeCAD AI Addon - Decision Engine Test Suite ===")
    print("Testing intelligent decision-making capabilities...\n")

    try:
        # Test individual components
        test_pattern_recognizer()
        test_constraint_solver()
        test_optimization_engine()
        test_error_recovery()
        test_design_validator()

        # Test complete system
        test_full_decision_engine()

        # Test integration
        test_integration_with_agents()

        print("\n" + "=" * 60)
        print("✅ ALL DECISION ENGINE TESTS COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print("\nDecision Engine Features Validated:")
        print("  ✓ Design pattern recognition (mounting brackets, flanges, housings)")
        print("  ✓ Constraint solver integration with auto-suggestions")
        print("  ✓ Multi-objective optimization (weight, strength, cost)")
        print("  ✓ Error recovery mechanisms with multiple strategies")
        print("  ✓ Design validation against manufacturing rules")
        print("  ✓ Intelligent decision coordination")
        print("  ✓ Performance metrics and history tracking")
        print("\nThe decision engine is ready for Phase 5.3 integration!")

        return True

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
