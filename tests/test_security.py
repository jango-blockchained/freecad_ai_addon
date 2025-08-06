"""
Tests for secure credential storage functionality
"""

import tempfile
import pytest
from pathlib import Path
from freecad_ai_addon.utils.security import CredentialManager


class TestCredentialManager:
    """Test cases for CredentialManager"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.manager = CredentialManager(config_dir=self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_store_and_retrieve_credential(self):
        """Test basic credential storage and retrieval"""
        provider = "openai"
        cred_type = "api_key"
        value = "sk-test123456789"
        
        # Store credential
        assert self.manager.store_credential(provider, cred_type, value)
        
        # Retrieve credential
        retrieved = self.manager.get_credential(provider, cred_type)
        assert retrieved == value
    
    def test_credential_not_found(self):
        """Test retrieving non-existent credential"""
        result = self.manager.get_credential("nonexistent", "api_key")
        assert result is None
    
    def test_remove_credential(self):
        """Test credential removal"""
        provider = "anthropic"
        cred_type = "api_key"
        value = "sk-ant-test123"
        
        # Store and verify
        self.manager.store_credential(provider, cred_type, value)
        assert self.manager.get_credential(provider, cred_type) == value
        
        # Remove and verify
        assert self.manager.remove_credential(provider, cred_type)
        assert self.manager.get_credential(provider, cred_type) is None
    
    def test_list_providers(self):
        """Test provider listing"""
        # Initially empty
        assert self.manager.list_providers() == []
        
        # Add some credentials
        self.manager.store_credential("openai", "api_key", "test1")
        self.manager.store_credential("anthropic", "api_key", "test2")
        
        providers = self.manager.list_providers()
        assert "openai" in providers
        assert "anthropic" in providers
        assert len(providers) == 2
    
    def test_list_credential_types(self):
        """Test credential type listing"""
        provider = "openai"
        
        # Initially empty
        assert self.manager.list_credential_types(provider) == []
        
        # Add credentials
        self.manager.store_credential(provider, "api_key", "test1")
        self.manager.store_credential(provider, "org_id", "test2")
        
        cred_types = self.manager.list_credential_types(provider)
        assert "api_key" in cred_types
        assert "org_id" in cred_types
        assert len(cred_types) == 2
    
    def test_validate_credential(self):
        """Test credential validation"""
        provider = "openai"
        
        # Valid API key
        valid_key = "sk-test123456789012345678901234567890"
        self.manager.store_credential(provider, "api_key", valid_key)
        assert self.manager.validate_credential(provider, "api_key")
        
        # Invalid (too short) API key
        invalid_key = "short"
        self.manager.store_credential(provider, "api_key", invalid_key)
        assert not self.manager.validate_credential(provider, "api_key")
        
        # Non-existent credential
        assert not self.manager.validate_credential("nonexistent", "api_key")
    
    def test_encryption_persistence(self):
        """Test that credentials survive manager recreation"""
        provider = "test_provider"
        cred_type = "api_key"
        value = "test_value_123456789"
        
        # Store with first manager
        self.manager.store_credential(provider, cred_type, value)
        
        # Create new manager with same config dir
        new_manager = CredentialManager(config_dir=self.temp_dir)
        
        # Should be able to retrieve with new manager
        retrieved = new_manager.get_credential(provider, cred_type)
        assert retrieved == value
    
    def test_export_import_credentials(self):
        """Test credential backup and restore"""
        # Store some test credentials
        self.manager.store_credential("openai", "api_key", "test_openai_key")
        self.manager.store_credential("anthropic", "api_key", "test_anthropic_key")
        
        # Export credentials
        export_file = self.temp_dir / "backup.enc"
        assert self.manager.export_credentials(str(export_file))
        
        # Clear current credentials
        self.manager.remove_credential("openai")
        self.manager.remove_credential("anthropic")
        assert self.manager.list_providers() == []
        
        # Import credentials
        assert self.manager.import_credentials(str(export_file))
        
        # Verify restored
        assert self.manager.get_credential("openai", "api_key") == "test_openai_key"
        assert self.manager.get_credential("anthropic", "api_key") == "test_anthropic_key"


if __name__ == "__main__":
    pytest.main([__file__])
