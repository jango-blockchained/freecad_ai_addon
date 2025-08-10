"""
Advanced features for the FreeCAD AI Addon.

This package exposes higher-level assistants such as the ManufacturingAdvisor.
"""

# Re-export key classes for convenient imports
from .manufacturing_advisor import (
    ManufacturingAdvisor,
    ManufacturingProcess,
    MaterialCategory,
    CostCategory,
    MaterialProperties,
    ProcessRecommendation,
    CostEstimate,
    ManufacturingAdvice,
)

__all__ = [
    "ManufacturingAdvisor",
    "ManufacturingProcess",
    "MaterialCategory",
    "CostCategory",
    "MaterialProperties",
    "ProcessRecommendation",
    "CostEstimate",
    "ManufacturingAdvice",
]
