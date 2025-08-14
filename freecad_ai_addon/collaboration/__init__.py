"""Collaboration feature package (Phase 6.2 initial implementation).

This package provides early, testable foundations for the Collaboration
Features outlined in taskplan.md section 6.2:

Implemented (MVP skeletons):
 - Design review & annotation tools (in-memory + JSON persistence)
 - Design history & versioning (lightweight document snapshotting)
 - Shared knowledge base (local, keyword searchable)
 - Design template sharing (exports parametric templates)

Deferred / future (placeholders only):
 - Team collaboration (multi-user sync, networking layer)
 - Collaborative problem solving sessions

Design goals for MVP:
 - Headless test compatibility (graceful when FreeCAD GUI absent)
 - Pure Python + stdlib only
 - Clear extension points ("TODO" markers)

Submodules:
 - annotations: Annotation model + DesignReviewManager
 - versioning: VersionManager for snapshot history
 - knowledge_base: KnowledgeBase local store
 - template_sharing: Template export utilities

All managers expose lightweight dataclass-based records to simplify future
serialization / remote transport.
"""
from .annotations import Annotation, DesignReviewManager  # noqa: F401
from .versioning import VersionManager, VersionSnapshot  # noqa: F401
from .knowledge_base import KnowledgeBase, KnowledgeEntry  # noqa: F401
from .template_sharing import TemplateSharingManager  # noqa: F401

__all__ = [
    "Annotation",
    "DesignReviewManager",
    "VersionManager",
    "VersionSnapshot",
    "KnowledgeBase",
    "KnowledgeEntry",
    "TemplateSharingManager",
]
