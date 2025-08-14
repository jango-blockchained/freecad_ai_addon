"""Tests for initial collaboration features (Phase 6.2 MVP).

Ensures annotation manager, version manager, knowledge base and template
sharing utilities function in a headless environment.
"""
from __future__ import annotations


from freecad_ai_addon.collaboration import (
    DesignReviewManager,
    VersionManager,
    KnowledgeBase,
    TemplateSharingManager,
)
from freecad_ai_addon.advanced_features import DesignType


def test_annotations_create_and_persist(tmp_path, monkeypatch):
    # Redirect base directory to temp to avoid polluting user home
    import freecad_ai_addon.collaboration.annotations as anns_mod

    def temp_base():
        d = tmp_path / "annotations"
        d.mkdir(parents=True, exist_ok=True)
        return d

    monkeypatch.setattr(anns_mod, "_get_base_dir", temp_base)

    mgr = DesignReviewManager()
    ann = mgr.create_annotation("doc1", "alice", "Check fillet radius", category="dfm")
    assert ann.id and ann.document_id == "doc1"
    anns = mgr.list_annotations("doc1")
    assert len(anns) == 1
    # New manager should load persisted file
    mgr2 = DesignReviewManager()
    anns2 = mgr2.list_annotations("doc1")
    assert len(anns2) == 1 and anns2[0].message.startswith("Check fillet")


def test_version_manager(tmp_path, monkeypatch):
    import freecad_ai_addon.collaboration.versioning as ver_mod

    def temp_versions():
        d = tmp_path / "versions"
        d.mkdir(parents=True, exist_ok=True)
        return d

    monkeypatch.setattr(ver_mod, "_base_dir", temp_versions)

    vm = VersionManager()
    v1 = vm.create_version("docX", "Initial")
    v2 = vm.create_version("docX", "Added holes", metadata={"holes": 4})
    assert v1.version_id == "v001"
    assert v2.parent_version == v1.version_id
    assert vm.latest_version("docX").version_id == v2.version_id


def test_knowledge_base(tmp_path, monkeypatch):
    import freecad_ai_addon.collaboration.knowledge_base as kb_mod

    kb_file = tmp_path / "kb.json"

    def temp_kb_dir():
        return kb_file

    monkeypatch.setattr(kb_mod, "_kb_dir", temp_kb_dir)

    kb = KnowledgeBase()
    kb.add_entry(
        "Standard Fillet Radius", "Use >= 1mm for aluminum.", ["dfm", "fillet"]
    )
    kb.add_entry("Wall Thickness", "Min 1.5mm for FDM printing", ["3d_printing", "dfm"])
    results = kb.search("fillet")
    assert len(results) == 1 and results[0].title.startswith("Standard Fillet")
    stats = kb.stats()
    assert stats["count"] == 2
    assert stats["tag_counts"]["dfm"] == 2


def test_template_sharing(tmp_path):
    mgr = TemplateSharingManager()
    out = mgr.export_template(
        DesignType.BEARING_MOUNT,
        {"bearing_diameter": 12.0},
        out_file=tmp_path / "bearing_mount.json",
    )
    assert out.exists()
    content = out.read_text()
    assert "BEARING_MOUNT" in content
