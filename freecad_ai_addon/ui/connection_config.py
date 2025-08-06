"""
Connection Management Configuration Dialog

Provides UI for configuring connection management settings.
"""

from PySide6 import QtWidgets
from freecad_ai_addon.core.connection_manager import (
    get_connection_manager, ConnectionConfig
)
from freecad_ai_addon.utils.config import ConfigManager
from freecad_ai_addon.utils.logging import get_logger

logger = get_logger('connection_config')


class ConnectionConfigDialog(QtWidgets.QDialog):
    """Dialog for configuring connection management settings"""

    def __init__(self, parent=None):
        """Initialize the connection config dialog"""
        super().__init__(parent)
        self.config_manager = ConfigManager()
        self.connection_manager = get_connection_manager()

        self.setWindowTitle("Connection Management Settings")
        self.setModal(True)
        self.setMinimumSize(500, 400)

        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        """Set up the user interface"""
        layout = QtWidgets.QVBoxLayout(self)

        # Header
        header_label = QtWidgets.QLabel("Connection Management Configuration")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header_label)

        # Retry Settings Group
        retry_group = QtWidgets.QGroupBox("Retry Settings")
        retry_layout = QtWidgets.QFormLayout(retry_group)

        self.retry_attempts_spin = QtWidgets.QSpinBox()
        self.retry_attempts_spin.setRange(1, 10)
        self.retry_attempts_spin.setValue(3)
        retry_layout.addRow("Retry Attempts:", self.retry_attempts_spin)

        self.retry_delay_spin = QtWidgets.QDoubleSpinBox()
        self.retry_delay_spin.setRange(1.0, 60.0)
        self.retry_delay_spin.setSuffix(" seconds")
        self.retry_delay_spin.setValue(5.0)
        retry_layout.addRow("Initial Retry Delay:", self.retry_delay_spin)

        self.retry_backoff_spin = QtWidgets.QDoubleSpinBox()
        self.retry_backoff_spin.setRange(1.0, 5.0)
        self.retry_backoff_spin.setSingleStep(0.1)
        self.retry_backoff_spin.setValue(2.0)
        retry_layout.addRow("Retry Backoff Multiplier:", self.retry_backoff_spin)

        self.max_retry_delay_spin = QtWidgets.QDoubleSpinBox()
        self.max_retry_delay_spin.setRange(10.0, 300.0)
        self.max_retry_delay_spin.setSuffix(" seconds")
        self.max_retry_delay_spin.setValue(60.0)
        retry_layout.addRow("Maximum Retry Delay:", self.max_retry_delay_spin)

        layout.addWidget(retry_group)

        # Health Check Settings Group
        health_group = QtWidgets.QGroupBox("Health Check Settings")
        health_layout = QtWidgets.QFormLayout(health_group)

        self.health_check_interval_spin = QtWidgets.QDoubleSpinBox()
        self.health_check_interval_spin.setRange(10.0, 600.0)
        self.health_check_interval_spin.setSuffix(" seconds")
        self.health_check_interval_spin.setValue(30.0)
        health_layout.addRow("Health Check Interval:", self.health_check_interval_spin)

        self.connection_timeout_spin = QtWidgets.QDoubleSpinBox()
        self.connection_timeout_spin.setRange(5.0, 120.0)
        self.connection_timeout_spin.setSuffix(" seconds")
        self.connection_timeout_spin.setValue(30.0)
        health_layout.addRow("Connection Timeout:", self.connection_timeout_spin)

        layout.addWidget(health_group)

        # Fallback Settings Group
        fallback_group = QtWidgets.QGroupBox("Fallback Settings")
        fallback_layout = QtWidgets.QVBoxLayout(fallback_group)

        self.enable_fallback_checkbox = QtWidgets.QCheckBox("Enable automatic fallback to other providers")
        self.enable_fallback_checkbox.setChecked(True)
        fallback_layout.addWidget(self.enable_fallback_checkbox)

        # Fallback order
        fallback_order_label = QtWidgets.QLabel("Fallback Provider Order:")
        fallback_layout.addWidget(fallback_order_label)

        self.fallback_list = QtWidgets.QListWidget()
        self.fallback_list.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.fallback_list.setMaximumHeight(100)
        fallback_layout.addWidget(self.fallback_list)

        fallback_buttons_layout = QtWidgets.QHBoxLayout()

        self.add_fallback_button = QtWidgets.QPushButton("Add Provider")
        self.add_fallback_button.clicked.connect(self._add_fallback_provider)
        fallback_buttons_layout.addWidget(self.add_fallback_button)

        self.remove_fallback_button = QtWidgets.QPushButton("Remove Selected")
        self.remove_fallback_button.clicked.connect(self._remove_fallback_provider)
        fallback_buttons_layout.addWidget(self.remove_fallback_button)

        fallback_buttons_layout.addStretch()
        fallback_layout.addLayout(fallback_buttons_layout)

        layout.addWidget(fallback_group)

        # Connection Pool Settings Group
        pool_group = QtWidgets.QGroupBox("Connection Pool Settings")
        pool_layout = QtWidgets.QFormLayout(pool_group)

        self.pool_size_spin = QtWidgets.QSpinBox()
        self.pool_size_spin.setRange(1, 20)
        self.pool_size_spin.setValue(5)
        pool_layout.addRow("Pool Size:", self.pool_size_spin)

        self.pool_timeout_spin = QtWidgets.QDoubleSpinBox()
        self.pool_timeout_spin.setRange(1.0, 60.0)
        self.pool_timeout_spin.setSuffix(" seconds")
        self.pool_timeout_spin.setValue(10.0)
        pool_layout.addRow("Pool Timeout:", self.pool_timeout_spin)

        layout.addWidget(pool_group)

        # Buttons
        button_layout = QtWidgets.QHBoxLayout()

        self.reset_button = QtWidgets.QPushButton("Reset to Defaults")
        self.reset_button.clicked.connect(self._reset_to_defaults)
        button_layout.addWidget(self.reset_button)

        button_layout.addStretch()

        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        self.save_button = QtWidgets.QPushButton("Save")
        self.save_button.clicked.connect(self.accept)
        self.save_button.setDefault(True)
        button_layout.addWidget(self.save_button)

        layout.addLayout(button_layout)

    def _load_settings(self):
        """Load current settings into the UI"""
        try:
            # Load from config manager
            self.retry_attempts_spin.setValue(
                self.config_manager.get('connection.retry_attempts', 3)
            )
            self.retry_delay_spin.setValue(
                self.config_manager.get('connection.retry_delay', 5.0)
            )
            self.retry_backoff_spin.setValue(
                self.config_manager.get('connection.retry_backoff', 2.0)
            )
            self.max_retry_delay_spin.setValue(
                self.config_manager.get('connection.max_retry_delay', 60.0)
            )
            self.health_check_interval_spin.setValue(
                self.config_manager.get('connection.health_check_interval', 30.0)
            )
            self.connection_timeout_spin.setValue(
                self.config_manager.get('connection.timeout', 30.0)
            )
            self.enable_fallback_checkbox.setChecked(
                self.config_manager.get('connection.enable_fallback', True)
            )
            self.pool_size_spin.setValue(
                self.config_manager.get('connection.pool_size', 5)
            )
            self.pool_timeout_spin.setValue(
                self.config_manager.get('connection.pool_timeout', 10.0)
            )

            # Load fallback order
            fallback_order = self.config_manager.get('connection.fallback_order', [])
            for provider in fallback_order:
                self.fallback_list.addItem(provider)

        except Exception as e:
            logger.error("Failed to load connection settings: %s", str(e))

    def _save_settings(self):
        """Save settings from UI to config"""
        try:
            # Save to config manager
            self.config_manager.set('connection.retry_attempts', self.retry_attempts_spin.value())
            self.config_manager.set('connection.retry_delay', self.retry_delay_spin.value())
            self.config_manager.set('connection.retry_backoff', self.retry_backoff_spin.value())
            self.config_manager.set('connection.max_retry_delay', self.max_retry_delay_spin.value())
            self.config_manager.set('connection.health_check_interval', self.health_check_interval_spin.value())
            self.config_manager.set('connection.timeout', self.connection_timeout_spin.value())
            self.config_manager.set('connection.enable_fallback', self.enable_fallback_checkbox.isChecked())
            self.config_manager.set('connection.pool_size', self.pool_size_spin.value())
            self.config_manager.set('connection.pool_timeout', self.pool_timeout_spin.value())

            # Save fallback order
            fallback_order = []
            for i in range(self.fallback_list.count()):
                fallback_order.append(self.fallback_list.item(i).text())
            self.config_manager.set('connection.fallback_order', fallback_order)

            # Update connection manager config
            config = ConnectionConfig(
                retry_attempts=self.retry_attempts_spin.value(),
                retry_delay=self.retry_delay_spin.value(),
                retry_backoff=self.retry_backoff_spin.value(),
                max_retry_delay=self.max_retry_delay_spin.value(),
                health_check_interval=self.health_check_interval_spin.value(),
                connection_timeout=self.connection_timeout_spin.value(),
                enable_fallback=self.enable_fallback_checkbox.isChecked(),
                fallback_order=fallback_order,
                pool_size=self.pool_size_spin.value(),
                pool_timeout=self.pool_timeout_spin.value()
            )

            self.connection_manager.update_config(config)
            logger.info("Connection settings saved successfully")

        except Exception as e:
            logger.error("Failed to save connection settings: %s", str(e))
            raise

    def _add_fallback_provider(self):
        """Add a provider to the fallback list"""
        providers = ["openai", "anthropic", "ollama"]
        existing_providers = []
        for i in range(self.fallback_list.count()):
            existing_providers.append(self.fallback_list.item(i).text())

        available_providers = [p for p in providers if p not in existing_providers]

        if not available_providers:
            QtWidgets.QMessageBox.information(
                self,
                "No Providers Available",
                "All available providers are already in the fallback list."
            )
            return

        provider, ok = QtWidgets.QInputDialog.getItem(
            self,
            "Add Fallback Provider",
            "Select provider to add:",
            available_providers,
            0,
            False
        )

        if ok:
            self.fallback_list.addItem(provider)

    def _remove_fallback_provider(self):
        """Remove selected provider from fallback list"""
        current_row = self.fallback_list.currentRow()
        if current_row >= 0:
            self.fallback_list.takeItem(current_row)

    def _reset_to_defaults(self):
        """Reset all settings to defaults"""
        reply = QtWidgets.QMessageBox.question(
            self,
            "Reset to Defaults",
            "Are you sure you want to reset all connection settings to defaults?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )

        if reply == QtWidgets.QMessageBox.Yes:
            self.retry_attempts_spin.setValue(3)
            self.retry_delay_spin.setValue(5.0)
            self.retry_backoff_spin.setValue(2.0)
            self.max_retry_delay_spin.setValue(60.0)
            self.health_check_interval_spin.setValue(30.0)
            self.connection_timeout_spin.setValue(30.0)
            self.enable_fallback_checkbox.setChecked(True)
            self.pool_size_spin.setValue(5)
            self.pool_timeout_spin.setValue(10.0)
            self.fallback_list.clear()

    def accept(self):
        """Save settings and close dialog"""
        try:
            self._save_settings()
            super().accept()
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "Save Error",
                f"Failed to save settings:\n{str(e)}"
            )
