from unittest.mock import Mock, patch

# Tests for advanced geometry operations without real FreeCAD


@patch("freecad_ai_addon.agent.geometry_agent.App")
def test_extrude_from_sketch_mock(mock_app):
    from freecad_ai_addon.agent.geometry_agent import GeometryAgent

    mock_doc = Mock()
    mock_sketch = Mock()
    mock_sketch.TypeId = "Sketcher::SketchObject"  # triggers PartDesign path first
    mock_pad = Mock()

    # Active document & object retrieval
    mock_app.ActiveDocument = mock_doc
    mock_doc.getObject.return_value = mock_sketch

    # addObject returns pad for PartDesign::Pad then fallback for others
    def add_object_side_effect(type_id, name):
        if type_id == "PartDesign::Pad":
            mock_pad.Name = name
            mock_pad.Shape = Mock(Volume=123.4)
            return mock_pad
        elif type_id == "Part::Extrusion":
            extr = Mock()
            extr.Name = name
            extr.Shape = Mock(Volume=120.0)
            return extr
        else:
            obj = Mock()
            obj.Name = name
            return obj

    mock_doc.addObject.side_effect = add_object_side_effect

    agent = GeometryAgent()
    params = {"operation": "extrude_from_sketch", "sketch": "Sketch001", "length": 15.0}
    task = type("T", (), {"parameters": params})
    result = agent.execute_task(task)
    assert result.status.name == "COMPLETED"
    assert result.result_data["length"] == 15.0
    assert result.result_data["volume"] == 123.4


@patch("freecad_ai_addon.agent.geometry_agent.App")
def test_pocket_from_sketch_mock(mock_app):
    from freecad_ai_addon.agent.geometry_agent import GeometryAgent

    mock_doc = Mock()
    mock_sketch = Mock()
    mock_base = Mock()
    mock_cut = Mock()
    mock_cut.Shape = Mock(Volume=80.0)

    mock_app.ActiveDocument = mock_doc

    def get_object_side_effect(name):
        if name == "Sketch001":
            return mock_sketch
        if name == "BaseObj":
            return mock_base
        return None

    mock_doc.getObject.side_effect = get_object_side_effect

    def add_object_side_effect(type_id, name):
        if type_id == "Part::Extrusion":
            extr = Mock()
            extr.Name = name
            return extr
        if type_id == "Part::Cut":
            mock_cut.Name = name
            return mock_cut
        return Mock()

    mock_doc.addObject.side_effect = add_object_side_effect

    agent = GeometryAgent()
    params = {
        "operation": "pocket_from_sketch",
        "sketch": "Sketch001",
        "depth": 5.0,
        "base_object": "BaseObj",
    }
    task = type("T", (), {"parameters": params})
    result = agent.execute_task(task)
    assert result.status.name == "COMPLETED"
    assert result.result_data["depth"] == 5.0
    assert result.result_data["volume"] == 80.0


@patch("freecad_ai_addon.agent.geometry_agent.App")
def test_loft_profiles_mock(mock_app):
    from freecad_ai_addon.agent.geometry_agent import GeometryAgent

    mock_doc = Mock()
    mock_prof1 = Mock()
    mock_prof2 = Mock()
    mock_loft = Mock()
    mock_loft.Shape = Mock(Volume=200.0)

    mock_app.ActiveDocument = mock_doc

    def get_object_side_effect(name):
        if name == "ProfA":
            return mock_prof1
        if name == "ProfB":
            return mock_prof2
        return None

    mock_doc.getObject.side_effect = get_object_side_effect

    def add_object_side_effect(type_id, name):
        if type_id == "Part::Loft":
            mock_loft.Name = name
            return mock_loft
        return Mock()

    mock_doc.addObject.side_effect = add_object_side_effect

    agent = GeometryAgent()
    params = {
        "operation": "loft_profiles",
        "profiles": ["ProfA", "ProfB"],
        "solid": True,
    }
    task = type("T", (), {"parameters": params})
    result = agent.execute_task(task)
    assert result.status.name == "COMPLETED"
    assert result.result_data["profiles"] == ["ProfA", "ProfB"]
    assert result.result_data["volume"] == 200.0


@patch("freecad_ai_addon.agent.geometry_agent.App")
def test_sweep_profile_mock(mock_app):
    from freecad_ai_addon.agent.geometry_agent import GeometryAgent

    mock_doc = Mock()
    mock_profile = Mock()
    mock_path = Mock()
    mock_sweep = Mock()
    mock_sweep.Shape = Mock(Volume=60.0)

    mock_app.ActiveDocument = mock_doc

    def get_object_side_effect(name):
        if name == "Prof":
            return mock_profile
        if name == "Path":
            return mock_path
        return None

    mock_doc.getObject.side_effect = get_object_side_effect

    def add_object_side_effect(type_id, name):
        if type_id == "Part::Sweep":
            mock_sweep.Name = name
            return mock_sweep
        return Mock()

    mock_doc.addObject.side_effect = add_object_side_effect

    agent = GeometryAgent()
    params = {"operation": "sweep_profile", "profile": "Prof", "path": "Path"}
    task = type("T", (), {"parameters": params})
    result = agent.execute_task(task)
    assert result.status.name == "COMPLETED"
    assert result.result_data["profile"] == "Prof"
    assert result.result_data["path"] == "Path"
    assert result.result_data["volume"] == 60.0
