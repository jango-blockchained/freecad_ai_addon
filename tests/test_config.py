"""
Test suite for configuration management
"""

import pytest
import tempfile
from pathlib import Path
from freecad_ai_addon.utils.config import ConfigManager


class TestConfigManager:
    """Test cases for ConfigManager"""

    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_manager = ConfigManager()
        # Override config directory for testing
        self.config_manager.config_dir = self.temp_dir
        self.config_manager.config_file = self.temp_dir / "config.json"

    def test_default_config_creation(self):
        """Test that default configuration is created properly"""
        config = self.config_manager._get_default_config()

        assert "version" in config
        assert "ui" in config
        assert "mcp" in config
        assert "agent" in config
        assert "logging" in config

        assert config["version"] == "0.1.0"
        assert config["ui"]["theme"] == "auto"
        assert config["agent"]["safety_mode"] is True

    def test_get_config_value(self):
        """Test getting configuration values"""
        # Test simple key
        version = self.config_manager.get("version")
        assert version == "0.1.0"

        # Test nested key
        theme = self.config_manager.get("ui.theme")
        assert theme == "auto"

        # Test non-existent key with default
        non_existent = self.config_manager.get("non.existent", "default")
        assert non_existent == "default"

    def test_set_config_value(self):
        """Test setting configuration values"""
        # Set simple value
        self.config_manager.set("test_key", "test_value")
        assert self.config_manager.get("test_key") == "test_value"

        # Set nested value
        self.config_manager.set("ui.new_setting", True)
        assert self.config_manager.get("ui.new_setting") is True

    def test_config_persistence(self):
        """Test that configuration persists to file"""
        # Set a value
        self.config_manager.set("test.persistence", "persistent_value")

        # Create new config manager instance
        new_config_manager = ConfigManager()
        new_config_manager.config_dir = self.temp_dir
        new_config_manager.config_file = self.temp_dir / "config.json"
        new_config_manager._config = new_config_manager._load_config()

        # Check that value persisted
        assert new_config_manager.get("test.persistence") == "persistent_value"

    def test_export_import_config(self):
        """Test configuration export and import"""
        # Set some test values
        self.config_manager.set("export.test1", "value1")
        self.config_manager.set("export.test2", "value2")

        # Export config
        export_file = self.temp_dir / "export.json"
        result = self.config_manager.export_config(str(export_file))
        assert result is True
        assert export_file.exists()

        # Reset config and import
        self.config_manager.reset_to_defaults()
        assert self.config_manager.get("export.test1") is None

        result = self.config_manager.import_config(str(export_file))
        assert result is True
        assert self.config_manager.get("export.test1") == "value1"
        assert self.config_manager.get("export.test2") == "value2"


if __name__ == "__main__":
    pytest.main([__file__])
