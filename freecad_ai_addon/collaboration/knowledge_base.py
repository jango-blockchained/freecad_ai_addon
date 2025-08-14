"""Local shared knowledge base (initial MVP).

Stores design standards, best practices, and decisions as searchable
entries. Future iterations may sync across team members via network or
cloud backends; for now it's purely local.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import json
import re
from typing import List, Dict, Any, Optional

from freecad_ai_addon.utils.logging import get_logger

logger = get_logger("collaboration.knowledge_base")


def _kb_dir() -> Path:
    base = Path.home() / ".FreeCAD" / "ai_addon" / "collaboration"
    base.mkdir(parents=True, exist_ok=True)
    return base / "knowledge_base.json"


@dataclass
class KnowledgeEntry:
    id: str
    title: str
    content: str
    tags: List[str]
    created_at: str
    metadata: Dict[str, Any]


class KnowledgeBase:
    def __init__(self):
        self._entries: List[KnowledgeEntry] = []
        self._loaded = False

    # -- Persistence --------------------------------------------------
    def _load(self):
        if self._loaded:
            return
        path = _kb_dir()
        if path.exists():
            try:
                data = json.loads(path.read_text())
                self._entries = [KnowledgeEntry(**e) for e in data.get("entries", [])]
            except Exception as e:  # noqa: BLE001
                logger.error("Failed loading knowledge base: %s", e)
        self._loaded = True

    def _save(self):
        path = _kb_dir()
        payload = {"entries": [asdict(e) for e in self._entries]}
        try:
            path.write_text(json.dumps(payload, indent=2))
        except Exception as e:  # noqa: BLE001
            logger.error("Failed saving knowledge base: %s", e)

    # -- Public API ----------------------------------------------------
    def add_entry(
        self,
        title: str,
        content: str,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> KnowledgeEntry:
        import uuid

        self._load()
        entry = KnowledgeEntry(
            id=str(uuid.uuid4()),
            title=title,
            content=content,
            tags=tags or [],
            created_at=datetime.utcnow().isoformat(),
            metadata=metadata or {},
        )
        self._entries.append(entry)
        self._save()
        return entry

    def list_entries(self) -> List[KnowledgeEntry]:
        self._load()
        return list(self._entries)

    def search(self, query: str) -> List[KnowledgeEntry]:
        self._load()
        if not query.strip():
            return []
        pattern = re.compile(re.escape(query), re.IGNORECASE)
        return [
            e
            for e in self._entries
            if pattern.search(e.title)
            or pattern.search(e.content)
            or any(pattern.search(t) for t in e.tags)
        ]

    def stats(self) -> Dict[str, Any]:
        self._load()
        return {
            "count": len(self._entries),
            "tag_counts": self._tag_counts(),
        }

    def _tag_counts(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for e in self._entries:
            for t in e.tags:
                counts[t] = counts.get(t, 0) + 1
        return counts


__all__ = ["KnowledgeBase", "KnowledgeEntry"]
