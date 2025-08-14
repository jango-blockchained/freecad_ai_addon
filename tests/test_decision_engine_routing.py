from freecad_ai_addon.agent.decision_engine import IntelligentDecisionEngine


def test_decision_engine_operation_routing_basic():
    engine = IntelligentDecisionEngine()
    req = {"desired_operations": ["extrude", "pocket", "loft", "sweep", "create_box"]}
    result = engine.make_design_decision(req)
    assert result["success"] is True
    routed = result.get("recommended_operations")
    assert routed is not None
    # Ensure mapping applied
    assert "extrude_from_sketch" in routed
    assert "pocket_from_sketch" in routed
    assert "loft_profiles" in routed
    assert "sweep_profile" in routed
    # Unmapped passes through
    assert "create_box" in routed


def test_decision_engine_routing_recommendations_string():
    engine = IntelligentDecisionEngine()
    req = {"desired_operations": ["extrude"]}
    result = engine.make_design_decision(req)
    assert any(
        "extrude_from_sketch" in r
        for r in [";".join(result.get("recommended_operations", []))]
    )
