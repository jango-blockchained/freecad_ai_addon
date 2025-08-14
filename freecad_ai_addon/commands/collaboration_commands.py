"""FreeCAD command wrappers for collaboration MVP features.

Currently provides simple commands for adding and listing annotations.
Commands are intentionally minimal to remain testable in headless mode.
"""
from __future__ import annotations

try:  # FreeCAD GUI optional
    import FreeCADGui as Gui  # type: ignore
except ImportError:  # pragma: no cover
    Gui = None  # type: ignore

from freecad_ai_addon.collaboration import DesignReviewManager
from freecad_ai_addon.utils.logging import get_logger

logger = get_logger("commands.collaboration")


_review_manager = DesignReviewManager()


class AI_AddAnnotationCommand:
    def GetResources(self):  # pragma: no cover - GUI contract
        return {
            "Pixmap": "ai_add_annotation.svg",
            "MenuText": "Add Design Annotation",
            "ToolTip": "Create a review annotation for the active design.",
        }

    def IsActive(self):  # Activation logic could check for a document
        return True

    def Activated(self):  # pragma: no cover - GUI path
        try:
            doc_id = "active_document"  # NOTE: integrate with FreeCAD active doc in future iteration
            ann = _review_manager.create_annotation(
                document_id=doc_id,
                author="user",
                message="Sample annotation (MVP)",
            )
            logger.info("Annotation added: %s", ann.id)
        except Exception as e:  # noqa: BLE001
            logger.error("Failed to add annotation: %s", e)


class AI_ListAnnotationsCommand:
    def GetResources(self):  # pragma: no cover
        return {
            "Pixmap": "ai_list_annotations.svg",
            "MenuText": "List Design Annotations",
            "ToolTip": "Show annotation summary in console/log.",
        }

    def IsActive(self):
        return True

    def Activated(self):  # pragma: no cover
        try:
            doc_id = "active_document"
            anns = _review_manager.list_annotations(doc_id)
            logger.info("%d annotations for %s", len(anns), doc_id)
            for a in anns:
                logger.info(" - [%s] %s", a.category, a.message[:80])
        except Exception as e:  # noqa: BLE001
            logger.error("Failed to list annotations: %s", e)


if Gui and hasattr(Gui, "addCommand"):  # pragma: no cover
    Gui.addCommand("AI_AddAnnotation", AI_AddAnnotationCommand())
    Gui.addCommand("AI_ListAnnotations", AI_ListAnnotationsCommand())

__all__ = ["AI_AddAnnotationCommand", "AI_ListAnnotationsCommand"]
