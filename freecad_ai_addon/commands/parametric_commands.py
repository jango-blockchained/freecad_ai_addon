"""Parametric design related FreeCAD commands.

Provides a lightweight command to generate a parametric design script
using ``ParametricDesignAssistant`` and (optionally) show or copy it.

The initial implementation avoids heavy GUI dependencies – if FreeCAD GUI
is available a simple message dialog is used; otherwise the script is
printed to the console/log so tests in headless mode can still validate
behavior.
"""
from __future__ import annotations

try:  # FreeCAD GUI optional
    import FreeCADGui as Gui  # type: ignore
except ImportError:  # pragma: no cover - absent in tests
    Gui = None  # type: ignore

from freecad_ai_addon.advanced_features import (
    ParametricDesignAssistant,
    DesignType,
)
from freecad_ai_addon.utils.logging import get_logger

logger = get_logger("parametric_commands")


class GenerateParametricDesignCommand:
    """Generate a parametric design script for a chosen template.

    Current MVP: always generates a bearing mount script; future UI will
    allow selection + parameter editing.
    """

    def GetResources(self):  # FreeCAD command contract
        return {
            "Pixmap": "ai_parametric_design.svg",
            "MenuText": "Generate Parametric Design",
            "ToolTip": "Create parametric design script (bearing mount template)",
        }

    def IsActive(self):  # Always available for now
        return True

    # Helper to show a simple dialog if GUI exists
    def _show_message(self, text: str):  # pragma: no cover - GUI branch
        if not (Gui and hasattr(Gui, "showMainWindow")):
            return
        try:
            from PySide2.QtWidgets import QMessageBox  # type: ignore

            QMessageBox.information(None, "Parametric Design Script", text[:5000])
        except ImportError:
            logger.debug("PySide2 not available for message dialog")

    def Activated(self):  # Entry point when user clicks command
        try:
            assistant = ParametricDesignAssistant()
            design = assistant.suggest_design_parameters(
                DesignType.BEARING_MOUNT, {"bearing_diameter": 25.0}
            )
            script = assistant.generate_freecad_script(design)
            logger.info("Generated parametric design script (%d chars)", len(script))
            # If GUI present show snippet, else print to console for headless usage
            if Gui:
                self._show_message(script[:1200])
            else:  # makes behavior testable without FreeCAD
                print(script)
        except Exception as e:  # noqa: BLE001 broad for robustness in FreeCAD cmd
            logger.error("Failed to generate parametric design: %s", e)
            if Gui:
                try:
                    from PySide2.QtWidgets import QMessageBox  # type: ignore

                    QMessageBox.critical(
                        None,
                        "Parametric Design Error",
                        f"Failed to generate design: {e}",
                    )
                except ImportError:
                    pass


if Gui and hasattr(Gui, "addCommand"):
    Gui.addCommand("AI_GenerateParametricDesign", GenerateParametricDesignCommand())

__all__ = ["GenerateParametricDesignCommand"]
