import json
from freecad_ai_addon.advanced_features.feature_recognition import (
    FeatureRecognitionAI,
    FeatureDetector,
    FeatureType,
    GeometricFeature,
)
import time


class DummyDetector(FeatureDetector):
    name = "dummy"
    provides = {FeatureType.CHAMFER}

    def detect(self, obj):  # simple deterministic
        return [
            GeometricFeature(
                feature_type=FeatureType.CHAMFER,
                location=(0.0, 0.0, 0.0),
                dimensions={"size": 1.0},
                confidence=0.5,
                description="Dummy chamfer",
            )
        ]


def test_detector_registration_and_listing():
    engine = FeatureRecognitionAI(detectors=[])
    assert engine.list_detectors() == []
    engine.register_detector(DummyDetector())
    assert "dummy" in engine.list_detectors()
    # Unregister path
    removed = engine.unregister_detector("dummy")
    assert removed is True
    assert "dummy" not in engine.list_detectors()


def test_mock_analysis_returns_features_and_confidence():
    engine = FeatureRecognitionAI()  # default mock detectors
    result = engine.analyze_object("example_part")
    assert result.success is True
    assert result.features_found, "Expected at least one mock feature"
    assert 0.0 < result.confidence_score <= 1.0


def test_json_serialization_round_trip():
    engine = FeatureRecognitionAI()
    result = engine.analyze_object("demo")
    data = result.to_dict()
    # ensure all features serialized to plain dicts
    assert all(isinstance(f, dict) for f in data["features_found"])
    # JSON dump should succeed
    json_str = json.dumps(data)
    assert isinstance(json_str, str)


class FailingDetector(FeatureDetector):
    name = "failing"
    provides = {FeatureType.BOSS}

    def detect(self, obj):
        raise RuntimeError("boom")


def test_failing_detector_isolated():
    engine = FeatureRecognitionAI(detectors=[FailingDetector()])
    result = engine.analyze_object("x")
    # Should succeed (no features) but warning recorded
    assert result.success is True
    assert result.features_found == []
    assert any("failing" in w for w in result.warnings)


def test_cache_reuse_and_invalidation():
    engine = FeatureRecognitionAI()  # includes mock detectors
    first = engine.analyze_object("cached_part")
    # Second call should return cached object reference (current design choice)
    t0 = time.time()
    second = engine.analyze_object("cached_part")
    dt = time.time() - t0
    assert first is second
    assert dt < 0.05  # heuristic: fast path
    # Invalidate and ensure new object
    engine.invalidate_cache("cached_part")
    third = engine.analyze_object("cached_part")
    assert third is not first


def test_dynamic_detector_addition_updates_results():
    class TempDetector(FeatureDetector):
        name = "temp_feat"
        provides = {FeatureType.BOSS}

        def detect(self, obj):
            return [
                GeometricFeature(
                    feature_type=FeatureType.BOSS,
                    location=(0, 0, 0),
                    dimensions={"height": 1.0},
                    confidence=0.6,
                    description="Temp boss",
                )
            ]

    engine = FeatureRecognitionAI()
    base = engine.analyze_object("dyn_obj")
    kinds_before = {f.feature_type for f in base.features_found}
    engine.register_detector(TempDetector())
    updated = engine.analyze_object("dyn_obj", use_cache=False)
    kinds_after = {f.feature_type for f in updated.features_found}
    assert FeatureType.BOSS in kinds_after - kinds_before


def test_analysis_history_records_runs():
    engine = FeatureRecognitionAI()
    engine.analyze_object("h1")
    engine.analyze_object("h2")
    assert len(engine.analysis_history) >= 2
