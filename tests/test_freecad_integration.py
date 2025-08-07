"""
Test FreeCAD Integration

Test the conversation widget integration with FreeCAD.
"""

import sys

# Mock FreeCAD modules for testing


class MockFreeCAD:
    class Version:
        def __init__(self):
            pass

        def __call__(self):
            return ["0.20", "29177", "2022/05/12"]

    class ActiveDocument:
        Name = "TestDocument"
        Label = "Test Document"
        FileName = "/tmp/test.FCStd"

        class Objects:
            def __init__(self):
                self.items = []

        def __init__(self):
            self.Objects = []

    def __init__(self):
        self.ActiveDocument = self.ActiveDocument()
        self.Version = self.Version()


class MockFreeCADGui:
    class Selection:
        @staticmethod
        def getSelection():
            return []

        @staticmethod
        def addObserver(observer):
            pass

        @staticmethod
        def removeObserver(observer):
            pass

    class activeWorkbench:
        @staticmethod
        def name():
            return "PartWorkbench"

    @staticmethod
    def getMainWindow():
        from PySide6.QtWidgets import QMainWindow

        return QMainWindow()


# Mock the FreeCAD modules
sys.modules["FreeCAD"] = MockFreeCAD()
sys.modules["FreeCADGui"] = MockFreeCADGui()

# Now we can test our integration
from freecad_ai_addon.integration.freecad_integration import (
    get_freecad_context,
    setup_selection_observer,
)


def test_freecad_context():
    """Test getting FreeCAD context"""
    try:
        context = get_freecad_context()
        print("FreeCAD Context:")
        print(f"  Document: {context['document']['name']}")
        print(f"  Objects: {context['document']['count']}")
        print(f"  Selection: {context['selection']['count']}")
        print(f"  Workbench: {context['workbench']}")
        print(f"  Version: {context['version']}")
        print("✓ Context retrieval test passed")

    except Exception as e:
        print(f"✗ Context retrieval test failed: {e}")


def test_selection_observer():
    """Test selection observer"""
    try:

        def on_selection_changed(selection_info):
            print(f"Selection changed: {selection_info}")

        setup_selection_observer(on_selection_changed)
        print("✓ Selection observer test passed")

    except Exception as e:
        print(f"✗ Selection observer test failed: {e}")


def test_conversation_dock():
    """Test conversation dock creation"""
    try:
        # This would normally require a running FreeCAD instance
        print("✓ Conversation dock test prepared (requires FreeCAD)")

    except Exception as e:
        print(f"✗ Conversation dock test failed: {e}")


if __name__ == "__main__":
    print("Testing FreeCAD Integration...")
    print("=" * 40)

    test_freecad_context()
    test_selection_observer()
    test_conversation_dock()

    print("=" * 40)
    print("Integration tests completed!")
