"""
FreeCAD Integration Utilities

Utilities for integrating with FreeCAD's selection system and other features.
"""

import FreeCAD as App
import FreeCADGui as Gui
from typing import Callable, Optional

from freecad_ai_addon.utils.logging import get_logger

logger = get_logger('freecad_integration')


class SelectionObserver:
    """Observer for FreeCAD selection changes"""

    def __init__(self, callback: Callable[[dict], None]):
        """
        Initialize selection observer

        Args:
            callback: Function to call when selection changes
        """
        self.callback = callback
        self.is_active = False

    def addSelection(self, doc, obj, sub, pnt):
        """Called when object is added to selection"""
        try:
            selection_info = self._get_selection_info()
            self.callback(selection_info)
        except Exception as e:
            logger.error("Error in addSelection: %s", str(e))

    def removeSelection(self, doc, obj, sub):
        """Called when object is removed from selection"""
        try:
            selection_info = self._get_selection_info()
            self.callback(selection_info)
        except Exception as e:
            logger.error("Error in removeSelection: %s", str(e))

    def setSelection(self, doc):
        """Called when selection is cleared or set"""
        try:
            selection_info = self._get_selection_info()
            self.callback(selection_info)
        except Exception as e:
            logger.error("Error in setSelection: %s", str(e))

    def clearSelection(self, doc):
        """Called when selection is cleared"""
        try:
            selection_info = {'objects': [], 'count': 0}
            self.callback(selection_info)
        except Exception as e:
            logger.error("Error in clearSelection: %s", str(e))

    def _get_selection_info(self) -> dict:
        """Get current selection information"""
        try:
            selection = Gui.Selection.getSelection()
            selection_info = {
                'objects': [obj.Name for obj in selection],
                'count': len(selection),
                'types': [obj.TypeId for obj in selection],
            }

            # Add detailed info for each selected object
            details = []
            for obj in selection:
                obj_info = {
                    'name': obj.Name,
                    'label': getattr(obj, 'Label', ''),
                    'type': obj.TypeId,
                    'document': obj.Document.Name if obj.Document else '',
                }

                # Add geometry info if available
                if hasattr(obj, 'Shape'):
                    try:
                        shape = obj.Shape
                        obj_info.update({
                            'volume': getattr(shape, 'Volume', 0),
                            'area': getattr(shape, 'Area', 0),
                            'length': getattr(shape, 'Length', 0),
                        })
                    except Exception:
                        pass

                details.append(obj_info)

            selection_info['details'] = details
            return selection_info

        except Exception as e:
            logger.error("Error getting selection info: %s", str(e))
            return {'objects': [], 'count': 0, 'details': []}

    def start(self):
        """Start observing selection changes"""
        if not self.is_active:
            Gui.Selection.addObserver(self)
            self.is_active = True
            logger.info("Selection observer started")

    def stop(self):
        """Stop observing selection changes"""
        if self.is_active:
            Gui.Selection.removeObserver(self)
            self.is_active = False
            logger.info("Selection observer stopped")


# Global selection observer instance
_selection_observer: Optional[SelectionObserver] = None


def setup_selection_observer(callback: Callable[[dict], None]):
    """
    Set up global selection observer

    Args:
        callback: Function to call when selection changes
    """
    global _selection_observer

    # Stop existing observer if any
    if _selection_observer:
        _selection_observer.stop()

    # Create and start new observer
    _selection_observer = SelectionObserver(callback)
    _selection_observer.start()

    logger.info("Selection observer configured")


def stop_selection_observer():
    """Stop the global selection observer"""
    global _selection_observer

    if _selection_observer:
        _selection_observer.stop()
        _selection_observer = None
        logger.info("Selection observer stopped")


def get_current_selection() -> dict:
    """Get current selection information"""
    try:
        selection = Gui.Selection.getSelection()
        return {
            'objects': [obj.Name for obj in selection],
            'count': len(selection),
            'types': [obj.TypeId for obj in selection],
        }
    except Exception as e:
        logger.error("Error getting current selection: %s", str(e))
        return {'objects': [], 'count': 0, 'types': []}


def get_active_document_info() -> dict:
    """Get information about the active document"""
    try:
        doc = App.ActiveDocument
        if not doc:
            return {'name': None, 'objects': [], 'count': 0}

        objects = doc.Objects
        return {
            'name': doc.Name,
            'label': getattr(doc, 'Label', ''),
            'path': getattr(doc, 'FileName', ''),
            'objects': [obj.Name for obj in objects],
            'count': len(objects),
            'types': list(set(obj.TypeId for obj in objects)),
        }

    except Exception as e:
        logger.error("Error getting document info: %s", str(e))
        return {'name': None, 'objects': [], 'count': 0}


def get_active_workbench() -> str:
    """Get the name of the active workbench"""
    try:
        return Gui.activeWorkbench().name()
    except Exception as e:
        logger.error("Error getting active workbench: %s", str(e))
        return "Unknown"


def get_freecad_context() -> dict:
    """Get comprehensive FreeCAD context information"""
    return {
        'document': get_active_document_info(),
        'selection': get_current_selection(),
        'workbench': get_active_workbench(),
        'version': App.Version(),
    }
