"""
Enhanced Provider Configuration UI with Real-time Status

Advanced provider management interface with status monitoring,
connection testing, and usage statistics.
"""

import asyncio
from typing import Optional, Dict
from PySide6 import QtWidgets, QtCore

from freecad_ai_addon.ui.security_dialogs import APIKeyInputDialog
from freecad_ai_addon.core.provider_status import (
    get_provider_monitor,
    ProviderStatus,
    ProviderHealth,
)
from freecad_ai_addon.utils.security import get_credential_manager
from freecad_ai_addon.utils.logging import get_logger

logger = get_logger("provider_ui")


class ProviderStatusWidget(QtWidgets.QWidget):
    """Widget showing real-time provider status"""

    def __init__(self, provider: str, parent=None):
        """Initialize provider status widget"""
        super().__init__(parent)
        self.provider = provider
        self.monitor = get_provider_monitor()
        self.current_health: Optional[ProviderHealth] = None

        self._setup_ui()
        self._register_callbacks()
        self._update_status()

    def _setup_ui(self):
        """Set up the user interface"""
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Provider name
        self.name_label = QtWidgets.QLabel(self.provider.title())
        self.name_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.name_label)

        # Status indicator
        self.status_indicator = QtWidgets.QLabel("●")
        self.status_indicator.setAlignment(QtCore.Qt.AlignCenter)
        self.status_indicator.setFixedSize(20, 20)
        layout.addWidget(self.status_indicator)

        # Status text
        self.status_label = QtWidgets.QLabel("Unknown")
        layout.addWidget(self.status_label)

        # Response time
        self.response_label = QtWidgets.QLabel("")
        self.response_label.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(self.response_label)

        layout.addStretch()

        # Actions
        self.test_button = QtWidgets.QPushButton("Test")
        self.test_button.setMaximumSize(60, 25)
        self.test_button.clicked.connect(self._test_connection)
        layout.addWidget(self.test_button)

        self.edit_button = QtWidgets.QPushButton("Edit")
        self.edit_button.setMaximumSize(60, 25)
        self.edit_button.clicked.connect(self._edit_provider)
        layout.addWidget(self.edit_button)

    def _register_callbacks(self):
        """Register for status updates"""
        self.monitor.register_status_callback(self.provider, self._on_status_update)

    def _on_status_update(self, health: ProviderHealth):
        """Handle status updates from monitor"""
        self.current_health = health
        QtCore.QMetaObject.invokeMethod(
            self, "_update_status", QtCore.Qt.QueuedConnection
        )

    @QtCore.Slot()
    def _update_status(self):
        """Update UI based on current health status"""
        if not self.current_health:
            health = self.monitor.get_provider_status(self.provider)
        else:
            health = self.current_health

        # Update status indicator color
        status_colors = {
            ProviderStatus.CONNECTED: "#4CAF50",  # Green
            ProviderStatus.CONNECTING: "#FF9800",  # Orange
            ProviderStatus.DISCONNECTED: "#9E9E9E",  # Gray
            ProviderStatus.ERROR: "#F44336",  # Red
            ProviderStatus.RATE_LIMITED: "#FF5722",  # Deep Orange
            ProviderStatus.EXPIRED: "#E91E63",  # Pink
            ProviderStatus.UNKNOWN: "#607D8B",  # Blue Gray
        }

        color = status_colors.get(health.status, "#607D8B")
        self.status_indicator.setStyleSheet(f"color: {color}; font-size: 16px;")

        # Update status text
        status_text = health.status.value.replace("_", " ").title()
        self.status_label.setText(status_text)

        # Update response time
        if health.response_time is not None:
            response_text = f"{health.response_time:.0f}ms"
            if health.rate_limit_remaining is not None:
                response_text += f" ({health.rate_limit_remaining} req)"
            self.response_label.setText(response_text)
        else:
            self.response_label.setText("")

        # Update tooltip with detailed info
        tooltip_parts = [f"Status: {status_text}"]
        if health.error_message:
            tooltip_parts.append(f"Error: {health.error_message}")
        if health.response_time is not None:
            tooltip_parts.append(f"Response time: {health.response_time:.2f}ms")
        if health.rate_limit_remaining is not None:
            tooltip_parts.append(f"Rate limit remaining: {health.rate_limit_remaining}")
        if health.usage_stats:
            for key, value in health.usage_stats.items():
                tooltip_parts.append(f"{key.replace('_', ' ').title()}: {value}")

        self.setToolTip("\n".join(tooltip_parts))

    @QtCore.Slot()
    def _test_connection(self):
        """Test connection to this provider"""
        self.test_button.setEnabled(False)
        self.test_button.setText("...")

        async def test_async():
            try:
                await self.monitor.check_provider_connection(self.provider)
            finally:
                QtCore.QMetaObject.invokeMethod(
                    self, "_test_complete", QtCore.Qt.QueuedConnection
                )

        # Run in event loop
        asyncio.create_task(test_async())

    @QtCore.Slot()
    def _test_complete(self):
        """Re-enable test button after test completes"""
        self.test_button.setEnabled(True)
        self.test_button.setText("Test")

    @QtCore.Slot()
    def _edit_provider(self):
        """Open edit dialog for this provider"""
        dialog = APIKeyInputDialog(self.provider, self)
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            # Trigger a status check after editing
            asyncio.create_task(self.monitor.check_provider_connection(self.provider))

    def cleanup(self):
        """Clean up resources"""
        self.monitor.unregister_status_callback(self.provider, self._on_status_update)


