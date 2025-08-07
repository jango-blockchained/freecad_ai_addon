"""
Logging Configuration for FreeCAD AI Addon

Provides centralized logging configuration and utilities for the addon.
"""

import logging
from pathlib import Path


def setup_logging(level=logging.INFO):
    """
    Set up logging configuration for the FreeCAD AI Addon.

    Args:
        level: Logging level (default: INFO)
    """
    try:
        # Create logs directory in user's FreeCAD directory
        freecad_user_dir = Path.home() / ".FreeCAD"
        log_dir = freecad_user_dir / "logs" / "ai_addon"
        log_dir.mkdir(parents=True, exist_ok=True)

        # Configure logging
        log_file = log_dir / "freecad_ai_addon.log"

        logging.basicConfig(
            level=level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
        )

        logger = logging.getLogger("freecad_ai_addon")
        logger.info("Logging system initialized successfully")

    except Exception as e:
        # Fallback to basic logging if setup fails
        logging.basicConfig(level=level)
        logger = logging.getLogger("freecad_ai_addon")
        logger.error(f"Failed to setup advanced logging: {e}")


def get_logger(name):
    """
    Get a logger instance for a specific module.

    Args:
        name: Name of the module/component

    Returns:
        Logger instance
    """
    return logging.getLogger(f"freecad_ai_addon.{name}")
