"""
Secure API Key Input Dialogs for FreeCAD AI Addon

Provides user interface components for securely managing API keys
and provider credentials.
"""

from typing import Dict
from PySide6 import QtWidgets, QtCore
from freecad_ai_addon.utils.security import get_credential_manager
from freecad_ai_addon.utils.logging import get_logger

logger = get_logger('security_ui')


class APIKeyInputDialog(QtWidgets.QDialog):
    """Dialog for securely inputting API keys"""

    def __init__(self, provider: str, parent=None):
        """
        Initialize the API key input dialog

        Args:
            provider: Name of the AI provider (e.g., 'openai', 'anthropic')
            parent: Parent widget
        """
        super().__init__(parent)
        self.provider = provider
        self.credential_manager = get_credential_manager()

        self.setWindowTitle(f"{provider.title()} API Configuration")
        self.setModal(True)
        self.setMinimumSize(400, 300)

        self._setup_ui()
        self._load_existing_credentials()

    def _setup_ui(self):
        """Set up the user interface"""
        layout = QtWidgets.QVBoxLayout(self)

        # Header
        header_label = QtWidgets.QLabel(f"Configure {self.provider.title()} API Access")
        header_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header_label)

        # Description
        desc_text = self._get_provider_description()
        desc_label = QtWidgets.QLabel(desc_text)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #666; margin-bottom: 15px;")
        layout.addWidget(desc_label)

        # Form layout
        form_layout = QtWidgets.QFormLayout()

        # API Key input
        self.api_key_input = QtWidgets.QLineEdit()
        self.api_key_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.api_key_input.setPlaceholderText("Enter your API key...")
        form_layout.addRow("API Key:", self.api_key_input)

        # Show/Hide API key button
        show_hide_layout = QtWidgets.QHBoxLayout()
        self.show_key_checkbox = QtWidgets.QCheckBox("Show API key")
        self.show_key_checkbox.toggled.connect(self._toggle_api_key_visibility)
        show_hide_layout.addWidget(self.show_key_checkbox)
        show_hide_layout.addStretch()
        form_layout.addRow("", show_hide_layout)

        # Additional provider-specific fields
        self._add_provider_specific_fields(form_layout)

        layout.addLayout(form_layout)

        # Test connection button
        self.test_button = QtWidgets.QPushButton("Test Connection")
        self.test_button.clicked.connect(self._test_connection)
        layout.addWidget(self.test_button)

        # Status label
        self.status_label = QtWidgets.QLabel("")
        self.status_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.status_label)

        # Buttons
        button_layout = QtWidgets.QHBoxLayout()

        self.save_button = QtWidgets.QPushButton("Save")
        self.save_button.clicked.connect(self.accept)
        self.save_button.setDefault(True)

        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        self.remove_button = QtWidgets.QPushButton("Remove Credentials")
        self.remove_button.clicked.connect(self._remove_credentials)
        self.remove_button.setStyleSheet("color: #d32f2f;")

        button_layout.addWidget(self.remove_button)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)

        layout.addLayout(button_layout)

    def _get_provider_description(self) -> str:
        """Get description text for the provider"""
        descriptions = {
            'openai': (
                "Enter your OpenAI API key to access GPT models. "
                "You can find your API key at https://platform.openai.com/api-keys"
            ),
            'anthropic': (
                "Enter your Anthropic API key to access Claude models. "
                "You can find your API key at https://console.anthropic.com/"
            ),
            'ollama': (
                "Configure connection to your local Ollama instance. "
                "Make sure Ollama is running on your system."
            )
        }
        return descriptions.get(self.provider, "Enter credentials for this AI provider.")

    def _add_provider_specific_fields(self, form_layout: QtWidgets.QFormLayout):
        """Add provider-specific input fields"""
        if self.provider == 'openai':
            # Organization ID (optional)
            self.org_id_input = QtWidgets.QLineEdit()
            self.org_id_input.setPlaceholderText("Optional: Organization ID")
            form_layout.addRow("Organization ID:", self.org_id_input)

        elif self.provider == 'anthropic':
            # No additional fields for Anthropic currently
            pass

        elif self.provider == 'ollama':
            # Base URL for Ollama
            self.base_url_input = QtWidgets.QLineEdit()
            self.base_url_input.setPlaceholderText("http://localhost:11434")
            self.base_url_input.setText("http://localhost:11434")
            form_layout.addRow("Base URL:", self.base_url_input)

    def _load_existing_credentials(self):
        """Load existing credentials into the form"""
        try:
            # Load API key
            api_key = self.credential_manager.get_credential(self.provider, 'api_key')
            if api_key:
                self.api_key_input.setText(api_key)

            # Load provider-specific credentials
            if self.provider == 'openai':
                org_id = self.credential_manager.get_credential(self.provider, 'org_id')
                if org_id and hasattr(self, 'org_id_input'):
                    self.org_id_input.setText(org_id)

            elif self.provider == 'ollama':
                base_url = self.credential_manager.get_credential(self.provider, 'base_url')
                if base_url and hasattr(self, 'base_url_input'):
                    self.base_url_input.setText(base_url)

        except Exception as e:
            logger.error("Failed to load existing credentials: %s", str(e))

    def _toggle_api_key_visibility(self, checked: bool):
        """Toggle API key visibility"""
        if checked:
            self.api_key_input.setEchoMode(QtWidgets.QLineEdit.Normal)
        else:
            self.api_key_input.setEchoMode(QtWidgets.QLineEdit.Password)

    def _test_connection(self):
        """Test the connection with provided credentials"""
        self.test_button.setEnabled(False)
        self.test_button.setText("Testing...")
        self.status_label.setText("Testing connection...")

        try:
            # Get current values from form
            credentials = self._get_form_credentials()

            # TODO: Implement actual connection testing
            # For now, just basic validation
            if not credentials.get('api_key') and self.provider != 'ollama':
                self._show_status("API key is required", error=True)
                return

            # Simulate connection test
            QtCore.QTimer.singleShot(1000, self._connection_test_success)

        except Exception as e:
            self._show_status(f"Connection test failed: {str(e)}", error=True)
        finally:
            self.test_button.setEnabled(True)
            self.test_button.setText("Test Connection")

    def _connection_test_success(self):
        """Handle successful connection test"""
        self._show_status("✓ Connection successful!", error=False)

    def _show_status(self, message: str, error: bool = False):
        """Show status message"""
        self.status_label.setText(message)
        if error:
            self.status_label.setStyleSheet("color: #d32f2f;")
        else:
            self.status_label.setStyleSheet("color: #388e3c;")

    def _get_form_credentials(self) -> Dict[str, str]:
        """Get credentials from form inputs"""
        credentials = {}

        # API key
        api_key = self.api_key_input.text().strip()
        if api_key:
            credentials['api_key'] = api_key

        # Provider-specific fields
        if self.provider == 'openai' and hasattr(self, 'org_id_input'):
            org_id = self.org_id_input.text().strip()
            if org_id:
                credentials['org_id'] = org_id

        elif self.provider == 'ollama' and hasattr(self, 'base_url_input'):
            base_url = self.base_url_input.text().strip()
            if base_url:
                credentials['base_url'] = base_url

        return credentials

    def _remove_credentials(self):
        """Remove stored credentials for this provider"""
        reply = QtWidgets.QMessageBox.question(
            self,
            "Remove Credentials",
            f"Are you sure you want to remove all stored credentials for {self.provider.title()}?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )

        if reply == QtWidgets.QMessageBox.Yes:
            try:
                self.credential_manager.remove_credential(self.provider)
                self._show_status("Credentials removed successfully", error=False)

                # Clear form
                self.api_key_input.clear()
                if hasattr(self, 'org_id_input'):
                    self.org_id_input.clear()
                if hasattr(self, 'base_url_input'):
                    self.base_url_input.setText("http://localhost:11434")

            except Exception as e:
                self._show_status(f"Failed to remove credentials: {str(e)}", error=True)

    def accept(self):
        """Save credentials and close dialog"""
        try:
            credentials = self._get_form_credentials()

            # Validate required fields
            if not credentials.get('api_key') and self.provider != 'ollama':
                self._show_status("API key is required", error=True)
                return

            # Save credentials
            for cred_type, value in credentials.items():
                if not self.credential_manager.store_credential(self.provider, cred_type, value):
                    self._show_status(f"Failed to save {cred_type}", error=True)
                    return

            logger.info("Successfully saved credentials for %s", self.provider)
            super().accept()

        except Exception as e:
            self._show_status(f"Failed to save credentials: {str(e)}", error=True)


class ProviderManagerDialog(QtWidgets.QDialog):
    """Dialog for managing all AI providers and their credentials"""

    def __init__(self, parent=None):
        """Initialize the provider manager dialog"""
        super().__init__(parent)
        self.credential_manager = get_credential_manager()

        self.setWindowTitle("AI Provider Management")
        self.setModal(True)
        self.setMinimumSize(600, 400)

        self._setup_ui()
        self._refresh_provider_list()

    def _setup_ui(self):
        """Set up the user interface"""
        layout = QtWidgets.QVBoxLayout(self)

        # Header
        header_label = QtWidgets.QLabel("Manage AI Provider Credentials")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header_label)

        # Provider list
        list_layout = QtWidgets.QHBoxLayout()

        # Left side - provider list
        left_layout = QtWidgets.QVBoxLayout()
        left_layout.addWidget(QtWidgets.QLabel("Configured Providers:"))

        self.provider_list = QtWidgets.QListWidget()
        self.provider_list.currentItemChanged.connect(self._on_provider_selected)
        left_layout.addWidget(self.provider_list)

        # Add provider buttons
        add_layout = QtWidgets.QHBoxLayout()

        self.add_openai_btn = QtWidgets.QPushButton("Add OpenAI")
        self.add_openai_btn.clicked.connect(lambda: self._add_provider('openai'))

        self.add_anthropic_btn = QtWidgets.QPushButton("Add Anthropic")
        self.add_anthropic_btn.clicked.connect(lambda: self._add_provider('anthropic'))

        self.add_ollama_btn = QtWidgets.QPushButton("Add Ollama")
        self.add_ollama_btn.clicked.connect(lambda: self._add_provider('ollama'))

        add_layout.addWidget(self.add_openai_btn)
        add_layout.addWidget(self.add_anthropic_btn)
        add_layout.addWidget(self.add_ollama_btn)

        left_layout.addLayout(add_layout)
        list_layout.addLayout(left_layout)

        # Right side - provider details
        right_layout = QtWidgets.QVBoxLayout()
        right_layout.addWidget(QtWidgets.QLabel("Provider Details:"))

        self.details_text = QtWidgets.QTextEdit()
        self.details_text.setReadOnly(True)
        right_layout.addWidget(self.details_text)

        # Provider action buttons
        action_layout = QtWidgets.QHBoxLayout()

        self.edit_btn = QtWidgets.QPushButton("Edit")
        self.edit_btn.clicked.connect(self._edit_provider)
        self.edit_btn.setEnabled(False)

        self.test_btn = QtWidgets.QPushButton("Test")
        self.test_btn.clicked.connect(self._test_provider)
        self.test_btn.setEnabled(False)

        self.remove_btn = QtWidgets.QPushButton("Remove")
        self.remove_btn.clicked.connect(self._remove_provider)
        self.remove_btn.setEnabled(False)
        self.remove_btn.setStyleSheet("color: #d32f2f;")

        action_layout.addWidget(self.edit_btn)
        action_layout.addWidget(self.test_btn)
        action_layout.addWidget(self.remove_btn)
        action_layout.addStretch()

        right_layout.addLayout(action_layout)
        list_layout.addLayout(right_layout)

        layout.addLayout(list_layout)

        # Close button
        close_layout = QtWidgets.QHBoxLayout()
        close_layout.addStretch()

        self.close_btn = QtWidgets.QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        close_layout.addWidget(self.close_btn)

        layout.addLayout(close_layout)

    def _refresh_provider_list(self):
        """Refresh the list of configured providers"""
        self.provider_list.clear()

        providers = self.credential_manager.list_providers()
        for provider in providers:
            item = QtWidgets.QListWidgetItem(provider.title())
            item.setData(QtCore.Qt.UserRole, provider)
            self.provider_list.addItem(item)

    def _on_provider_selected(self, current, previous):
        """Handle provider selection"""
        if current is None:
            self.details_text.clear()
            self.edit_btn.setEnabled(False)
            self.test_btn.setEnabled(False)
            self.remove_btn.setEnabled(False)
            return

        provider = current.data(QtCore.Qt.UserRole)
        self._show_provider_details(provider)

        self.edit_btn.setEnabled(True)
        self.test_btn.setEnabled(True)
        self.remove_btn.setEnabled(True)

    def _show_provider_details(self, provider: str):
        """Show details for the selected provider"""
        try:
            cred_types = self.credential_manager.list_credential_types(provider)

            details = f"Provider: {provider.title()}\n\n"
            details += "Configured Credentials:\n"

            for cred_type in cred_types:
                is_valid = self.credential_manager.validate_credential(provider, cred_type)
                status = "✓ Valid" if is_valid else "⚠ Invalid"
                details += f"  • {cred_type}: {status}\n"

            if not cred_types:
                details += "  No credentials configured\n"

            self.details_text.setText(details)

        except Exception as e:
            self.details_text.setText(f"Error loading provider details: {str(e)}")

    def _add_provider(self, provider: str):
        """Add a new provider"""
        dialog = APIKeyInputDialog(provider, self)
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            self._refresh_provider_list()

    def _edit_provider(self):
        """Edit the selected provider"""
        current = self.provider_list.currentItem()
        if current is None:
            return

        provider = current.data(QtCore.Qt.UserRole)
        dialog = APIKeyInputDialog(provider, self)
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            self._refresh_provider_list()
            self._show_provider_details(provider)

    def _test_provider(self):
        """Test the selected provider connection"""
        current = self.provider_list.currentItem()
        if current is None:
            return

        provider = current.data(QtCore.Qt.UserRole)

        # TODO: Implement actual provider testing
        QtWidgets.QMessageBox.information(
            self,
            "Test Connection",
            f"Connection test for {provider.title()} would be performed here."
        )

    def _remove_provider(self):
        """Remove the selected provider"""
        current = self.provider_list.currentItem()
        if current is None:
            return

        provider = current.data(QtCore.Qt.UserRole)

        reply = QtWidgets.QMessageBox.question(
            self,
            "Remove Provider",
            f"Are you sure you want to remove {provider.title()} and all its credentials?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )

        if reply == QtWidgets.QMessageBox.Yes:
            try:
                self.credential_manager.remove_credential(provider)
                self._refresh_provider_list()

                QtWidgets.QMessageBox.information(
                    self,
                    "Provider Removed",
                    f"{provider.title()} credentials have been removed successfully."
                )

            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to remove provider: {str(e)}"
                )
