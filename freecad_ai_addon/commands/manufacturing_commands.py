"""
Manufacturing-related FreeCAD commands.
"""

try:
    import FreeCADGui as Gui
except Exception:  # Allow import outside FreeCAD
    Gui = None

from freecad_ai_addon.ui.manufacturing_advice_dialog import ManufacturingAdviceDialog
from freecad_ai_addon.utils.logging import get_logger

logger = get_logger("manufacturing_commands")


class ShowManufacturingAdviceCommand:
    """Open a dialog that shows manufacturing advice for the selected object."""

    def GetResources(self):
        return {
            "Pixmap": "ai_manufacturing_advice.svg",
            "MenuText": "Show Manufacturing Advice",
            "ToolTip": "Analyze manufacturability and show recommendations",
        }

    def IsActive(self):
        return True

    def Activated(self):
        try:
            object_name = self._get_selected_object_name() or "ActivePart"
            dialog = ManufacturingAdviceDialog(object_name=object_name, quantity=50)
            # Support both PySide2 (exec_) and PySide6 (exec)
            if hasattr(dialog, "exec"):
                dialog.exec()  # type: ignore[attr-defined]
            elif hasattr(dialog, "exec_"):
                dialog.exec_()  # type: ignore[attr-defined]
            else:
                # Fallback: show non-blocking if neither method exists
                if hasattr(dialog, "show"):
                    dialog.show()  # type: ignore[attr-defined]
        except Exception as e:
            logger.error("Failed to show manufacturing advice: %s", e)
            if Gui:
                Gui.SendMsgToActiveView("Failed to show manufacturing advice")

    def _get_selected_object_name(self):
        try:
            if Gui and hasattr(Gui, "Selection"):
                sel = Gui.Selection.getSelection()
                if sel:
                    return getattr(sel[0], "Name", None)
        except Exception:
            pass
        return None


if Gui and hasattr(Gui, "addCommand"):
    Gui.addCommand("AI_ShowManufacturingAdvice", ShowManufacturingAdviceCommand())
