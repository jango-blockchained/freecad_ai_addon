"""
Test suite for enhanced FreeCAD AI Addon features.

Tests the new parametric modeling, advanced sketch patterns,
and manufacturing analysis capabilities.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from freecad_ai_addon.agent.parametric_modeling import (
    ParametricFeature,
    ParametricModelBuilder,
)
from freecad_ai_addon.agent.advanced_sketch_patterns import AdvancedSketchPatterns
from freecad_ai_addon.agent.manufacturing_analyzer import ManufacturingAnalyzer


class TestParametricModeling:
    """Test parametric modeling capabilities."""

    def setup_method(self):
        """Set up test fixtures."""
        self.builder = ParametricModelBuilder()

    def test_parametric_feature_creation(self):
        """Test creating a parametric feature."""
        feature = ParametricFeature(
            "test_box", "box", {"length": 10.0, "width": 20.0, "height": 30.0}
        )

        assert feature.name == "test_box"
        assert feature.feature_type == "box"
        assert feature.parameters["length"] == 10.0
        assert len(feature.dependencies) == 0

    def test_feature_dependency_management(self):
        """Test feature dependency relationships."""
        base_feature = ParametricFeature("base", "box", {"length": 10})
        dependent_feature = ParametricFeature("dependent", "cylinder", {"radius": 5})

        dependent_feature.add_dependency(base_feature)

        assert base_feature in dependent_feature.dependencies
        assert dependent_feature in base_feature.dependent_features

    def test_parameter_updates(self):
        """Test parameter updates and propagation."""
        feature = ParametricFeature("test", "box", {"length": 10.0})

        result = feature.update_parameter("length", 15.0)
        assert result is True
        assert feature.parameters["length"] == 15.0

    @patch("freecad_ai_addon.agent.parametric_modeling.App")
    def test_create_parametric_feature(self, mock_app):
        """Test creating parametric features through builder."""
        mock_doc = Mock()
        mock_app.ActiveDocument = mock_doc
        mock_app.Vector = Mock(return_value=Mock())

        mock_obj = Mock()
        mock_doc.addObject.return_value = mock_obj

        result = self.builder.create_parametric_feature(
            "test_box", "box", {"length": 10.0, "width": 20.0, "height": 30.0}
        )

        assert result["status"] == "success"
        assert result["feature_name"] == "test_box"
        assert "test_box" in self.builder.features

    def test_design_templates(self):
        """Test design template creation."""
        available_templates = list(self.builder.feature_templates.keys())
        assert "mounting_bracket" in available_templates
        assert "bearing_mount" in available_templates
        assert "flange" in available_templates

    @patch("freecad_ai_addon.agent.parametric_modeling.App")
    def test_mounting_bracket_template(self, mock_app):
        """Test mounting bracket template creation."""
        mock_doc = Mock()
        mock_app.ActiveDocument = mock_doc
        mock_app.Vector = Mock(return_value=Mock())

        mock_obj = Mock()
        mock_doc.addObject.return_value = mock_obj

        result = self.builder.create_design_template(
            "mounting_bracket",
            {"base_length": 50.0, "base_width": 30.0, "bracket_height": 40.0},
        )

        assert result["status"] == "success"
        assert result["template_name"] == "mounting_bracket"
        assert len(result["created_features"]) > 0

    def test_feature_tree_info(self):
        """Test feature tree information retrieval."""
        # Add some features
        feature1 = ParametricFeature("f1", "box", {"length": 10})
        feature2 = ParametricFeature("f2", "cylinder", {"radius": 5})
        feature2.add_dependency(feature1)

        self.builder.features["f1"] = feature1
        self.builder.features["f2"] = feature2
        self.builder.feature_tree = [feature1, feature2]

        info = self.builder.get_feature_tree_info()

        assert info["total_features"] == 2
        assert len(info["feature_list"]) == 2
        assert "f1" in info["relationships"]
        assert "f2" in info["relationships"]


class TestAdvancedSketchPatterns:
    """Test advanced sketch patterns functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.patterns = AdvancedSketchPatterns()

    def test_pattern_library_initialization(self):
        """Test pattern library is properly initialized."""
        assert len(self.patterns.pattern_library) > 0
        assert "rectangular_hole_pattern" in self.patterns.pattern_library
        assert "circular_hole_pattern" in self.patterns.pattern_library
        assert "gear_tooth_pattern" in self.patterns.pattern_library

    def test_rectangular_hole_pattern(self):
        """Test rectangular hole pattern creation."""
        result = self.patterns.create_rectangular_hole_pattern(
            {
                "rows": 2,
                "cols": 3,
                "hole_diameter": 6.0,
                "row_spacing": 25.0,
                "col_spacing": 30.0,
            }
        )

        assert "geometry" in result
        assert len(result["geometry"]) == 6  # 2x3 = 6 holes
        assert result["pattern_info"]["total_holes"] == 6

        # Check first hole
        first_hole = result["geometry"][0]
        assert first_hole["type"] == "circle"
        assert first_hole["radius"] == 3.0  # diameter/2

    def test_circular_hole_pattern(self):
        """Test circular hole pattern creation."""
        result = self.patterns.create_circular_hole_pattern(
            {"count": 8, "radius": 30.0, "hole_diameter": 5.0, "center": (0, 0)}
        )

        assert "geometry" in result
        assert len(result["geometry"]) == 8
        assert result["pattern_info"]["count"] == 8

        # Check hole positions are on circle
        for hole in result["geometry"]:
            x, y = hole["center"]
            distance = (x**2 + y**2) ** 0.5
            assert abs(distance - 30.0) < 0.001  # Should be on 30mm radius

    def test_hexagonal_pattern(self):
        """Test hexagonal pattern creation."""
        result = self.patterns.create_hexagonal_pattern(
            {"rings": 2, "spacing": 10.0, "element_size": 3.0, "center": (0, 0)}
        )

        assert "geometry" in result
        # Center + 6 (ring 1) + 12 (ring 2) = 19 elements
        assert len(result["geometry"]) == 19
        assert result["pattern_info"]["rings"] == 2

    def test_gear_tooth_pattern(self):
        """Test gear tooth pattern creation."""
        result = self.patterns.create_gear_tooth_pattern(
            {
                "teeth_count": 20,
                "pitch_diameter": 50.0,
                "addendum": 2.5,
                "dedendum": 3.125,
            }
        )

        assert "geometry" in result
        assert result["pattern_info"]["teeth_count"] == 20
        # Should have multiple line segments per tooth
        assert len(result["geometry"]) > 20

    def test_mounting_holes_pattern(self):
        """Test mounting holes pattern creation."""
        result = self.patterns.create_mounting_holes(
            {"hole_type": "M6", "spacing": 25.0, "count": 4, "layout": "square"}
        )

        assert "geometry" in result
        # Square layout should create 4 holes (2x2)
        assert len(result["geometry"]) >= 4

    def test_sketch_slot_and_patterns_api_presence(self):
        """Ensure SketchActionLibrary exposes slot and pattern functions."""
        from freecad_ai_addon.agent.sketch_action_library import SketchActionLibrary

        lib = SketchActionLibrary()
        ops = lib.sketch_operations
        assert "add_slot" in ops
        assert "rectangular_pattern" in ops
        assert "polar_pattern" in ops
        assert "linear_pattern" in ops

    def test_geometry_agent_operations_registry(self):
        """Verify geometry agent supports new transformation operations."""
        from freecad_ai_addon.agent.geometry_agent import GeometryAgent

        agent = GeometryAgent()
        for op in [
            "mirror_object",
            "array_linear",
            "array_polar",
            "scale_object",
            "rotate_object",
            "translate_object",
        ]:
            assert op in agent.supported_operations

    @patch("freecad_ai_addon.agent.advanced_sketch_patterns.App")
    def test_parametric_sketch_creation(self, mock_app):
        """Test parametric sketch creation."""
        mock_doc = Mock()
        mock_app.ActiveDocument = mock_doc
        mock_app.Vector = Mock(return_value=Mock())

        mock_sketch = Mock()
        mock_doc.addObject.return_value = mock_sketch
        mock_doc.getObject.return_value = Mock()

        geometry = [
            {"type": "circle", "center": (0, 0), "radius": 5.0},
            {"type": "line", "start": (0, 0), "end": (10, 0)},
        ]

        constraints = [{"type": "radius", "geo": 0, "radius": 5.0}]

        result = self.patterns.create_parametric_sketch(
            "test_sketch", geometry, constraints
        )

        assert result["status"] == "success"
        assert result["sketch_name"] == "test_sketch"
        assert result["geometry_count"] == 2
        assert result["constraint_count"] == 1


