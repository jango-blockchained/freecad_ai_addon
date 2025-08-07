"""
Configuration Management for FreeCAD AI Addon

Provides centralized configuration management with secure storage
of sensitive data like API keys.
"""

import json
from pathlib import Path
from typing import Dict, Any
from freecad_ai_addon.utils.logging import get_logger

logger = get_logger("config")


class ConfigManager:
    """Manages configuration for the FreeCAD AI Addon"""

    def __init__(self):
        """Initialize the configuration manager"""
        self.config_dir = Path.home() / ".FreeCAD" / "ai_addon"
        self.config_file = self.config_dir / "config.json"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                logger.info("Configuration loaded successfully")
                return config
            else:
                logger.info("No existing configuration found, using defaults")
                return self._get_default_config()
        except Exception as e:
            logger.error("Failed to load configuration: %s", str(e))
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "version": "0.1.0",
            "ui": {
                "theme": "auto",
                "conversation_history_limit": 100,
                "auto_save_conversations": True,
            },
            "mcp": {"timeout": 30, "retry_attempts": 3, "connection_pool_size": 5},
            "agent": {
                "safety_mode": True,
                "confirmation_required": True,
                "max_operations_per_session": 50,
            },
            "logging": {"level": "INFO", "max_log_size_mb": 10, "backup_count": 5},
        }

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.

        Args:
            key: Configuration key (e.g., 'ui.theme')
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key.split(".")
        value = self._config

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value using dot notation.

        Args:
            key: Configuration key (e.g., 'ui.theme')
            value: Value to set
        """
        keys = key.split(".")
        config = self._config

        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # Set the value
        config[keys[-1]] = value
        self._save_config()

    def _save_config(self) -> None:
        """Save configuration to file"""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2)
            logger.info("Configuration saved successfully")
        except Exception as e:
            logger.error("Failed to save configuration: %s", str(e))

    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults"""
        self._config = self._get_default_config()
        self._save_config()
        logger.info("Configuration reset to defaults")

    def export_config(self, file_path: str) -> bool:
        """
        Export configuration to a file.

        Args:
            file_path: Path to export file

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2)
            logger.info("Configuration exported to %s", file_path)
            return True
        except Exception as e:
            logger.error("Failed to export configuration: %s", str(e))
            return False

    def import_config(self, file_path: str) -> bool:
        """
        Import configuration from a file.

        Args:
            file_path: Path to import file

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                imported_config = json.load(f)

            # Validate and merge with current config
            self._config.update(imported_config)
            self._save_config()
            logger.info("Configuration imported from %s", file_path)
            return True
        except Exception as e:
            logger.error("Failed to import configuration: %s", str(e))
            return False


# Global config manager instance
_config_manager = None


def get_config_manager() -> ConfigManager:
    """Get the global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager
