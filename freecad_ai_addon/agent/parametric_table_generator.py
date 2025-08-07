"""
Parametric Table Generator for FreeCAD AI Addon
Generates parameter tables for parametric design assistant.
"""


class ParametricTableGenerator:
    def __init__(self):
        """
        Initialize the ParametricTableGenerator.
        """
        # No initialization needed currently

    def generate_table(self, model) -> dict:
        """
        Generate a parameter table from a FreeCAD model.

        Args:
            model: A FreeCAD document object or feature.

        Returns:
            dict: A dictionary mapping parameter names to their values.
        """
        param_table = {}
        # Attempt to extract parameters from the model's properties
        if hasattr(model, "PropertiesList"):
            for prop in model.PropertiesList:
                try:
                    param_table[prop] = getattr(model, prop)
                except AttributeError:
                    param_table[prop] = None
        # If model has 'Parameters' attribute (custom), include those
        if hasattr(model, "Parameters") and isinstance(model.Parameters, dict):
            param_table.update(model.Parameters)
        return param_table
