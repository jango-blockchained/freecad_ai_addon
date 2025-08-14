"""Lightweight design history & versioning (initial MVP).

Captures simple document snapshots requested by the collaboration plan.
Future iterations can integrate deeper FreeCAD object diffs.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import json
import hashlib
from typing import List, Dict, Any, Optional

from freecad_ai_addon.utils.logging import get_logger

logger = get_logger("collaboration.versioning")


def _base_dir() -> Path:
    base = Path.home() / ".FreeCAD" / "ai_addon" / "collaboration" / "versions"
    base.mkdir(parents=True, exist_ok=True)
    return base


def _hash(document_id: str) -> str:
    return hashlib.sha256(document_id.encode()).hexdigest()[:16]


@dataclass
class VersionSnapshot:
    document_id: str
    version_id: str
    created_at: str
    summary: str
    metadata: Dict[str, Any]
    parent_version: Optional[str] = None


class VersionManager:
    def __init__(self):
        self._cache: Dict[str, List[VersionSnapshot]] = {}

    def _file(self, document_id: str) -> Path:
        return _base_dir() / f"{_hash(document_id)}.json"

    def _load(self, document_id: str) -> List[VersionSnapshot]:
        if document_id in self._cache:
            return self._cache[document_id]
        path = self._file(document_id)
        if path.exists():
            try:
                data = json.loads(path.read_text())
                snaps = [VersionSnapshot(**d) for d in data.get("versions", [])]
                self._cache[document_id] = snaps
                return snaps
            except Exception as e:  # noqa: BLE001
                logger.error("Load versions failed for %s: %s", document_id, e)
        self._cache[document_id] = []
        return []

    def _save(self, document_id: str):
        path = self._file(document_id)
        snaps = self._cache.get(document_id, [])
        payload = {"document_id": document_id, "versions": [asdict(s) for s in snaps]}
        try:
            path.write_text(json.dumps(payload, indent=2))
        except Exception as e:  # noqa: BLE001
            logger.error("Save versions failed for %s: %s", document_id, e)

    def create_version(
        self, document_id: str, summary: str, metadata: Optional[Dict[str, Any]] = None
    ) -> VersionSnapshot:
        snaps = self._load(document_id)
        parent = snaps[-1].version_id if snaps else None
        version_id = f"v{len(snaps)+1:03d}"
        snap = VersionSnapshot(
            document_id=document_id,
            version_id=version_id,
            created_at=datetime.utcnow().isoformat(),
            summary=summary,
            metadata=metadata or {},
            parent_version=parent,
        )
        snaps.append(snap)
        self._cache[document_id] = snaps
        self._save(document_id)
        logger.debug("Created version %s for %s", version_id, document_id)
        return snap

    def list_versions(self, document_id: str) -> List[VersionSnapshot]:
        return list(self._load(document_id))

    def latest_version(self, document_id: str) -> Optional[VersionSnapshot]:
        snaps = self._load(document_id)
        return snaps[-1] if snaps else None

    def to_dict(self, document_id: str) -> Dict[str, Any]:
        snaps = self._load(document_id)
        return {
            "document_id": document_id,
            "count": len(snaps),
            "versions": [asdict(s) for s in snaps],
        }


__all__ = ["VersionManager", "VersionSnapshot"]
