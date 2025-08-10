import pytest

from freecad_ai_addon.advanced_features import (
    ManufacturingAdvisor,
    ManufacturingProcess,
    CostCategory,
)


def test_analyze_manufacturability_mock_mode():
    advisor = ManufacturingAdvisor()
    advice = advisor.analyze_manufacturability(
        "NonExistentObject",
        quantity=25,
        requirements={
            "strength_requirement": "medium",
            "cost_target": 100.0,
        },
    )

    # Should return a ManufacturingAdvice object with mock data when FreeCAD is not available
    assert advice.recommended_materials, "Expected at least one recommended material"
    assert advice.recommended_processes, "Expected at least one recommended process"
    assert advice.cost_estimates, "Expected at least one cost estimate"
    assert isinstance(advice.timeline_estimate, str)


def test_estimate_manufacturing_cost_does_not_crash_mock():
    advisor = ManufacturingAdvisor()
    # Use a known material from the mock DB and a process that's supported
    estimate = advisor.estimate_manufacturing_cost(
        object_name="mock_object",
        quantity=10,
        process=ManufacturingProcess.MACHINING,
        material_name="steel_1018",
    )

    assert estimate.total_cost > 0
    assert estimate.quantity == 10
    assert estimate.cost_breakdown[CostCategory.MATERIAL_COST] > 0


@pytest.mark.parametrize(
    "process",
    [
        ManufacturingProcess.MACHINING,
        ManufacturingProcess.ADDITIVE_MANUFACTURING,
        ManufacturingProcess.INJECTION_MOLDING,
    ],
)
def test_recommendations_and_costs_for_various_processes(process):
    advisor = ManufacturingAdvisor()
    # Build a minimal design_characteristics similar to internal expectations
    dc = {
        "volume": 1000.0,
        "surface_area": 600.0,
        "complexity": "medium",
        "features": ["holes", "fillets"],
        "min_wall_thickness": 2.0,
        "aspect_ratio": 2.5,
        "symmetry": "partial",
        "tolerances": "standard",
    }

    # Private API sanity: recommend processes returns list; we won't assert internals
    recs = advisor._recommend_processes(dc, quantity=50)
    assert isinstance(recs, list)

    # Cost estimation path
    est = advisor.estimate_manufacturing_cost(
        object_name="mock_obj",
        quantity=50,
        process=process,
        material_name="steel_1018",
    )
    assert est.cost_per_unit > 0