class EnhancedProviderManagerDialog(QtWidgets.QDialog):
    """Enhanced provider management dialog with real-time monitoring"""

    def __init__(self, parent=None):
        """Initialize the enhanced provider manager dialog"""
        super().__init__(parent)
        self.credential_manager = get_credential_manager()
        self.monitor = get_provider_monitor()
        self.provider_widgets: Dict[str, ProviderStatusWidget] = {}

        self.setWindowTitle("AI Provider Management")
        self.setModal(True)
        self.setMinimumSize(800, 600)

        self._setup_ui()
        self._refresh_providers()
        self._start_monitoring()

    def _setup_ui(self):
        """Set up the user interface"""
        layout = QtWidgets.QVBoxLayout(self)

        # Header
        header_layout = QtWidgets.QHBoxLayout()

        header_label = QtWidgets.QLabel("AI Provider Management")
        header_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(header_label)

        header_layout.addStretch()

        # Auto-refresh toggle
        self.auto_refresh_checkbox = QtWidgets.QCheckBox("Auto-refresh")
        self.auto_refresh_checkbox.setChecked(True)
        self.auto_refresh_checkbox.toggled.connect(self._toggle_auto_refresh)
        header_layout.addWidget(self.auto_refresh_checkbox)

        # Refresh button
        self.refresh_button = QtWidgets.QPushButton("Refresh All")
        self.refresh_button.clicked.connect(self._refresh_all_providers)
        header_layout.addWidget(self.refresh_button)

        layout.addLayout(header_layout)

        # Provider list
        providers_group = QtWidgets.QGroupBox("Configured Providers")
        providers_layout = QtWidgets.QVBoxLayout(providers_group)

        # Scroll area for providers
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(200)

        self.providers_widget = QtWidgets.QWidget()
        self.providers_layout = QtWidgets.QVBoxLayout(self.providers_widget)
        self.providers_layout.addStretch()

        scroll_area.setWidget(self.providers_widget)
        providers_layout.addWidget(scroll_area)

        layout.addWidget(providers_group)

        # Add provider section
        add_group = QtWidgets.QGroupBox("Add New Provider")
        add_layout = QtWidgets.QHBoxLayout(add_group)

        self.add_openai_btn = QtWidgets.QPushButton("Add OpenAI")
        self.add_openai_btn.clicked.connect(lambda: self._add_provider("openai"))
        add_layout.addWidget(self.add_openai_btn)

        self.add_anthropic_btn = QtWidgets.QPushButton("Add Anthropic")
        self.add_anthropic_btn.clicked.connect(lambda: self._add_provider("anthropic"))
        add_layout.addWidget(self.add_anthropic_btn)

        self.add_ollama_btn = QtWidgets.QPushButton("Add Ollama")
        self.add_ollama_btn.clicked.connect(lambda: self._add_provider("ollama"))
        add_layout.addWidget(self.add_ollama_btn)

        add_layout.addStretch()

        layout.addWidget(add_group)

        # Status information
        status_group = QtWidgets.QGroupBox("System Status")
        status_layout = QtWidgets.QVBoxLayout(status_group)

        self.status_text = QtWidgets.QTextEdit()
        self.status_text.setMaximumHeight(100)
        self.status_text.setReadOnly(True)
        status_layout.addWidget(self.status_text)

        layout.addWidget(status_group)

        # Buttons
        button_layout = QtWidgets.QHBoxLayout()

        self.backup_button = QtWidgets.QPushButton("Backup Credentials")
        self.backup_button.clicked.connect(self._backup_credentials)
        button_layout.addWidget(self.backup_button)

        self.restore_button = QtWidgets.QPushButton("Restore Credentials")
        self.restore_button.clicked.connect(self._restore_credentials)
        button_layout.addWidget(self.restore_button)

        button_layout.addStretch()

        self.close_button = QtWidgets.QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

    def _refresh_providers(self):
        """Refresh the provider list"""
        # Clear existing widgets
        for widget in self.provider_widgets.values():
            widget.cleanup()
            widget.setParent(None)
        self.provider_widgets.clear()

        # Add provider widgets
        providers = self.credential_manager.list_providers()
        for provider in providers:
            widget = ProviderStatusWidget(provider, self)
            self.provider_widgets[provider] = widget
            self.providers_layout.insertWidget(
                self.providers_layout.count() - 1, widget
            )

        self._update_status_text()

    def _update_status_text(self):
        """Update the status text area"""
        status_lines = []

        if not self.provider_widgets:
            status_lines.append("No providers configured.")
        else:
            status_lines.append(f"Total providers: {len(self.provider_widgets)}")

            # Count by status
            status_counts = {}
            for widget in self.provider_widgets.values():
                health = self.monitor.get_provider_status(widget.provider)
                status = health.status.value
                status_counts[status] = status_counts.get(status, 0) + 1

            for status, count in status_counts.items():
                status_lines.append(f"  {status.replace('_', ' ').title()}: {count}")

        # Monitoring status
        status_lines.append("")
        if self.auto_refresh_checkbox.isChecked():
            status_lines.append("Auto-refresh: Enabled")
        else:
            status_lines.append("Auto-refresh: Disabled")

        self.status_text.setText("\n".join(status_lines))

    def _add_provider(self, provider: str):
        """Add a new provider"""
        dialog = APIKeyInputDialog(provider, self)
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            self._refresh_providers()
            # Test the new provider
            asyncio.create_task(self.monitor.check_provider_connection(provider))

    @QtCore.Slot()
    def _refresh_all_providers(self):
        """Refresh all provider statuses"""
        self.refresh_button.setEnabled(False)
        self.refresh_button.setText("Refreshing...")

        async def refresh_async():
            try:
                providers = list(self.provider_widgets.keys())
                tasks = [
                    self.monitor.check_provider_connection(provider)
                    for provider in providers
                ]
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)
            finally:
                QtCore.QMetaObject.invokeMethod(
                    self, "_refresh_complete", QtCore.Qt.QueuedConnection
                )

        asyncio.create_task(refresh_async())

    @QtCore.Slot()
    def _refresh_complete(self):
        """Re-enable refresh button after refresh completes"""
        self.refresh_button.setEnabled(True)
        self.refresh_button.setText("Refresh All")
        self._update_status_text()

    @QtCore.Slot(bool)
    def _toggle_auto_refresh(self, enabled: bool):
        """Toggle auto-refresh monitoring"""
        if enabled:
            self._start_monitoring()
        else:
            self._stop_monitoring()

    def _start_monitoring(self):
        """Start provider monitoring"""
        asyncio.create_task(self.monitor.start_monitoring(interval=30.0))
        logger.info("Started provider monitoring")

    def _stop_monitoring(self):
        """Stop provider monitoring"""
        asyncio.create_task(self.monitor.stop_monitoring())
        logger.info("Stopped provider monitoring")

    @QtCore.Slot()
    def _backup_credentials(self):
        """Backup credentials to file"""
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Backup Credentials",
            "ai_addon_credentials_backup.enc",
            "Encrypted Files (*.enc);;All Files (*)",
        )

        if file_path:
            try:
                if self.credential_manager.export_credentials(file_path):
                    QtWidgets.QMessageBox.information(
                        self,
                        "Backup Successful",
                        f"Credentials backed up to:\n{file_path}",
                    )
                else:
                    QtWidgets.QMessageBox.warning(
                        self,
                        "Backup Failed",
                        "Failed to backup credentials. Check the logs for details.",
                    )
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self, "Backup Error", f"An error occurred during backup:\n{str(e)}"
                )

    @QtCore.Slot()
    def _restore_credentials(self):
        """Restore credentials from backup file"""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Restore Credentials", "", "Encrypted Files (*.enc);;All Files (*)"
        )

        if file_path:
            reply = QtWidgets.QMessageBox.question(
                self,
                "Restore Credentials",
                "This will merge the backup with your current credentials.\n"
                "Existing credentials will not be overwritten.\n\n"
                "Continue with restore?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.No,
            )

            if reply == QtWidgets.QMessageBox.Yes:
                try:
                    if self.credential_manager.import_credentials(
                        file_path, overwrite=False
                    ):
                        QtWidgets.QMessageBox.information(
                            self,
                            "Restore Successful",
                            "Credentials restored successfully!",
                        )
                        self._refresh_providers()
                    else:
                        QtWidgets.QMessageBox.warning(
                            self,
                            "Restore Failed",
                            "Failed to restore credentials. Check the logs for details.",
                        )
                except Exception as e:
                    QtWidgets.QMessageBox.critical(
                        self,
                        "Restore Error",
                        f"An error occurred during restore:\n{str(e)}",
                    )

    def closeEvent(self, event):
        """Handle dialog close event"""
        # Clean up provider widgets
        for widget in self.provider_widgets.values():
            widget.cleanup()

        # Stop monitoring if it was started
        asyncio.create_task(self.monitor.stop_monitoring())

        super().closeEvent(event)
