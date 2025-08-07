"""
AI Provider Manager for FreeCAD AI Addon

Manages multiple AI providers (OpenAI, Anthropic, local models) with secure
credential storage and provider abstraction.
"""

import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod
from enum import Enum

from freecad_ai_addon.utils.logging import get_logger
from freecad_ai_addon.utils.config import ConfigManager

logger = get_logger("provider_manager")


class ProviderType(Enum):
    """Enumeration of supported AI provider types"""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL_OLLAMA = "local_ollama"
    MCP_SERVER = "mcp_server"


class MessageRole(Enum):
    """Enumeration of message roles"""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class ChatMessage:
    """Represents a chat message"""

    role: MessageRole
    content: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ProviderCapabilities:
    """Represents capabilities of an AI provider"""

    supports_chat: bool = True
    supports_streaming: bool = False
    supports_tools: bool = False
    supports_images: bool = False
    max_tokens: Optional[int] = None
    context_length: Optional[int] = None
    models: List[str] = None

    def __post_init__(self):
        if self.models is None:
            self.models = []


@dataclass
class ProviderConfig:
    """Configuration for an AI provider"""

    name: str
    provider_type: ProviderType
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = None
    enabled: bool = True
    settings: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.settings is None:
            self.settings = {}


class AIProvider(ABC):
    """Abstract base class for AI providers"""

    def __init__(self, config: ProviderConfig):
        self.config = config
        self.capabilities = ProviderCapabilities()

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the provider"""
        pass

    @abstractmethod
    async def chat(
        self,
        messages: List[ChatMessage],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs,
    ) -> str:
        """Send a chat request and get response"""
        pass

    @abstractmethod
    async def test_connection(self) -> bool:
        """Test if the provider connection is working"""
        pass

    @abstractmethod
    async def get_models(self) -> List[str]:
        """Get list of available models"""
        pass

    async def cleanup(self) -> None:
        """Clean up provider resources"""
        pass


class OpenAIProvider(AIProvider):
    """OpenAI provider implementation"""

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.client = None
        self.capabilities = ProviderCapabilities(
            supports_chat=True,
            supports_streaming=True,
            supports_tools=True,
            supports_images=True,
            max_tokens=4096,
            context_length=128000,
            models=["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
        )

    async def initialize(self) -> None:
        """Initialize OpenAI client"""
        try:
            # Import here to avoid dependency issues if not installed
            import openai

            self.client = openai.AsyncOpenAI(
                api_key=self.config.api_key, base_url=self.config.base_url
            )

            logger.info("OpenAI provider initialized for %s", self.config.name)
        except ImportError:
            logger.error("OpenAI library not installed")
            raise
        except Exception as e:
            logger.error("Failed to initialize OpenAI provider: %s", str(e))
            raise

    async def chat(
        self,
        messages: List[ChatMessage],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs,
    ) -> str:
        """Send chat request to OpenAI"""
        if not self.client:
            raise RuntimeError("Provider not initialized")

        try:
            # Convert messages to OpenAI format
            openai_messages = [
                {"role": msg.role.value, "content": msg.content} for msg in messages
            ]

            response = await self.client.chat.completions.create(
                model=model or self.config.model or "gpt-3.5-turbo",
                messages=openai_messages,
                max_tokens=max_tokens or self.capabilities.max_tokens,
                temperature=temperature or 0.7,
                **kwargs,
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error("OpenAI chat request failed: %s", str(e))
            raise

    async def test_connection(self) -> bool:
        """Test OpenAI connection"""
        try:
            await self.chat([ChatMessage(MessageRole.USER, "Hello")])
            return True
        except Exception as e:
            logger.error("OpenAI connection test failed: %s", str(e))
            return False

    async def get_models(self) -> List[str]:
        """Get available OpenAI models"""
        if not self.client:
            return self.capabilities.models

        try:
            models = await self.client.models.list()
            return [model.id for model in models.data]
        except Exception as e:
            logger.error("Failed to get OpenAI models: %s", str(e))
            return self.capabilities.models


class AnthropicProvider(AIProvider):
    """Anthropic (Claude) provider implementation"""

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.client = None
        self.capabilities = ProviderCapabilities(
            supports_chat=True,
            supports_streaming=True,
            supports_tools=True,
            supports_images=True,
            max_tokens=4096,
            context_length=200000,
            models=[
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307",
            ],
        )

    async def initialize(self) -> None:
        """Initialize Anthropic client"""
        try:
            import anthropic

            self.client = anthropic.AsyncAnthropic(
                api_key=self.config.api_key, base_url=self.config.base_url
            )

            logger.info("Anthropic provider initialized for %s", self.config.name)
        except ImportError:
            logger.error("Anthropic library not installed")
            raise
        except Exception as e:
            logger.error("Failed to initialize Anthropic provider: %s", str(e))
            raise

    async def chat(
        self,
        messages: List[ChatMessage],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs,
    ) -> str:
        """Send chat request to Anthropic"""
        if not self.client:
            raise RuntimeError("Provider not initialized")

        try:
            # Convert messages to Anthropic format
            anthropic_messages = []
            system_message = None

            for msg in messages:
                if msg.role == MessageRole.SYSTEM:
                    system_message = msg.content
                else:
                    anthropic_messages.append(
                        {"role": msg.role.value, "content": msg.content}
                    )

            response = await self.client.messages.create(
                model=model or self.config.model or "claude-3-sonnet-20240229",
                messages=anthropic_messages,
                max_tokens=max_tokens or self.capabilities.max_tokens,
                temperature=temperature or 0.7,
                system=system_message,
                **kwargs,
            )

            return response.content[0].text

        except Exception as e:
            logger.error("Anthropic chat request failed: %s", str(e))
            raise

    async def test_connection(self) -> bool:
        """Test Anthropic connection"""
        try:
            await self.chat([ChatMessage(MessageRole.USER, "Hello")])
            return True
        except Exception as e:
            logger.error("Anthropic connection test failed: %s", str(e))
            return False

    async def get_models(self) -> List[str]:
        """Get available Anthropic models"""
        # Anthropic doesn't have a models endpoint, return known models
        return self.capabilities.models


class LocalOllamaProvider(AIProvider):
    """Local Ollama provider implementation"""

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.base_url = config.base_url or "http://localhost:11434"
        self.capabilities = ProviderCapabilities(
            supports_chat=True,
            supports_streaming=True,
            supports_tools=False,
            supports_images=False,
            max_tokens=2048,
            context_length=4096,
            models=[],  # Will be populated dynamically
        )

    async def initialize(self) -> None:
        """Initialize Ollama connection"""
        try:
            import httpx

            self.client = httpx.AsyncClient(base_url=self.base_url)

            # Test connection and get models
            self.capabilities.models = await self.get_models()

            logger.info("Ollama provider initialized for %s", self.config.name)
        except ImportError:
            logger.error("httpx library not installed")
            raise
        except Exception as e:
            logger.error("Failed to initialize Ollama provider: %s", str(e))
            raise

    async def chat(
        self,
        messages: List[ChatMessage],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs,
    ) -> str:
        """Send chat request to Ollama"""
        if not self.client:
            raise RuntimeError("Provider not initialized")

        try:
            # Convert to single prompt for Ollama
            prompt = "\n".join([f"{msg.role.value}: {msg.content}" for msg in messages])

            response = await self.client.post(
                "/api/generate",
                json={
                    "model": model or self.config.model or "llama2",
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens or self.capabilities.max_tokens,
                        "temperature": temperature or 0.7,
                    },
                },
            )

            response.raise_for_status()
            result = response.json()
            return result.get("response", "")

        except Exception as e:
            logger.error("Ollama chat request failed: %s", str(e))
            raise

    async def test_connection(self) -> bool:
        """Test Ollama connection"""
        try:
            if not self.client:
                return False

            response = await self.client.get("/api/tags")
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error("Ollama connection test failed: %s", str(e))
            return False

    async def get_models(self) -> List[str]:
        """Get available Ollama models"""
        try:
            if not self.client:
                return []

            response = await self.client.get("/api/tags")
            response.raise_for_status()

            data = response.json()
            return [model["name"] for model in data.get("models", [])]

        except Exception as e:
            logger.error("Failed to get Ollama models: %s", str(e))
            return []

    async def cleanup(self) -> None:
        """Clean up Ollama client"""
        if self.client:
            await self.client.aclose()


class ProviderManager:
    """
    Manages multiple AI providers with secure credential storage and
    unified interface for chat operations.
    """

    def __init__(self, config_manager: ConfigManager):
        """
        Initialize the Provider Manager.

        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager
        self.providers: Dict[str, AIProvider] = {}
        self.provider_configs: Dict[str, ProviderConfig] = {}
        self.default_provider: Optional[str] = None

    async def initialize(self) -> None:
        """Initialize the provider manager and load configurations"""
        try:
            await self._load_provider_configurations()
            await self._initialize_providers()
            logger.info("Provider Manager initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize Provider Manager: %s", str(e))
            raise

    async def _load_provider_configurations(self) -> None:
        """Load provider configurations from config"""
        try:
            providers_config = self.config_manager.get("providers", {})
            self.default_provider = providers_config.get("default")

            for provider_name, provider_data in providers_config.get(
                "list", {}
            ).items():
                config = ProviderConfig(
                    name=provider_name,
                    provider_type=ProviderType(provider_data.get("type")),
                    api_key=provider_data.get("api_key"),
                    base_url=provider_data.get("base_url"),
                    model=provider_data.get("model"),
                    enabled=provider_data.get("enabled", True),
                    settings=provider_data.get("settings", {}),
                )

                self.provider_configs[provider_name] = config

            logger.info("Loaded %d provider configurations", len(self.provider_configs))

        except Exception as e:
            logger.error("Failed to load provider configurations: %s", str(e))
            raise

    async def _initialize_providers(self) -> None:
        """Initialize all enabled providers"""
        initialization_tasks = []

        for provider_name, config in self.provider_configs.items():
            if config.enabled:
                task = asyncio.create_task(
                    self._initialize_provider(provider_name, config),
                    name=f"init_{provider_name}",
                )
                initialization_tasks.append(task)

        if initialization_tasks:
            results = await asyncio.gather(
                *initialization_tasks, return_exceptions=True
            )

            for i, (provider_name, config) in enumerate(
                [
                    (name, cfg)
                    for name, cfg in self.provider_configs.items()
                    if cfg.enabled
                ]
            ):
                if isinstance(results[i], Exception):
                    logger.error(
                        "Failed to initialize provider %s: %s",
                        provider_name,
                        str(results[i]),
                    )
                else:
                    logger.info("Successfully initialized provider %s", provider_name)

    async def _initialize_provider(
        self, provider_name: str, config: ProviderConfig
    ) -> None:
        """Initialize a single provider"""
        try:
            # Create provider instance based on type
            if config.provider_type == ProviderType.OPENAI:
                provider = OpenAIProvider(config)
            elif config.provider_type == ProviderType.ANTHROPIC:
                provider = AnthropicProvider(config)
            elif config.provider_type == ProviderType.LOCAL_OLLAMA:
                provider = LocalOllamaProvider(config)
            else:
                raise ValueError(f"Unsupported provider type: {config.provider_type}")

            await provider.initialize()
            self.providers[provider_name] = provider

        except Exception as e:
            logger.error("Failed to initialize provider %s: %s", provider_name, str(e))
            raise

    def get_provider(self, provider_name: Optional[str] = None) -> AIProvider:
        """
        Get a provider instance.

        Args:
            provider_name: Name of the provider (uses default if None)

        Returns:
            Provider instance

        Raises:
            ValueError: If provider not found
        """
        if provider_name is None:
            provider_name = self.default_provider

        if provider_name not in self.providers:
            raise ValueError(f"Provider '{provider_name}' not found or not initialized")

        return self.providers[provider_name]

    def get_available_providers(self) -> List[str]:
        """Get list of available (initialized) provider names"""
        return list(self.providers.keys())

    def get_all_configurations(self) -> Dict[str, ProviderConfig]:
        """Get all provider configurations"""
        return self.provider_configs.copy()

    async def chat(
        self,
        messages: List[ChatMessage],
        provider_name: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs,
    ) -> str:
        """
        Send a chat request using the specified or default provider.

        Args:
            messages: List of chat messages
            provider_name: Provider to use (uses default if None)
            model: Model to use
            **kwargs: Additional arguments for the provider

        Returns:
            Chat response
        """
        provider = self.get_provider(provider_name)
        return await provider.chat(messages, model=model, **kwargs)

    async def test_provider(self, provider_name: str) -> bool:
        """Test a provider connection"""
        if provider_name not in self.providers:
            return False

        provider = self.providers[provider_name]
        return await provider.test_connection()

    async def add_provider(self, config: ProviderConfig) -> None:
        """Add and initialize a new provider"""
        self.provider_configs[config.name] = config

        if config.enabled:
            await self._initialize_provider(config.name, config)

        # Save configuration
        await self._save_provider_configurations()

    async def remove_provider(self, provider_name: str) -> None:
        """Remove a provider"""
        # Clean up provider
        if provider_name in self.providers:
            await self.providers[provider_name].cleanup()
            del self.providers[provider_name]

        # Remove configuration
        if provider_name in self.provider_configs:
            del self.provider_configs[provider_name]

        # Update default if needed
        if self.default_provider == provider_name:
            available = list(self.providers.keys())
            self.default_provider = available[0] if available else None

        # Save configuration
        await self._save_provider_configurations()

    async def _save_provider_configurations(self) -> None:
        """Save provider configurations to config"""
        providers_config = {"default": self.default_provider, "list": {}}

        for provider_name, config in self.provider_configs.items():
            providers_config["list"][provider_name] = {
                "type": config.provider_type.value,
                "api_key": config.api_key,
                "base_url": config.base_url,
                "model": config.model,
                "enabled": config.enabled,
                "settings": config.settings,
            }

        self.config_manager.set("providers", providers_config)

    async def cleanup(self) -> None:
        """Clean up all providers"""
        cleanup_tasks = []

        for provider in self.providers.values():
            task = asyncio.create_task(provider.cleanup())
            cleanup_tasks.append(task)

        if cleanup_tasks:
            await asyncio.gather(*cleanup_tasks, return_exceptions=True)

        self.providers.clear()
        logger.info("Provider Manager cleaned up successfully")


# Global provider manager instance
_provider_manager = None


def get_provider_manager() -> ProviderManager:
    """
    Get the global provider manager instance

    Returns:
        ProviderManager instance
    """
    global _provider_manager
    if _provider_manager is None:
        from freecad_ai_addon.utils.config import ConfigManager

        config_manager = ConfigManager()
        _provider_manager = ProviderManager(config_manager)
    return _provider_manager
