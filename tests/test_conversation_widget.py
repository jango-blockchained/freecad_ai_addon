"""
Test for Conversation Widget

Basic test to ensure the conversation widget components work correctly.
Runs headless and avoids mixing Qt bindings.
"""

import os
import sys
import pytest

# Ensure headless Qt
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# Import the same binding family as the widget prefers: PySide2 first, then PySide6
qt_loaded = False
try:
    from PySide2.QtWidgets import QApplication, QMainWindow  # type: ignore

    qt_loaded = True
except Exception:
    try:
        from PySide6.QtWidgets import QApplication, QMainWindow  # type: ignore

        qt_loaded = True
    except Exception:
        pytest.skip("No compatible Qt binding (PySide2/PySide6) available")

from freecad_ai_addon.ui.conversation_widget import ConversationWidget


def test_conversation_widget():
    """Test the conversation widget in a basic window"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    # Create main window
    window = QMainWindow()
    window.setWindowTitle("FreeCAD AI Conversation Test")
    window.setGeometry(100, 100, 800, 600)

    # Create conversation widget
    conversation_widget = ConversationWidget()
    window.setCentralWidget(conversation_widget)

    # Add some test messages
    conversation_widget.add_system_message("Welcome to FreeCAD AI Assistant!")
    conversation_widget.add_user_message("Hello, can you help me with FreeCAD?")

    assistant_message = (
        "Of course! I can help you with **FreeCAD** operations. "
        "Here are some things I can do:\n\n"
        "- Create 3D models and sketches\n"
        "- Modify existing designs\n"
        "- Provide design suggestions\n"
        "- Help with measurements and constraints\n\n"
        "What would you like to work on?\n\n"
        "```python\n"
        "# Example: Create a cube\n"
        "import FreeCAD\n"
        "doc = FreeCAD.newDocument()\n"
        "cube = doc.addObject('Part::Box', 'Cube')\n"
        "cube.Length = 10\n"
        "cube.Width = 10\n"
        "cube.Height = 10\n"
        "doc.recompute()\n"
        "```"
    )
    conversation_widget.add_assistant_message(
        assistant_message, provider="OpenAI GPT-4"
    )

    # Connect signal for testing
    def on_message_sent(text, attachments):
        print(f"Message sent: {text}")
        if attachments:
            print(f"Attachments: {attachments}")
        # Echo the message back as assistant response
        response = (
            f"I received your message: *{text}*\n\n" "How can I help you with this?"
        )
        conversation_widget.add_assistant_message(response, provider="Test Assistant")

    conversation_widget.message_sent.connect(on_message_sent)

    # Do not show the window in headless test environments
    # window.show()

    return app, window, conversation_widget


if __name__ == "__main__":
    app, window, widget = test_conversation_widget()
    sys.exit(app.exec())
