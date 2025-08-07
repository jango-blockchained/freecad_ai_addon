"""
Tests for Provider Management System (Phase 3)

Tests the complete provider management system including secure storage,
UI components, and connection management.
"""

import tempfile
import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from freecad_ai_addon.utils.security import CredentialManager
from freecad_ai_addon.core.provider_status import ProviderMonitor, ProviderStatus
from freecad_ai_addon.core.connection_manager import ConnectionManager, ConnectionConfig


class TestProviderManagementSystem:
    """Test cases for the complete provider management system"""

    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.credential_manager = CredentialManager(config_dir=self.temp_dir)
        self.provider_monitor = ProviderMonitor()
        self.connection_manager = ConnectionManager()

    def teardown_method(self):
        """Clean up test environment"""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_credential_storage_integration(self):
        """Test credential storage with multiple providers"""
        # Store credentials for multiple providers
        providers = [
            ("openai", "api_key", "sk-test-openai-key"),
            ("anthropic", "api_key", "sk-ant-test-key"),
            ("ollama", "base_url", "http://localhost:11434"),
        ]

        for provider, cred_type, value in providers:
            assert self.credential_manager.store_credential(provider, cred_type, value)

        # Verify all stored
        stored_providers = self.credential_manager.list_providers()
        assert "openai" in stored_providers
        assert "anthropic" in stored_providers
        assert "ollama" in stored_providers

        # Test credential validation
        assert self.credential_manager.validate_credential("openai", "api_key")
        assert self.credential_manager.validate_credential("anthropic", "api_key")
        assert self.credential_manager.validate_credential("ollama", "base_url")

    @pytest.mark.asyncio
    async def test_provider_status_monitoring(self):
        """Test provider status monitoring"""
        # Mock HTTP responses for testing
        with patch("httpx.AsyncClient") as mock_client:
            # Mock successful OpenAI response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"data": [{"id": "gpt-3.5-turbo"}]}
            mock_response.headers = {"x-ratelimit-remaining-requests": "100"}

            mock_client.return_value.__aenter__.return_value.get.return_value = (
                mock_response
            )

            # Store test credentials
            self.credential_manager.store_credential(
                "openai", "api_key", "sk-test-key-12345678901234567890"
            )

            # Test connection
            health = await self.provider_monitor.check_provider_connection("openai")

            assert health.status == ProviderStatus.CONNECTED
            assert health.response_time is not None
            assert health.error_message is None

    @pytest.mark.asyncio
    async def test_connection_manager_retry_logic(self):
        """Test connection manager retry logic"""
        config = ConnectionConfig(
            retry_attempts=2, retry_delay=0.1, retry_backoff=1.5  # Fast for testing
        )

        connection_manager = ConnectionManager(config)

        # Mock a failing then succeeding connection
        call_count = 0

        async def mock_check_connection(provider):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                # First call fails
                from freecad_ai_addon.core.provider_status import (
                    ProviderHealth,
                    ProviderStatus,
                )

                return ProviderHealth(
                    status=ProviderStatus.ERROR,
                    last_check=0,
                    response_time=None,
                    error_message="Connection failed",
                    rate_limit_remaining=None,
                    rate_limit_reset=None,
                    usage_stats={},
                )
            else:
                # Second call succeeds
                return ProviderHealth(
                    status=ProviderStatus.CONNECTED,
                    last_check=0,
                    response_time=100,
                    error_message=None,
                    rate_limit_remaining=1000,
                    rate_limit_reset=None,
                    usage_stats={},
                )

        with patch.object(
            connection_manager.provider_monitor,
            "check_provider_connection",
            side_effect=mock_check_connection,
        ):
            # Store test credentials
            self.credential_manager.store_credential(
                "openai", "api_key", "sk-test-key-12345678901234567890"
            )

            # Test connection with retry
            success = await connection_manager.connect_provider("openai")

            assert success
            assert call_count == 2  # Should have retried once
            assert connection_manager.is_connected("openai")

    @pytest.mark.asyncio
    async def test_connection_manager_fallback(self):
        """Test connection manager fallback functionality"""
        config = ConnectionConfig(
            enable_fallback=True,
            fallback_order=["anthropic", "ollama"],
            retry_attempts=1,
        )

        connection_manager = ConnectionManager(config)

        # Mock all OpenAI calls to fail, Anthropic to succeed
        async def mock_check_connection(provider):
            from freecad_ai_addon.core.provider_status import (
                ProviderHealth,
                ProviderStatus,
            )

            if provider == "openai":
                return ProviderHealth(
                    status=ProviderStatus.ERROR,
                    last_check=0,
                    response_time=None,
                    error_message="OpenAI down",
                    rate_limit_remaining=None,
                    rate_limit_reset=None,
                    usage_stats={},
                )
            elif provider == "anthropic":
                return ProviderHealth(
                    status=ProviderStatus.CONNECTED,
                    last_check=0,
                    response_time=150,
                    error_message=None,
                    rate_limit_remaining=500,
                    rate_limit_reset=None,
                    usage_stats={},
                )

        with patch.object(
            connection_manager.provider_monitor,
            "check_provider_connection",
            side_effect=mock_check_connection,
        ):
            # Store credentials for both providers
            self.credential_manager.store_credential(
                "openai", "api_key", "sk-test-key-12345678901234567890"
            )
            self.credential_manager.store_credential(
                "anthropic", "api_key", "sk-ant-test-key-12345678901234567890"
            )

            # Try to connect to OpenAI (should fail and fallback to Anthropic)
            await connection_manager.connect_provider("openai")

            # OpenAI should be disconnected, but Anthropic should be connected due to fallback
            assert not connection_manager.is_connected("openai")
            assert connection_manager.is_connected("anthropic")

    def test_connection_config_persistence(self):
        """Test connection configuration persistence"""
        from freecad_ai_addon.utils.config import ConfigManager

        config_manager = ConfigManager()

        # Set connection configuration
        config_manager.set("connection.retry_attempts", 5)
        config_manager.set("connection.retry_delay", 10.0)
        config_manager.set("connection.enable_fallback", False)
        config_manager.set("connection.fallback_order", ["anthropic", "ollama"])

        # Verify persistence
        assert config_manager.get("connection.retry_attempts") == 5
        assert config_manager.get("connection.retry_delay") == 10.0
        assert config_manager.get("connection.enable_fallback") is False
        assert config_manager.get("connection.fallback_order") == [
            "anthropic",
            "ollama",
        ]

    def test_credential_backup_restore(self):
        """Test credential backup and restore functionality"""
        # Store some test credentials
        test_credentials = [
            ("openai", "api_key", "sk-openai-test-key"),
            ("openai", "org_id", "org-test123"),
            ("anthropic", "api_key", "sk-ant-test-key"),
            ("ollama", "base_url", "http://localhost:11434"),
        ]

        for provider, cred_type, value in test_credentials:
            self.credential_manager.store_credential(provider, cred_type, value)

        # Export credentials
        backup_file = self.temp_dir / "backup.enc"
        assert self.credential_manager.export_credentials(str(backup_file))
        assert backup_file.exists()

        # Clear current credentials
        for provider, _, _ in test_credentials:
            self.credential_manager.remove_credential(provider)

        assert len(self.credential_manager.list_providers()) == 0

        # Import credentials
        assert self.credential_manager.import_credentials(str(backup_file))

        # Verify all credentials restored
        for provider, cred_type, value in test_credentials:
            restored_value = self.credential_manager.get_credential(provider, cred_type)
            assert restored_value == value

    @pytest.mark.asyncio
    async def test_provider_status_callbacks(self):
        """Test provider status callback system"""
        callback_events = []

        def status_callback(health):
            callback_events.append(health.status)

        # Register callback
        self.provider_monitor.register_status_callback("openai", status_callback)

        # Mock a status check
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"data": []}
            mock_response.headers = {}

            mock_client.return_value.__aenter__.return_value.get.return_value = (
                mock_response
            )

            # Store test credentials
            self.credential_manager.store_credential(
                "openai", "api_key", "sk-test-key-12345678901234567890"
            )

            # Trigger status check
            await self.provider_monitor.check_provider_connection("openai")

        # Verify callback was called
        assert len(callback_events) > 0
        assert ProviderStatus.CONNECTED in callback_events

        # Unregister callback
        self.provider_monitor.unregister_status_callback("openai", status_callback)

    def test_integration_provider_lifecycle(self):
        """Test complete provider lifecycle"""
        provider = "openai"

        # 1. Add provider credentials
        assert self.credential_manager.store_credential(
            provider, "api_key", "sk-test-key-12345678901234567890"
        )
        assert self.credential_manager.store_credential(
            provider, "org_id", "org-test123"
        )

        # 2. Validate credentials
        assert self.credential_manager.validate_credential(provider, "api_key")
        assert self.credential_manager.validate_credential(provider, "org_id")

        # 3. Check provider exists
        assert provider in self.credential_manager.list_providers()
        cred_types = self.credential_manager.list_credential_types(provider)
        assert "api_key" in cred_types
        assert "org_id" in cred_types

        # 4. Remove specific credential
        assert self.credential_manager.remove_credential(provider, "org_id")
        assert "org_id" not in self.credential_manager.list_credential_types(provider)
        assert "api_key" in self.credential_manager.list_credential_types(provider)

        # 5. Remove all credentials for provider
        assert self.credential_manager.remove_credential(provider)
        assert provider not in self.credential_manager.list_providers()


if __name__ == "__main__":
    pytest.main([__file__])
