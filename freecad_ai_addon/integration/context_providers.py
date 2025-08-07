"""
FreeCAD Context Provider

Extracts and provides contextual information from FreeCAD's current state,
including document structure, selected objects, sketches, and workspace information.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass

try:
    import FreeCAD as App
    import FreeCADGui as Gui

    FREECAD_AVAILABLE = True
except ImportError:
    # For testing without FreeCAD
    FREECAD_AVAILABLE = False
    App = None
    Gui = None

from freecad_ai_addon.utils.logging import get_logger

logger = get_logger("context_provider")


@dataclass
class ObjectInfo:
    """Information about a FreeCAD object"""

    name: str
    label: str
    type_id: str
    properties: Dict[str, Any]
    placement: Optional[Dict[str, Any]] = None
    shape_info: Optional[Dict[str, Any]] = None


@dataclass
class DocumentInfo:
    """Information about a FreeCAD document"""

    name: str
    file_path: Optional[str]
    objects: List[ObjectInfo]
    selected_objects: List[str]
    visible_objects: List[str]


@dataclass
class WorkbenchInfo:
    """Information about the current workbench"""

    name: str
    active_tool: Optional[str]
    available_commands: List[str]


@dataclass
class FreeCADContext:
    """Complete FreeCAD context information"""

    active_document: Optional[DocumentInfo]
    all_documents: List[DocumentInfo]
    workbench: Optional[WorkbenchInfo]
    selection: List[ObjectInfo]
    view_info: Dict[str, Any]
    preferences: Dict[str, Any]


class FreeCADContextProvider:
    """
    Provides contextual information about the current FreeCAD state
    for AI assistant operations.
    """

    def __init__(self):
        """Initialize the context provider"""
        self.last_context: Optional[FreeCADContext] = None

        if not FREECAD_AVAILABLE:
            logger.warning("FreeCAD not available - running in mock mode")

    def get_complete_context(self) -> FreeCADContext:
        """
        Get complete FreeCAD context information.

        Returns:
            Complete context information
        """
        if not FREECAD_AVAILABLE:
            return self._get_mock_context()

        try:
            context = FreeCADContext(
                active_document=self._get_active_document_info(),
                all_documents=self._get_all_documents_info(),
                workbench=self._get_workbench_info(),
                selection=self._get_selection_info(),
                view_info=self._get_view_info(),
                preferences=self._get_preferences_info(),
            )

            self.last_context = context
            return context

        except Exception as e:
            logger.error("Failed to get FreeCAD context: %s", str(e))
            raise

    def get_selection_context(self) -> Dict[str, Any]:
        """
        Get context information about currently selected objects.

        Returns:
            Selection context information
        """
        if not FREECAD_AVAILABLE:
            return {"objects": [], "count": 0}

        try:
            selection = self._get_selection_info()

            context = {
                "count": len(selection),
                "objects": [
                    {
                        "name": obj.name,
                        "label": obj.label,
                        "type": obj.type_id,
                        "properties": obj.properties,
                        "shape_info": obj.shape_info,
                    }
                    for obj in selection
                ],
            }

            return context

        except Exception as e:
            logger.error("Failed to get selection context: %s", str(e))
            return {"objects": [], "count": 0}

    def get_document_summary(self, doc_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get a summary of document contents.

        Args:
            doc_name: Name of document (uses active if None)

        Returns:
            Document summary
        """
        if not FREECAD_AVAILABLE:
            return {"name": "mock_document", "object_count": 0, "objects": []}

        try:
            if doc_name is None:
                doc_info = self._get_active_document_info()
            else:
                doc_info = self._get_document_info_by_name(doc_name)

            if not doc_info:
                return {"error": "Document not found"}

            # Group objects by type
            object_types: Dict[str, int] = {}
            for obj in doc_info.objects:
                obj_type = obj.type_id
                object_types[obj_type] = object_types.get(obj_type, 0) + 1

            return {
                "name": doc_info.name,
                "file_path": doc_info.file_path,
                "object_count": len(doc_info.objects),
                "object_types": object_types,
                "selected_count": len(doc_info.selected_objects),
                "visible_count": len(doc_info.visible_objects),
                "objects": [
                    {"name": obj.name, "label": obj.label, "type": obj.type_id}
                    for obj in doc_info.objects
                ],
            }

        except Exception as e:
            logger.error("Failed to get document summary: %s", str(e))
            return {"error": str(e)}

    def get_geometric_analysis(
        self, object_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get geometric analysis of objects.

        Args:
            object_names: List of object names (uses selection if None)

        Returns:
            Geometric analysis
        """
        if not FREECAD_AVAILABLE:
            return {"objects": [], "total_volume": 0, "total_area": 0}

        try:
            if object_names is None:
                # Use current selection
                selection = Gui.Selection.getSelection()
                objects = selection
            else:
                # Get objects by name from active document
                doc = App.ActiveDocument
                if not doc:
                    return {"error": "No active document"}

                objects = []
                for name in object_names:
                    obj = doc.getObject(name)
                    if obj:
                        objects.append(obj)

            analysis = {
                "objects": [],
                "total_volume": 0.0,
                "total_area": 0.0,
                "bounding_box": None,
            }

            all_bbox_points = []

            for obj in objects:
                obj_analysis = self._analyze_object_geometry(obj)
                analysis["objects"].append(obj_analysis)

                if obj_analysis.get("volume"):
                    analysis["total_volume"] += obj_analysis["volume"]
                if obj_analysis.get("area"):
                    analysis["total_area"] += obj_analysis["area"]

                if obj_analysis.get("bounding_box"):
                    bbox = obj_analysis["bounding_box"]
                    all_bbox_points.extend(
                        [
                            (bbox["x_min"], bbox["y_min"], bbox["z_min"]),
                            (bbox["x_max"], bbox["y_max"], bbox["z_max"]),
                        ]
                    )

            # Calculate combined bounding box
            if all_bbox_points:
                x_coords = [p[0] for p in all_bbox_points]
                y_coords = [p[1] for p in all_bbox_points]
                z_coords = [p[2] for p in all_bbox_points]

                analysis["bounding_box"] = {
                    "x_min": min(x_coords),
                    "x_max": max(x_coords),
                    "y_min": min(y_coords),
                    "y_max": max(y_coords),
                    "z_min": min(z_coords),
                    "z_max": max(z_coords),
                    "dimensions": {
                        "length": max(x_coords) - min(x_coords),
                        "width": max(y_coords) - min(y_coords),
                        "height": max(z_coords) - min(z_coords),
                    },
                }

            return analysis

        except Exception as e:
            logger.error("Failed to get geometric analysis: %s", str(e))
            return {"error": str(e)}

    def get_sketch_context(self, sketch_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get context information about a sketch.

        Args:
            sketch_name: Name of sketch (uses selected sketch if None)

        Returns:
            Sketch context information
        """
        if not FREECAD_AVAILABLE:
            return {"constraints": [], "geometry": [], "fully_constrained": False}

        try:
            # Find sketch object
            sketch = None
            if sketch_name:
                doc = App.ActiveDocument
                if doc:
                    sketch = doc.getObject(sketch_name)
            else:
                # Look for selected sketch
                selection = Gui.Selection.getSelection()
                for obj in selection:
                    if hasattr(obj, "TypeId") and "Sketch" in obj.TypeId:
                        sketch = obj
                        break

            if not sketch:
                return {"error": "No sketch found"}

            context = {
                "name": sketch.Name,
                "label": sketch.Label,
                "constraint_count": len(sketch.Constraints),
                "geometry_count": len(sketch.Geometry),
                "constraints": [],
                "geometry": [],
                "fully_constrained": False,
            }

            # Get constraint information
            for i, constraint in enumerate(sketch.Constraints):
                constraint_info = {
                    "index": i,
                    "type": constraint.Type,
                    "name": (
                        constraint.Name
                        if hasattr(constraint, "Name")
                        else f"Constraint{i}"
                    ),
                }

                if hasattr(constraint, "Value"):
                    constraint_info["value"] = constraint.Value

                context["constraints"].append(constraint_info)

            # Get geometry information
            for i, geo in enumerate(sketch.Geometry):
                geo_info = {
                    "index": i,
                    "type": type(geo).__name__,
                    "construction": (
                        geo.Construction if hasattr(geo, "Construction") else False
                    ),
                }

                # Add type-specific information
                if hasattr(geo, "Center"):
                    geo_info["center"] = [geo.Center.x, geo.Center.y]
                if hasattr(geo, "Radius"):
                    geo_info["radius"] = geo.Radius
                if hasattr(geo, "StartPoint"):
                    geo_info["start_point"] = [geo.StartPoint.x, geo.StartPoint.y]
                if hasattr(geo, "EndPoint"):
                    geo_info["end_point"] = [geo.EndPoint.x, geo.EndPoint.y]

                context["geometry"].append(geo_info)

            # Check if fully constrained (simplified check)
            # This is a basic heuristic - real implementation would be more complex
            total_dof = len(sketch.Geometry) * 2  # Simplified
            constraint_dof = len(sketch.Constraints)
            context["fully_constrained"] = constraint_dof >= total_dof

            return context

        except Exception as e:
            logger.error("Failed to get sketch context: %s", str(e))
            return {"error": str(e)}

    def _get_active_document_info(self) -> Optional[DocumentInfo]:
        """Get information about the active document"""
        if not App or not App.ActiveDocument:
            return None

        doc = App.ActiveDocument
        return self._create_document_info(doc)

    def _get_all_documents_info(self) -> List[DocumentInfo]:
        """Get information about all open documents"""
        if not App:
            return []

        docs = []
        for doc in App.listDocuments().values():
            doc_info = self._create_document_info(doc)
            if doc_info:
                docs.append(doc_info)

        return docs

    def _get_document_info_by_name(self, doc_name: str) -> Optional[DocumentInfo]:
        """Get document info by name"""
        if not App:
            return None

        doc = App.getDocument(doc_name)
        if doc:
            return self._create_document_info(doc)

        return None

    def _create_document_info(self, doc) -> DocumentInfo:
        """Create DocumentInfo from FreeCAD document"""
        objects = []
        for obj in doc.Objects:
            obj_info = self._create_object_info(obj)
            objects.append(obj_info)

        # Get selection and visibility info
        selected_objects = []
        visible_objects = []

        if Gui:
            # Get selected objects in this document
            for sel_obj in Gui.Selection.getSelection():
                if sel_obj.Document == doc:
                    selected_objects.append(sel_obj.Name)

            # Get visible objects
            for obj in doc.Objects:
                view_obj = Gui.getDocument(doc.Name).getObject(obj.Name)
                if view_obj and view_obj.Visibility:
                    visible_objects.append(obj.Name)

        return DocumentInfo(
            name=doc.Name,
            file_path=doc.FileName if hasattr(doc, "FileName") else None,
            objects=objects,
            selected_objects=selected_objects,
            visible_objects=visible_objects,
        )

    def _create_object_info(self, obj) -> ObjectInfo:
        """Create ObjectInfo from FreeCAD object"""
        # Extract basic properties
        properties = {}
        for prop_name in obj.PropertiesList:
            try:
                prop_value = getattr(obj, prop_name)
                # Convert to serializable format
                if hasattr(prop_value, "__dict__"):
                    if hasattr(prop_value, "x") and hasattr(prop_value, "y"):
                        # Vector-like object
                        if hasattr(prop_value, "z"):
                            properties[prop_name] = [
                                prop_value.x,
                                prop_value.y,
                                prop_value.z,
                            ]
                        else:
                            properties[prop_name] = [prop_value.x, prop_value.y]
                    else:
                        properties[prop_name] = str(prop_value)
                else:
                    properties[prop_name] = prop_value
            except Exception:
                # Skip properties that can't be accessed
                pass

        # Get placement information
        placement = None
        if hasattr(obj, "Placement"):
            p = obj.Placement
            placement = {
                "position": [p.Base.x, p.Base.y, p.Base.z],
                "rotation": [
                    p.Rotation.Q[0],
                    p.Rotation.Q[1],
                    p.Rotation.Q[2],
                    p.Rotation.Q[3],
                ],
            }

        # Get shape information if available
        shape_info = None
        if hasattr(obj, "Shape") and obj.Shape:
            shape_info = self._extract_shape_info(obj.Shape)

        return ObjectInfo(
            name=obj.Name,
            label=obj.Label,
            type_id=obj.TypeId,
            properties=properties,
            placement=placement,
            shape_info=shape_info,
        )

    def _extract_shape_info(self, shape) -> Dict[str, Any]:
        """Extract information from a FreeCAD shape"""
        try:
            info = {
                "type": shape.ShapeType,
                "valid": shape.isValid(),
                "volume": shape.Volume if hasattr(shape, "Volume") else None,
                "area": shape.Area if hasattr(shape, "Area") else None,
                "length": shape.Length if hasattr(shape, "Length") else None,
                "face_count": len(shape.Faces) if hasattr(shape, "Faces") else 0,
                "edge_count": len(shape.Edges) if hasattr(shape, "Edges") else 0,
                "vertex_count": (
                    len(shape.Vertexes) if hasattr(shape, "Vertexes") else 0
                ),
            }

            # Bounding box
            if hasattr(shape, "BoundBox"):
                bbox = shape.BoundBox
                info["bounding_box"] = {
                    "x_min": bbox.XMin,
                    "x_max": bbox.XMax,
                    "y_min": bbox.YMin,
                    "y_max": bbox.YMax,
                    "z_min": bbox.ZMin,
                    "z_max": bbox.ZMax,
                    "dimensions": {
                        "length": bbox.XLength,
                        "width": bbox.YLength,
                        "height": bbox.ZLength,
                    },
                }

            return info

        except Exception as e:
            logger.error("Failed to extract shape info: %s", str(e))
            return {"error": str(e)}

    def _analyze_object_geometry(self, obj) -> Dict[str, Any]:
        """Analyze geometry of a single object"""
        analysis = {"name": obj.Name, "label": obj.Label, "type": obj.TypeId}

        if hasattr(obj, "Shape") and obj.Shape:
            shape_info = self._extract_shape_info(obj.Shape)
            analysis.update(shape_info)

        return analysis

    def _get_selection_info(self) -> List[ObjectInfo]:
        """Get information about selected objects"""
        if not Gui:
            return []

        selection = []
        for obj in Gui.Selection.getSelection():
            obj_info = self._create_object_info(obj)
            selection.append(obj_info)

        return selection

    def _get_workbench_info(self) -> Optional[WorkbenchInfo]:
        """Get information about current workbench"""
        if not Gui:
            return None

        try:
            workbench = Gui.activeWorkbench()

            return WorkbenchInfo(
                name=workbench.name() if hasattr(workbench, "name") else str(workbench),
                active_tool=None,  # Would need more complex detection
                available_commands=[],  # Would need workbench introspection
            )
        except Exception as e:
            logger.error("Failed to get workbench info: %s", str(e))
            return None

    def _get_view_info(self) -> Dict[str, Any]:
        """Get information about current view"""
        if not Gui:
            return {}

        try:
            view = Gui.ActiveDocument.ActiveView if Gui.ActiveDocument else None
            if not view:
                return {}

            info = {}

            # Camera information
            if hasattr(view, "getCameraNode"):
                camera = view.getCameraNode()
                if camera:
                    info["camera_type"] = (
                        "perspective"
                        if camera.getTypeId().find("Perspective") >= 0
                        else "orthographic"
                    )

            # View direction
            if hasattr(view, "getViewDirection"):
                view_dir = view.getViewDirection()
                info["view_direction"] = [view_dir.x, view_dir.y, view_dir.z]

            return info

        except Exception as e:
            logger.error("Failed to get view info: %s", str(e))
            return {}

    def _get_preferences_info(self) -> Dict[str, Any]:
        """Get relevant FreeCAD preferences"""
        if not App:
            return {}

        try:
            # Get some basic preferences that might be relevant
            prefs = {}

            # Units
            if hasattr(App, "ParamGet"):
                param = App.ParamGet("User parameter:BaseApp/Preferences/Units")
                prefs["units"] = {
                    "user_schema": param.GetInt("UserSchema", 0),
                    "decimals": param.GetInt("Decimals", 2),
                }

            return prefs

        except Exception as e:
            logger.error("Failed to get preferences info: %s", str(e))
            return {}

    def _get_mock_context(self) -> FreeCADContext:
        """Get mock context for testing without FreeCAD"""
        mock_object = ObjectInfo(
            name="MockObject",
            label="Mock Object",
            type_id="Part::Box",
            properties={"Length": 10, "Width": 10, "Height": 10},
        )

        mock_doc = DocumentInfo(
            name="MockDocument",
            file_path=None,
            objects=[mock_object],
            selected_objects=[],
            visible_objects=["MockObject"],
        )

        return FreeCADContext(
            active_document=mock_doc,
            all_documents=[mock_doc],
            workbench=WorkbenchInfo(
                name="MockWorkbench", active_tool=None, available_commands=[]
            ),
            selection=[],
            view_info={},
            preferences={},
        )
