"""Design template sharing utilities.

Wraps existing parametric design assistant functionality to make export
of template parameter presets straightforward.
"""
from __future__ import annotations

from pathlib import Path
import json
from typing import Dict, Any

from freecad_ai_addon.advanced_features import ParametricDesignAssistant, DesignType
from freecad_ai_addon.utils.logging import get_logger

logger = get_logger("collaboration.template_sharing")


class TemplateSharingManager:
    def __init__(self):
        self.assistant = ParametricDesignAssistant()

    def export_template(
        self,
        design_type: DesignType,
        params: Dict[str, Any] | None = None,
        out_file: str | Path | None = None,
    ) -> Path:
        params = params or {}
        design = self.assistant.suggest_design_parameters(design_type, params)
        # Convert parameters (which may be Parameter dataclasses) into primitives
        param_export = {}
        for name, param in design.parameters.items():  # type: ignore[union-attr]
            try:
                # ParametricDesignAssistant.ParametricDesign uses Parameter objects with value attribute
                value = getattr(param, "value", param)
                default = getattr(param, "default", None)
                desc = getattr(param, "description", "")
                param_export[name] = {
                    "value": value,
                    **({"default": default} if default is not None else {}),
                    **({"description": desc} if desc else {}),
                }
            except Exception:  # noqa: BLE001
                param_export[name] = str(param)
        data = {
            "design_type": design_type.name,
            "parameters": param_export,
            "metadata": {
                "generated_by": "TemplateSharingManager",
            },
        }
        if out_file is None:
            out_file = Path.cwd() / f"template_{design_type.name.lower()}.json"
        else:
            out_file = Path(out_file)
        out_file.write_text(json.dumps(data, indent=2))
        logger.debug("Exported template %s -> %s", design_type.name, out_file)
        return out_file


__all__ = ["TemplateSharingManager"]
