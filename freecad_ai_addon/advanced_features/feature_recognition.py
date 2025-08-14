"""Feature Recognition Module (Refactored).

This refactored module provides an extensible framework for geometric feature
recognition inside (or outside) FreeCAD. It is intentionally light‑weight so it
can run in three modes:

1. Full FreeCAD mode (FreeCAD Python environment available)
2. Headless/mock mode (no FreeCAD – returns deterministic mock data)
3. Hybrid mode where external code supplies already loaded FreeCAD objects

Key improvements over the previous prototype implementation:
* Pluggable detector architecture (register/unregister custom detectors)
* Clear, typed data models with helpers for (de)serialization
* Graceful degradation when FreeCAD is missing
* Separation of orchestration (FeatureRecognitionAI) from individual detectors
* Simple performance timing & consolidated logging

Public entry points maintained for backward compatibility:
* FeatureType (Enum)
* GeometricFeature (dataclass)
* AnalysisResult (dataclass)
* FeatureRecognitionAI (main orchestrator)
* demo_feature_recognition() (manual smoke test)

Adding a new detector:
    class MyDetector(FeatureDetector):
        name = "my_detector"
        provides = {FeatureType.BOSS}
        def detect(self, obj) -> list[GeometricFeature]:
            # implement
            return []
    engine.register_detector(MyDetector())

Detectors should NEVER raise; they must catch and log internally so one faulty
detector does not abort the entire analysis.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from enum import Enum
from time import perf_counter
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple
import logging

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Optional FreeCAD import (soft dependency)
# ---------------------------------------------------------------------------
try:  # pragma: no cover - import path differs in CI vs user env
    import FreeCAD as App  # type: ignore

    FREECAD_AVAILABLE = True
except ImportError:  # pragma: no cover - FreeCAD not installed
    FREECAD_AVAILABLE = False
    logger.info("FreeCAD not available; feature recognition will run in mock mode.")


# ---------------------------------------------------------------------------
# Core Data Models
# ---------------------------------------------------------------------------
class FeatureType(Enum):
    """Types of geometric features that can be recognized."""

    HOLE = "hole"
    FILLET = "fillet"
    CHAMFER = "chamfer"
    BOSS = "boss"
    CUT = "cut"
    POCKET = "pocket"
    RIB = "rib"
    GROOVE = "groove"
    THREAD = "thread"
    COUNTERBORE = "counterbore"
    COUNTERSINK = "countersink"
    KEYWAY = "keyway"
    TAP = "tap"
    DRAFT = "draft"


@dataclass(slots=True)
class GeometricFeature:
    """Represents a recognized geometric feature."""

    feature_type: FeatureType
    location: Tuple[float, float, float]
    dimensions: Dict[str, float]
    confidence: float
    description: str

    def to_dict(self) -> Dict[str, Any]:  # convenience for JSON serialization
        d = asdict(self)
        d["feature_type"] = self.feature_type.value
        return d


@dataclass(slots=True)
class AnalysisResult:
    """Results from feature recognition analysis."""

    success: bool
    features_found: List[GeometricFeature]
    analysis_time: float
    confidence_score: float
    recommendations: List[str]
    warnings: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "features_found": [f.to_dict() for f in self.features_found],
            "analysis_time": self.analysis_time,
            "confidence_score": self.confidence_score,
            "recommendations": list(self.recommendations),
            "warnings": list(self.warnings),
        }


# ---------------------------------------------------------------------------
# Detector Base Class & Built‑in Detectors
# ---------------------------------------------------------------------------
class FeatureDetector:
    """Base class for all feature detectors.

    Subclasses must set:
        name: unique short identifier
        provides: set of FeatureType values the detector yields
    """

    name: str = "base"
    provides: Set[FeatureType] = set()

    def detect(
        self, obj: Any
    ) -> List[GeometricFeature]:  # pragma: no cover - overridden
        raise NotImplementedError

    # Safe wrapper invoked by orchestrator
    def run(self, obj: Any) -> Tuple[List[GeometricFeature], Optional[str]]:
        try:
            feats = self.detect(obj)
            return feats, None
        except (RuntimeError, ValueError, AttributeError) as e:
            logger.exception("Detector '%s' failed", self.name)
            return [], f"Detector {self.name} failed: {e}"


class MockHoleDetector(FeatureDetector):
    name = "mock_hole"
    provides = {FeatureType.HOLE}

    def detect(self, obj: Any) -> List[GeometricFeature]:  # pragma: no cover - trivial
        # In FreeCAD mode, you would inspect obj.Shape, faces, etc.
        return [
            GeometricFeature(
                feature_type=FeatureType.HOLE,
                location=(10.0, 20.0, 0.0),
                dimensions={"diameter": 8.0, "depth": 15.0},
                confidence=0.92,
                description="Through hole, 8mm diameter",
            )
        ]


class MockFilletDetector(FeatureDetector):
    name = "mock_fillet"
    provides = {FeatureType.FILLET}

    def detect(self, obj: Any) -> List[GeometricFeature]:  # pragma: no cover - trivial
        return [
            GeometricFeature(
                feature_type=FeatureType.FILLET,
                location=(5.0, 5.0, 0.0),
                dimensions={"radius": 2.0},
                confidence=0.88,
                description="Edge fillet, 2mm radius",
            )
        ]


class FreeCADFeatureDetector(FeatureDetector):
    """Detector stub that inspects a real FreeCAD object (if available).

    This is a placeholder showing where real topology/shape analysis would be
    implemented. It only runs when FreeCAD is present; otherwise it yields
    no features. Extend this to use obj.Shape, iterate over faces/edges, etc.
    """

    name = "freecad_basic"
    provides = {FeatureType.HOLE, FeatureType.FILLET}

    def detect(
        self, obj: Any
    ) -> List[GeometricFeature]:  # pragma: no cover - needs FreeCAD
        if not FREECAD_AVAILABLE:
            return []
        feats: List[GeometricFeature] = []
        shape = getattr(obj, "Shape", None)
        if shape is None:
            return feats
        # Extremely naive placeholder heuristics:
        # Count circular edges as potential holes (mock) and smooth edges as fillets.
        try:
            for edge in getattr(shape, "Edges", []):
                curve = getattr(edge, "Curve", None)
                if curve and curve.__class__.__name__.lower().startswith("circle"):
                    center = getattr(curve, "Center", None)
                    radius = getattr(curve, "Radius", 0.0)
                    loc = (
                        getattr(center, "x", 0.0),
                        getattr(center, "y", 0.0),
                        getattr(center, "z", 0.0),
                    )
                    feats.append(
                        GeometricFeature(
                            feature_type=FeatureType.HOLE,
                            location=loc,
                            dimensions={"diameter": radius * 2},
                            confidence=0.4,
                            description="Potential circular hole (heuristic)",
                        )
                    )
            # Placeholder fillet heuristic: if there are more than 10 edges, assume fillets exist
            if len(getattr(shape, "Edges", [])) > 10:
                feats.append(
                    GeometricFeature(
                        feature_type=FeatureType.FILLET,
                        location=(0.0, 0.0, 0.0),
                        dimensions={"radius": 1.0},
                        confidence=0.3,
                        description="Heuristic fillet indication",
                    )
                )
        except Exception:  # pragma: no cover - defensive around FreeCAD internals
            logger.exception("FreeCADFeatureDetector failed during shape inspection")
        return feats


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------
class FeatureRecognitionAI:
    """AI‑powered feature recognition engine.

    The engine aggregates multiple detectors and produces a consolidated
    analysis. It records history for optional later inspection.
    """

    def __init__(self, detectors: Optional[Sequence[FeatureDetector]] = None):
        self._detectors: Dict[str, FeatureDetector] = {}
        self.feature_database = self._load_feature_database()
        self.analysis_history: List[AnalysisResult] = []
        # Simple in-memory cache: key -> AnalysisResult (no persistence)
        self._cache: Dict[str, AnalysisResult] = {}
        # Register default detectors
        if detectors is None:
            detectors = [MockHoleDetector(), MockFilletDetector()]
            if FREECAD_AVAILABLE:  # add FreeCAD stub detector automatically
                detectors.append(FreeCADFeatureDetector())
        for d in detectors:
            self.register_detector(d)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def register_detector(
        self, detector: FeatureDetector, overwrite: bool = True
    ) -> None:
        if not overwrite and detector.name in self._detectors:
            raise ValueError(f"Detector '{detector.name}' already registered")
        self._detectors[detector.name] = detector
        # Invalidate cache because detector set changed
        self._cache.clear()

    def unregister_detector(self, name: str) -> bool:
        removed = self._detectors.pop(name, None) is not None
        if removed:
            self._cache.clear()
        return removed

    def list_detectors(self) -> List[str]:
        return sorted(self._detectors.keys())

    def analyze_object(
        self, object_or_name: Any, use_cache: bool = True
    ) -> AnalysisResult:
        """Analyze a FreeCAD object (or name) for geometric features.

        Accepts either a FreeCAD object instance (with expected shape attrs) or
        a string in which case we'll try to resolve it from the active
        FreeCAD document if available. In mock mode, the string variant just
        triggers deterministic sample data.
        """

        start = perf_counter()
        warnings: List[str] = []

        if isinstance(object_or_name, str):
            obj_name = object_or_name
            if use_cache and obj_name in self._cache:
                cached = self._cache[obj_name]
                # Return shallow copy with updated history append (avoid mutating original)
                self.analysis_history.append(cached)
                return cached
            obj = self._resolve_object_by_name(obj_name)
            if obj is None and not FREECAD_AVAILABLE:
                # We'll proceed with a mock placeholder object token
                obj = {"name": obj_name}
            elif obj is None:  # FreeCAD expected but object missing
                msg = f"Object '{obj_name}' not found in active document"
                logger.error(msg)
                return AnalysisResult(
                    success=False,
                    features_found=[],
                    analysis_time=0.0,
                    confidence_score=0.0,
                    recommendations=[f"Analysis failed: {msg}"],
                    warnings=[],
                )
        else:
            obj = object_or_name

        logger.info("Starting feature analysis with %d detectors", len(self._detectors))
        all_features: List[GeometricFeature] = []

        for det in self._detectors.values():
            feats, warn = det.run(obj)
            if warn:
                warnings.append(warn)
            all_features.extend(feats)

        # Deduplicate (by type + location + description) – simple heuristic
        unique: Dict[Tuple[str, Tuple[float, float, float], str], GeometricFeature] = {}
        for f in all_features:
            key = (f.feature_type.value, f.location, f.description)
            if key not in unique or unique[key].confidence < f.confidence:
                unique[key] = f
        deduped = list(unique.values())

        recommendations = self._generate_recommendations(deduped)
        confidence = self._aggregate_confidence(deduped)
        elapsed = perf_counter() - start

        result = AnalysisResult(
            success=True,
            features_found=deduped,
            analysis_time=elapsed,
            confidence_score=confidence,
            recommendations=recommendations,
            warnings=warnings,
        )

        self.analysis_history.append(result)
        if isinstance(object_or_name, str) and use_cache:
            self._cache[object_or_name] = result
        return result

    # ------------------------------------------------------------------
    # Cache Management
    # ------------------------------------------------------------------
    def invalidate_cache(self, key: Optional[str] = None) -> None:
        """Invalidate cached analysis results.

        Args:
            key: object name to invalidate; if None, clear entire cache
        """
        if key:
            self._cache.pop(key, None)
        else:
            self._cache.clear()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _resolve_object_by_name(self, name: str) -> Any:
        if not FREECAD_AVAILABLE:
            return None
        try:  # pragma: no cover - depends on FreeCAD runtime
            doc = App.activeDocument()
            if not doc:
                logger.warning("No active FreeCAD document.")
                return None
            return doc.getObject(name)
        except (AttributeError, RuntimeError):  # pragma: no cover - defensive
            logger.exception("Failed to resolve FreeCAD object '%s'", name)
            return None

    def _aggregate_confidence(self, features: Sequence[GeometricFeature]) -> float:
        if not features:
            return 0.0
        return sum(f.confidence for f in features) / len(features)

    def _generate_recommendations(
        self, features: Sequence[GeometricFeature]
    ) -> List[str]:
        recs: List[str] = []
        for feature in features:
            if feature.feature_type == FeatureType.HOLE:
                recs.append("Consider standard drill sizes for holes")
            elif feature.feature_type == FeatureType.FILLET:
                recs.append("Fillets can improve stress distribution")
        if not recs:
            recs.append("No specific recommendations – consider adding more detectors.")
        return recs

    def _load_feature_database(self) -> Dict[str, Any]:  # pragma: no cover - trivial
        return {
            "hole_patterns": {
                "circular": {"min_diameter": 1.0, "max_diameter": 100.0},
                "counterbore": {"depth_ratio": 0.3},
                "countersink": {"angle_range": [60, 120]},
            },
            "fillet_patterns": {
                "edge_fillet": {"min_radius": 0.5, "max_radius": 50.0},
                "face_fillet": {"typical_ratios": [0.1, 0.2, 0.5]},
            },
        }


# ---------------------------------------------------------------------------
# Demo / Manual Smoke Test
# ---------------------------------------------------------------------------
def demo_feature_recognition() -> None:
    print("Feature Recognition AI Demo (Refactored)")
    print("=" * 45)
    engine = FeatureRecognitionAI()
    result = engine.analyze_object("demo_object")
    print(f"Success: {result.success}")
    print(f"Detectors: {engine.list_detectors()}")
    print(
        f"Features: {len(result.features_found)} | Confidence: {result.confidence_score:.2f}"
    )
    for i, feat in enumerate(result.features_found, 1):
        print(
            f"  {i}. {feat.feature_type.value.title()} @ {feat.location} -> {feat.description} (c={feat.confidence:.2f})"
        )
    print("Recommendations:")
    for r in result.recommendations:
        print(f"  - {r}")
    if result.warnings:
        print("Warnings:")
        for w in result.warnings:
            print(f"  * {w}")


__all__ = [
    "FeatureType",
    "GeometricFeature",
    "AnalysisResult",
    "FeatureDetector",
    "FeatureRecognitionAI",
    "demo_feature_recognition",
]


if __name__ == "__main__":  # pragma: no cover
    demo_feature_recognition()
