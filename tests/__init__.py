"""
Test package for FreeCAD AI Addon.
Contains unit tests and integration tests for the addon functionality.
"""

import sys
from pathlib import Path

# Add the addon directory to Python path for testing
addon_dir = Path(__file__).parent.parent / "freecad_ai_addon"
sys.path.insert(0, str(addon_dir))

# Test configuration
TEST_CONFIG = {
    "test_data_dir": Path(__file__).parent / "test_data",
    "temp_dir": Path(__file__).parent / "temp",
    "mock_freecad": True  # Use mock FreeCAD objects in tests
}
