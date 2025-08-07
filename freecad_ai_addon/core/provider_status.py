"""
Provider Status and Connection Monitoring

Manages real-time status of AI providers and their connections.
"""

import asyncio
import time
from typing import Dict, Optional, Any, Callable
from enum import Enum
from dataclasses import dataclass

from freecad_ai_addon.utils.security import get_credential_manager
from freecad_ai_addon.utils.logging import get_logger

logger = get_logger("provider_status")


class ProviderStatus(Enum):
    """Provider connection status enumeration"""

    UNKNOWN = "unknown"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"
    EXPIRED = "expired"


@dataclass
class ProviderHealth:
    """Provider health information"""

    status: ProviderStatus
    last_check: float
    response_time: Optional[float]
    error_message: Optional[str]
    rate_limit_remaining: Optional[int]
    rate_limit_reset: Optional[float]
    usage_stats: Dict[str, Any]


class ProviderMonitor:
    """Monitors provider status and connection health"""

    def __init__(self):
        """Initialize the provider monitor"""
        self.credential_manager = get_credential_manager()
        self._status_cache: Dict[str, ProviderHealth] = {}
        self._status_callbacks: Dict[str, list[Callable]] = {}
        self._monitoring_active = False
        self._monitor_task: Optional[asyncio.Task] = None

        logger.info("Provider monitor initialized")

    def register_status_callback(
        self, provider: str, callback: Callable[[ProviderHealth], None]
    ):
        """
        Register a callback for provider status changes

        Args:
            provider: Provider name
            callback: Function to call when status changes
        """
        if provider not in self._status_callbacks:
            self._status_callbacks[provider] = []
        self._status_callbacks[provider].append(callback)
        logger.debug("Registered status callback for provider %s", provider)

    def unregister_status_callback(
        self, provider: str, callback: Callable[[ProviderHealth], None]
    ):
        """
        Unregister a status callback

        Args:
            provider: Provider name
            callback: Callback function to remove
        """
        if provider in self._status_callbacks:
            try:
                self._status_callbacks[provider].remove(callback)
                if not self._status_callbacks[provider]:
                    del self._status_callbacks[provider]
                logger.debug("Unregistered status callback for provider %s", provider)
            except ValueError:
                logger.warning("Callback not found for provider %s", provider)

    def get_provider_status(self, provider: str) -> ProviderHealth:
        """
        Get current status for a provider

        Args:
            provider: Provider name

        Returns:
            ProviderHealth object with current status
        """
        if provider not in self._status_cache:
            # Initialize with unknown status
            self._status_cache[provider] = ProviderHealth(
                status=ProviderStatus.UNKNOWN,
                last_check=0,
                response_time=None,
                error_message=None,
                rate_limit_remaining=None,
                rate_limit_reset=None,
                usage_stats={},
            )

        return self._status_cache[provider]

    def get_all_provider_statuses(self) -> Dict[str, ProviderHealth]:
        """
        Get status for all monitored providers

        Returns:
            Dictionary mapping provider names to ProviderHealth objects
        """
        return self._status_cache.copy()

    async def check_provider_connection(self, provider: str) -> ProviderHealth:
        """
        Check connection to a specific provider

        Args:
            provider: Provider name

        Returns:
            Updated ProviderHealth object
        """
        start_time = time.time()

        try:
            # Get credentials
            api_key = self.credential_manager.get_credential(provider, "api_key")
            if not api_key and provider != "ollama":
                health = ProviderHealth(
                    status=ProviderStatus.DISCONNECTED,
                    last_check=start_time,
                    response_time=None,
                    error_message="No API key configured",
                    rate_limit_remaining=None,
                    rate_limit_reset=None,
                    usage_stats={},
                )
            else:
                # Perform actual connection test
                health = await self._test_provider_connection(
                    provider, api_key, start_time
                )

            # Cache the result
            self._status_cache[provider] = health

            # Notify callbacks
            await self._notify_status_callbacks(provider, health)

            return health

        except Exception as e:
            logger.error("Failed to check provider %s: %s", provider, str(e))
            health = ProviderHealth(
                status=ProviderStatus.ERROR,
                last_check=start_time,
                response_time=time.time() - start_time,
                error_message=str(e),
                rate_limit_remaining=None,
                rate_limit_reset=None,
                usage_stats={},
            )
            self._status_cache[provider] = health
            await self._notify_status_callbacks(provider, health)
            return health

    async def _test_provider_connection(
        self, provider: str, api_key: Optional[str], start_time: float
    ) -> ProviderHealth:
        """
        Test connection to a specific provider

        Args:
            provider: Provider name
            api_key: API key for the provider
            start_time: Start time of the test

        Returns:
            ProviderHealth object with test results
        """
        if provider == "openai":
            return await self._test_openai_connection(api_key, start_time)
        elif provider == "anthropic":
            return await self._test_anthropic_connection(api_key, start_time)
        elif provider == "ollama":
            return await self._test_ollama_connection(start_time)
        else:
            raise ValueError(f"Unknown provider: {provider}")

    async def _test_openai_connection(
        self, api_key: str, start_time: float
    ) -> ProviderHealth:
        """Test OpenAI connection"""
        try:
            import httpx

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.openai.com/v1/models", headers=headers, timeout=10.0
                )

                response_time = time.time() - start_time

                if response.status_code == 200:
                    # Parse rate limit headers
                    rate_limit_remaining = response.headers.get(
                        "x-ratelimit-remaining-requests"
                    )
                    rate_limit_reset = response.headers.get(
                        "x-ratelimit-reset-requests"
                    )

                    return ProviderHealth(
                        status=ProviderStatus.CONNECTED,
                        last_check=start_time,
                        response_time=response_time,
                        error_message=None,
                        rate_limit_remaining=(
                            int(rate_limit_remaining) if rate_limit_remaining else None
                        ),
                        rate_limit_reset=(
                            float(rate_limit_reset) if rate_limit_reset else None
                        ),
                        usage_stats={
                            "models_available": len(response.json().get("data", []))
                        },
                    )
                elif response.status_code == 401:
                    return ProviderHealth(
                        status=ProviderStatus.EXPIRED,
                        last_check=start_time,
                        response_time=response_time,
                        error_message="Invalid API key",
                        rate_limit_remaining=None,
                        rate_limit_reset=None,
                        usage_stats={},
                    )
                elif response.status_code == 429:
                    return ProviderHealth(
                        status=ProviderStatus.RATE_LIMITED,
                        last_check=start_time,
                        response_time=response_time,
                        error_message="Rate limit exceeded",
                        rate_limit_remaining=0,
                        rate_limit_reset=None,
                        usage_stats={},
                    )
                else:
                    return ProviderHealth(
                        status=ProviderStatus.ERROR,
                        last_check=start_time,
                        response_time=response_time,
                        error_message=f"HTTP {response.status_code}: {response.text}",
                        rate_limit_remaining=None,
                        rate_limit_reset=None,
                        usage_stats={},
                    )

        except Exception as e:
            return ProviderHealth(
                status=ProviderStatus.ERROR,
                last_check=start_time,
                response_time=time.time() - start_time,
                error_message=str(e),
                rate_limit_remaining=None,
                rate_limit_reset=None,
                usage_stats={},
            )

    async def _test_anthropic_connection(
        self, api_key: str, start_time: float
    ) -> ProviderHealth:
        """Test Anthropic connection"""
        try:
            import httpx

            headers = {
                "x-api-key": api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01",
            }

            # Test with a simple message to validate the key
            data = {
                "model": "claude-3-haiku-20240307",
                "max_tokens": 1,
                "messages": [{"role": "user", "content": "test"}],
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers=headers,
                    json=data,
                    timeout=10.0,
                )

                response_time = time.time() - start_time

                if response.status_code in [200, 400]:  # 400 is ok for validation
                    return ProviderHealth(
                        status=ProviderStatus.CONNECTED,
                        last_check=start_time,
                        response_time=response_time,
                        error_message=None,
                        rate_limit_remaining=None,
                        rate_limit_reset=None,
                        usage_stats={},
                    )
                elif response.status_code == 401:
                    return ProviderHealth(
                        status=ProviderStatus.EXPIRED,
                        last_check=start_time,
                        response_time=response_time,
                        error_message="Invalid API key",
                        rate_limit_remaining=None,
                        rate_limit_reset=None,
                        usage_stats={},
                    )
                elif response.status_code == 429:
                    return ProviderHealth(
                        status=ProviderStatus.RATE_LIMITED,
                        last_check=start_time,
                        response_time=response_time,
                        error_message="Rate limit exceeded",
                        rate_limit_remaining=0,
                        rate_limit_reset=None,
                        usage_stats={},
                    )
                else:
                    return ProviderHealth(
                        status=ProviderStatus.ERROR,
                        last_check=start_time,
                        response_time=response_time,
                        error_message=f"HTTP {response.status_code}: {response.text}",
                        rate_limit_remaining=None,
                        rate_limit_reset=None,
                        usage_stats={},
                    )

        except Exception as e:
            return ProviderHealth(
                status=ProviderStatus.ERROR,
                last_check=start_time,
                response_time=time.time() - start_time,
                error_message=str(e),
                rate_limit_remaining=None,
                rate_limit_reset=None,
                usage_stats={},
            )

    async def _test_ollama_connection(self, start_time: float) -> ProviderHealth:
        """Test Ollama connection"""
        try:
            import httpx

            # Get base URL from credentials or use default
            base_url = self.credential_manager.get_credential("ollama", "base_url")
            if not base_url:
                base_url = "http://localhost:11434"

            async with httpx.AsyncClient() as client:
                response = await client.get(f"{base_url}/api/tags", timeout=5.0)

                response_time = time.time() - start_time

                if response.status_code == 200:
                    models = response.json().get("models", [])
                    return ProviderHealth(
                        status=ProviderStatus.CONNECTED,
                        last_check=start_time,
                        response_time=response_time,
                        error_message=None,
                        rate_limit_remaining=None,
                        rate_limit_reset=None,
                        usage_stats={"models_available": len(models)},
                    )
                else:
                    return ProviderHealth(
                        status=ProviderStatus.ERROR,
                        last_check=start_time,
                        response_time=response_time,
                        error_message=f"HTTP {response.status_code}",
                        rate_limit_remaining=None,
                        rate_limit_reset=None,
                        usage_stats={},
                    )

        except Exception as e:
            return ProviderHealth(
                status=ProviderStatus.DISCONNECTED,
                last_check=start_time,
                response_time=time.time() - start_time,
                error_message=f"Connection failed: {str(e)}",
                rate_limit_remaining=None,
                rate_limit_reset=None,
                usage_stats={},
            )

    async def _notify_status_callbacks(self, provider: str, health: ProviderHealth):
        """Notify registered callbacks of status changes"""
        if provider in self._status_callbacks:
            for callback in self._status_callbacks[provider]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(health)
                    else:
                        callback(health)
                except Exception as e:
                    logger.error("Error in status callback: %s", str(e))

    async def start_monitoring(self, interval: float = 60.0):
        """
        Start continuous monitoring of all configured providers

        Args:
            interval: Check interval in seconds
        """
        if self._monitoring_active:
            logger.warning("Monitoring already active")
            return

        self._monitoring_active = True
        logger.info("Starting provider monitoring with %ss interval", interval)

        async def monitor_loop():
            while self._monitoring_active:
                try:
                    providers = self.credential_manager.list_providers()
                    tasks = [
                        self.check_provider_connection(provider)
                        for provider in providers
                    ]
                    if tasks:
                        await asyncio.gather(*tasks, return_exceptions=True)

                    await asyncio.sleep(interval)
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error("Error in monitoring loop: %s", str(e))
                    await asyncio.sleep(interval)

        self._monitor_task = asyncio.create_task(monitor_loop())

    async def stop_monitoring(self):
        """Stop continuous monitoring"""
        if not self._monitoring_active:
            return

        self._monitoring_active = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
            self._monitor_task = None

        logger.info("Provider monitoring stopped")


# Global provider monitor instance
_provider_monitor = None


def get_provider_monitor() -> ProviderMonitor:
    """
    Get the global provider monitor instance

    Returns:
        ProviderMonitor instance
    """
    global _provider_monitor
    if _provider_monitor is None:
        _provider_monitor = ProviderMonitor()
    return _provider_monitor
