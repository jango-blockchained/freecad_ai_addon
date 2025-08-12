"""Service layer utilities for Feature Recognition.

Provides convenience wrappers that use FeatureRecognitionAI and deliver
JSON-serializable payloads for UI layers, web APIs, or agent communication.
"""
from __future__ import annotations

from typing import Any, Dict
import json
import logging

from .feature_recognition import FeatureRecognitionAI, AnalysisResult

logger = logging.getLogger(__name__)


class FeatureRecognitionService:
    """High-level service facade.

    Designed so GUI / Agent code can call a single method and receive a
    JSON-friendly dict (or JSON string) without depending on dataclasses.
    """

    def __init__(self, engine: FeatureRecognitionAI | None = None):
        self.engine = engine or FeatureRecognitionAI()

    def analyze_to_dict(self, object_or_name: Any) -> Dict[str, Any]:
        result = self.engine.analyze_object(object_or_name)
        return result.to_dict()

    def analyze_to_json(self, object_or_name: Any, **json_kwargs) -> str:
        data = self.analyze_to_dict(object_or_name)
        return json.dumps(data, **json_kwargs)

    def last_result(self) -> AnalysisResult | None:
        if not self.engine.analysis_history:
            return None
        return self.engine.analysis_history[-1]


__all__ = ["FeatureRecognitionService"]