class TestManufacturingAnalyzer:
    """Test manufacturing analysis capabilities."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = ManufacturingAnalyzer()

    def test_analyzer_initialization(self):
        """Test analyzer is properly initialized."""
        assert len(self.analyzer.analyzers) > 0
        assert "cnc_machining" in self.analyzer.analyzers
        assert "3d_printing" in self.analyzer.analyzers
        assert "injection_molding" in self.analyzer.analyzers

        # Check tool libraries
        assert "end_mills" in self.analyzer.cnc_tools
        assert "drills" in self.analyzer.cnc_tools

        # Check material database
        assert "aluminum" in self.analyzer.materials
        assert "steel" in self.analyzer.materials
        assert "plastic_pla" in self.analyzer.materials

    def test_material_properties(self):
        """Test material properties database."""
        aluminum = self.analyzer.materials["aluminum"]
        assert aluminum["density"] == 2.7
        assert aluminum["machinability"] == "excellent"
        assert "min_wall_thickness" in aluminum

        steel = self.analyzer.materials["steel"]
        assert steel["density"] == 7.85
        assert steel["machinability"] == "good"

    @patch("freecad_ai_addon.agent.manufacturing_analyzer.App")
    def test_cnc_machining_analysis(self, mock_app):
        """Test CNC machining analysis."""
        mock_doc = Mock()
        mock_app.ActiveDocument = mock_doc

        mock_obj = Mock()
        mock_shape = Mock()
        mock_shape.Volume = 100.0
        mock_shape.Area = 50.0
        mock_shape.BoundBox = Mock()
        mock_shape.BoundBox.XLength = 10.0
        mock_shape.BoundBox.YLength = 10.0
        mock_shape.BoundBox.ZLength = 10.0

        # Make sure Faces, Edges, and Vertexes are empty lists, not Mock objects
        mock_shape.Faces = []
        mock_shape.Edges = []
        mock_shape.Vertexes = []

        mock_obj.Shape = mock_shape
        mock_doc.getObject.return_value = mock_obj

        result = self.analyzer.analyze_manufacturing_feasibility(
            "test_object", "cnc_machining", "aluminum"
        )

        assert result["status"] == "success"
        assert result["process"] == "cnc_machining"
        assert result["material"] == "aluminum"
        assert "analysis" in result

        analysis = result["analysis"]
        assert analysis["process"] == "cnc_machining"
        assert "volume" in analysis
        assert "mass" in analysis

    @patch("freecad_ai_addon.agent.manufacturing_analyzer.App")
    def test_3d_printing_analysis(self, mock_app):
        """Test 3D printing analysis."""
        mock_doc = Mock()
        mock_app.ActiveDocument = mock_doc

        mock_obj = Mock()
        mock_shape = Mock()
        mock_shape.Volume = 50.0
        mock_shape.Area = 30.0
        mock_shape.BoundBox = Mock()
        mock_shape.BoundBox.XLength = 5.0
        mock_shape.BoundBox.YLength = 5.0
        mock_shape.BoundBox.ZLength = 5.0

        # Make sure all shape attributes are proper lists
        mock_shape.Faces = []
        mock_shape.Edges = []
        mock_shape.Vertexes = []

        mock_obj.Shape = mock_shape
        mock_doc.getObject.return_value = mock_obj

        result = self.analyzer.analyze_manufacturing_feasibility(
            "test_object",
            "3d_printing",
            "plastic_pla",
            {"layer_height": 0.2, "nozzle_diameter": 0.4},
        )

        assert result["status"] == "success"
        assert result["process"] == "3d_printing"
        assert "analysis" in result

        analysis = result["analysis"]
        assert analysis["process"] == "3d_printing"
        assert "overhangs" in analysis
        assert "print_time" in analysis

    @patch("freecad_ai_addon.agent.manufacturing_analyzer.App")
    def test_injection_molding_analysis(self, mock_app):
        """Test injection molding analysis."""
        mock_doc = Mock()
        mock_app.ActiveDocument = mock_doc

        mock_obj = Mock()
        mock_shape = Mock()
        mock_shape.Volume = 75.0
        mock_shape.Area = 40.0
        mock_shape.BoundBox = Mock()
        mock_shape.BoundBox.XLength = 8.0
        mock_shape.BoundBox.YLength = 8.0
        mock_shape.BoundBox.ZLength = 8.0

        # Make sure all shape attributes are proper lists
        mock_shape.Faces = []
        mock_shape.Edges = []
        mock_shape.Vertexes = []

        mock_obj.Shape = mock_shape
        mock_doc.getObject.return_value = mock_obj

        result = self.analyzer.analyze_manufacturing_feasibility(
            "test_object", "injection_molding", "plastic_abs"
        )

        assert result["status"] == "success"
        assert result["process"] == "injection_molding"
        assert "analysis" in result

        analysis = result["analysis"]
        assert analysis["process"] == "injection_molding"
        assert "mold_complexity" in analysis
        assert "cycle_time" in analysis

    def test_unknown_process_handling(self):
        """Test handling of unknown manufacturing processes."""
        result = self.analyzer.analyze_manufacturing_feasibility(
            "test_object", "unknown_process", "aluminum"
        )

        assert result["status"] == "failed"
        assert "Unknown process" in result["error"]
        assert "available_processes" in result

    def test_complexity_score_calculation(self):
        """Test complexity score calculation."""
        mock_shape = Mock()
        mock_shape.Volume = 100.0

        # Create proper lists instead of Mock objects
        mock_shape.Faces = [Mock() for _ in range(10)]
        mock_shape.Edges = [Mock() for _ in range(20)]
        mock_shape.Vertexes = [Mock() for _ in range(15)]

        complexity = self.analyzer._calculate_complexity_score(mock_shape)

        assert isinstance(complexity, float)
        assert 0 <= complexity <= 10.0


class TestIntegration:
    """Test integration between enhanced components."""

    def setup_method(self):
        """Set up integration test fixtures."""
        self.builder = ParametricModelBuilder()
        self.patterns = AdvancedSketchPatterns()
        self.analyzer = ManufacturingAnalyzer()

    def test_parametric_to_manufacturing_workflow(self):
        """Test workflow from parametric design to manufacturing analysis."""
        # This would test the complete workflow in a real scenario
        assert self.builder is not None
        assert self.patterns is not None
        assert self.analyzer is not None

    def test_design_pattern_to_sketch_pattern_integration(self):
        """Test integration between design patterns and sketch patterns."""
        # Test that design templates can utilize sketch patterns
        mounting_holes = self.patterns.create_mounting_holes(
            {"hole_type": "M6", "spacing": 25.0, "layout": "square"}
        )

        assert "geometry" in mounting_holes
        # This pattern could be used in a parametric template

    def test_manufacturing_feedback_to_design(self):
        """Test manufacturing feedback influencing design parameters."""
        # This would test how manufacturing analysis results
        # can be used to optimize parametric designs
        materials = list(self.analyzer.materials.keys())
        assert len(materials) > 0

        # Check that material constraints are available
        aluminum = self.analyzer.materials["aluminum"]
        min_wall = aluminum["min_wall_thickness"]
        assert min_wall > 0


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
