import pytest
from freecad_ai_addon.advanced_features.feature_recognition import (
    FeatureRecognitionAI,
    FreeCADFeatureDetector,
)

FREECAD_AVAILABLE = False
try:  # pragma: no cover - environment dependent
    import FreeCAD  # type: ignore  # noqa: F401

    FREECAD_AVAILABLE = True
except Exception:  # pragma: no cover
    pass

pytestmark = pytest.mark.skipif(
    not FREECAD_AVAILABLE, reason="FreeCAD not available in test environment"
)


def test_freecad_detector_auto_registration():
    engine = FeatureRecognitionAI()
    if FREECAD_AVAILABLE:
        assert any(name == "freecad_basic" for name in engine.list_detectors())


def test_freecad_detector_manual():
    engine = FeatureRecognitionAI(detectors=[])  # start empty
    engine.register_detector(FreeCADFeatureDetector())
    assert "freecad_basic" in engine.list_detectors()
