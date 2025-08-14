"""Design review & annotation tools (initial MVP).

The goal is to provide a simple, testable annotation system that can later
be rendered as 3D overlays inside FreeCAD. For now, annotations are stored
as JSON entries with positional metadata (if available) plus AI / reviewer
comments.

Persistence Layout:
  ~/.FreeCAD/ai_addon/collaboration/annotations/<document_hash>.json

Document identification:
  FreeCAD documents can be identified by file path; if unavailable (e.g.
  unsaved / test mode), the caller may supply a synthetic identifier.

Extensibility:
  - Future: 3D anchor type (vertex/edge/face references) once FreeCAD
    object references are integrated.
  - Future: status workflow (open / resolved / needs_changes / approved).
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import json
import hashlib
import uuid
from typing import List, Dict, Any, Optional

from freecad_ai_addon.utils.logging import get_logger

logger = get_logger("collaboration.annotations")


def _get_base_dir() -> Path:
    # Avoid importing FreeCAD (headless tests) – just reuse ~/.FreeCAD
    home = Path.home()
    base = home / ".FreeCAD" / "ai_addon" / "collaboration" / "annotations"
    base.mkdir(parents=True, exist_ok=True)
    return base


def _doc_hash(document_id: str) -> str:
    return hashlib.sha256(document_id.encode("utf-8")).hexdigest()[:16]


@dataclass
class Annotation:
    id: str
    document_id: str
    author: str
    message: str
    created_at: str
    category: str = "general"
    position: Optional[Dict[str, Any]] = None  # e.g., {"type": "3d", "point": [x,y,z]}
    ai_generated: bool = False
    metadata: Optional[Dict[str, Any]] = None

    @staticmethod
    def create(
        document_id: str,
        author: str,
        message: str,
        category: str = "general",
        position: Optional[Dict[str, Any]] = None,
        ai_generated: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "Annotation":
        return Annotation(
            id=str(uuid.uuid4()),
            document_id=document_id,
            author=author,
            message=message,
            created_at=datetime.utcnow().isoformat(),
            category=category,
            position=position,
            ai_generated=ai_generated,
            metadata=metadata,
        )


class DesignReviewManager:
    def __init__(self):
        self._cache: Dict[str, List[Annotation]] = {}

    # -- Persistence -----------------------------------------------------
    def _file_for(self, document_id: str) -> Path:
        return _get_base_dir() / f"{_doc_hash(document_id)}.json"

    def _load(self, document_id: str) -> List[Annotation]:
        if document_id in self._cache:
            return self._cache[document_id]
        path = self._file_for(document_id)
        if path.exists():
            try:
                data = json.loads(path.read_text())
                anns = [Annotation(**item) for item in data.get("annotations", [])]
                self._cache[document_id] = anns
                return anns
            except Exception as e:  # noqa: BLE001
                logger.error("Failed to load annotations for %s: %s", document_id, e)
        self._cache[document_id] = []
        return []

    def _save(self, document_id: str):
        path = self._file_for(document_id)
        anns = self._cache.get(document_id, [])
        payload = {"document_id": document_id, "annotations": [asdict(a) for a in anns]}
        try:
            path.write_text(json.dumps(payload, indent=2))
        except Exception as e:  # noqa: BLE001
            logger.error("Failed to save annotations for %s: %s", document_id, e)

    # -- Public API ------------------------------------------------------
    def add_annotation(self, annotation: Annotation):
        anns = self._load(annotation.document_id)
        anns.append(annotation)
        self._cache[annotation.document_id] = anns
        self._save(annotation.document_id)
        logger.debug("Added annotation %s to %s", annotation.id, annotation.document_id)
        return annotation

    def create_annotation(
        self,
        document_id: str,
        author: str,
        message: str,
        **kwargs,
    ) -> Annotation:
        ann = Annotation.create(document_id, author, message, **kwargs)
        return self.add_annotation(ann)

    def list_annotations(
        self, document_id: str, category: str | None = None
    ) -> List[Annotation]:
        anns = self._load(document_id)
        if category:
            return [a for a in anns if a.category == category]
        return list(anns)

    def to_dict(self, document_id: str) -> Dict[str, Any]:
        anns = self._load(document_id)
        return {
            "document_id": document_id,
            "count": len(anns),
            "annotations": [asdict(a) for a in anns],
        }

    # Placeholder for future advanced features
    def summarize_annotations(self, document_id: str) -> str:
        anns = self._load(document_id)
        if not anns:
            return "No annotations."
        cats: Dict[str, int] = {}
        for a in anns:
            cats[a.category] = cats.get(a.category, 0) + 1
        return ", ".join(f"{c}:{n}" for c, n in sorted(cats.items()))


__all__ = ["Annotation", "DesignReviewManager"]
