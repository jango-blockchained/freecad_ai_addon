#!/usr/bin/env python3
"""
Test Agent Integration

Test script to validate the agent conversation integration without FreeCAD.
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from freecad_ai_addon.ui.enhanced_conversation_widget import (
    EnhancedConversationWidget
)
from freecad_ai_addon.utils.logging import get_logger

# Add the project path for imports
sys.path.insert(0, '/home/jango/Git/freecad-ai-addon')

logger = get_logger('test_agent_integration')


class TestMainWindow(QMainWindow):
    """Test main window for the enhanced conversation widget"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FreeCAD AI Agent Integration Test")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout
        layout = QVBoxLayout(central_widget)
        
        # Create enhanced conversation widget
        try:
            self.conversation_widget = EnhancedConversationWidget()
            layout.addWidget(self.conversation_widget)
            
            # Add welcome message
            self.conversation_widget.add_system_message(
                "🤖 **AI Agent Framework Test Environment**\n\n"
                "This is a test of the integrated agent conversation system. "
                "The agent framework has been initialized and is ready for "
                "testing.\n\n"
                "**Available Test Commands:**\n"
                "- 'create a box' - Test geometry agent\n"
                "- 'make a sketch' - Test sketch agent\n"
                "- 'analyze the model' - Test analysis agent\n"
                "- 'help' - Show available operations"
            )
            
            logger.info("Enhanced conversation widget created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create enhanced conversation widget: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Main test function"""
    # Create Qt application
    app = QApplication(sys.argv)
    
    # Create and show main window
    window = TestMainWindow()
    window.show()
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
