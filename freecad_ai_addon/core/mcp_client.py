"""
MCP Client Manager for FreeCAD AI Addon

Provides a high-level interface for connecting to and managing MCP servers,
handling multiple AI providers through the Model Context Protocol.
"""

import asyncio
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from contextlib import AsyncExitStack

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.client.streamable_http import streamablehttp_client
from mcp.client.sse import sse_client

from freecad_ai_addon.utils.logging import get_logger
from freecad_ai_addon.utils.config import ConfigManager

logger = get_logger("mcp_client")


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server connection"""

    name: str
    transport: str  # 'stdio', 'http', 'sse'
    command: Optional[str] = None
    args: Optional[List[str]] = None
    url: Optional[str] = None
    env: Optional[Dict[str, str]] = None
    timeout: int = 30
    enabled: bool = True


@dataclass
class MCPTool:
    """Represents an MCP tool with metadata"""

    name: str
    description: str
    input_schema: Dict[str, Any]
    server_name: str


@dataclass
class MCPResource:
    """Represents an MCP resource with metadata"""

    uri: str
    name: str
    description: str
    mime_type: Optional[str]
    server_name: str


class MCPClientManager:
    """
    Manages connections to multiple MCP servers and provides a unified interface
    for accessing tools and resources across all connected servers.
    """

    def __init__(self, config_manager: ConfigManager):
        """
        Initialize the MCP Client Manager.

        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager
        self.servers: Dict[str, ClientSession] = {}
        self.server_configs: Dict[str, MCPServerConfig] = {}
        self.exit_stack = AsyncExitStack()
        self._tools_cache: Dict[str, List[MCPTool]] = {}
        self._resources_cache: Dict[str, List[MCPResource]] = {}
        self._connection_status: Dict[str, bool] = {}

        # Event callbacks
        self.on_connection_status_changed: Optional[Callable[[str, bool], None]] = None
        self.on_tools_updated: Optional[Callable[[str, List[MCPTool]], None]] = None
        self.on_resources_updated: Optional[
            Callable[[str, List[MCPResource]], None]
        ] = None

    async def initialize(self) -> None:
        """Initialize the MCP client manager and load server configurations"""
        try:
            await self._load_server_configurations()
            await self._connect_enabled_servers()
            logger.info("MCP Client Manager initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize MCP Client Manager: %s", str(e))
            raise

    async def _load_server_configurations(self) -> None:
        """Load MCP server configurations from config"""
        try:
            servers_config = self.config_manager.get("mcp.servers", {})

            for server_name, server_data in servers_config.items():
                config = MCPServerConfig(
                    name=server_name,
                    transport=server_data.get("transport", "stdio"),
                    command=server_data.get("command"),
                    args=server_data.get("args", []),
                    url=server_data.get("url"),
                    env=server_data.get("env", {}),
                    timeout=server_data.get("timeout", 30),
                    enabled=server_data.get("enabled", True),
                )

                self.server_configs[server_name] = config
                self._connection_status[server_name] = False

            logger.info("Loaded %d MCP server configurations", len(self.server_configs))

        except Exception as e:
            logger.error("Failed to load MCP server configurations: %s", str(e))
            raise

    async def _connect_enabled_servers(self) -> None:
        """Connect to all enabled MCP servers"""
        connection_tasks = []

        for server_name, config in self.server_configs.items():
            if config.enabled:
                task = asyncio.create_task(
                    self._connect_server(server_name, config),
                    name=f"connect_{server_name}",
                )
                connection_tasks.append(task)

        if connection_tasks:
            # Connect to servers concurrently
            results = await asyncio.gather(*connection_tasks, return_exceptions=True)

            # Log results
            for i, (server_name, config) in enumerate(
                [
                    (name, cfg)
                    for name, cfg in self.server_configs.items()
                    if cfg.enabled
                ]
            ):
                if isinstance(results[i], Exception):
                    logger.error(
                        "Failed to connect to server %s: %s",
                        server_name,
                        str(results[i]),
                    )
                else:
                    logger.info("Successfully connected to server %s", server_name)

    async def _connect_server(self, server_name: str, config: MCPServerConfig) -> None:
        """
        Connect to a single MCP server.

        Args:
            server_name: Name of the server
            config: Server configuration
        """
        try:
            logger.info(
                "Connecting to MCP server %s via %s", server_name, config.transport
            )

            if config.transport == "stdio":
                await self._connect_stdio_server(server_name, config)
            elif config.transport == "http":
                await self._connect_http_server(server_name, config)
            elif config.transport == "sse":
                await self._connect_sse_server(server_name, config)
            else:
                raise ValueError(f"Unsupported transport: {config.transport}")

            # Cache tools and resources
            await self._refresh_server_capabilities(server_name)

            # Update connection status
            self._connection_status[server_name] = True
            if self.on_connection_status_changed:
                self.on_connection_status_changed(server_name, True)

        except Exception as e:
            logger.error("Failed to connect to server %s: %s", server_name, str(e))
            self._connection_status[server_name] = False
            if self.on_connection_status_changed:
                self.on_connection_status_changed(server_name, False)
            raise

    async def _connect_stdio_server(
        self, server_name: str, config: MCPServerConfig
    ) -> None:
        """Connect to an MCP server via stdio transport"""
        if not config.command:
            raise ValueError(
                f"Command required for stdio transport (server: {server_name})"
            )

        server_params = StdioServerParameters(
            command=config.command, args=config.args or [], env=config.env
        )

        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        read, write = stdio_transport

        session = await self.exit_stack.enter_async_context(ClientSession(read, write))

        await session.initialize()
        self.servers[server_name] = session

    async def _connect_http_server(
        self, server_name: str, config: MCPServerConfig
    ) -> None:
        """Connect to an MCP server via HTTP transport"""
        if not config.url:
            raise ValueError(f"URL required for HTTP transport (server: {server_name})")

        http_transport = await self.exit_stack.enter_async_context(
            streamablehttp_client(config.url)
        )
        read, write, _ = http_transport

        session = await self.exit_stack.enter_async_context(ClientSession(read, write))

        await session.initialize()
        self.servers[server_name] = session

    async def _connect_sse_server(
        self, server_name: str, config: MCPServerConfig
    ) -> None:
        """Connect to an MCP server via SSE transport"""
        if not config.url:
            raise ValueError(f"URL required for SSE transport (server: {server_name})")

        sse_transport = await self.exit_stack.enter_async_context(
            sse_client(config.url)
        )
        read, write = sse_transport

        session = await self.exit_stack.enter_async_context(ClientSession(read, write))

        await session.initialize()
        self.servers[server_name] = session

    async def _refresh_server_capabilities(self, server_name: str) -> None:
        """Refresh cached tools and resources for a server"""
        session = self.servers.get(server_name)
        if not session:
            return

        try:
            # Refresh tools
            tools_response = await session.list_tools()
            tools = []

            for item in tools_response:
                if isinstance(item, tuple) and item[0] == "tools":
                    for tool in item[1]:
                        tools.append(
                            MCPTool(
                                name=tool.name,
                                description=tool.description or "",
                                input_schema=tool.inputSchema or {},
                                server_name=server_name,
                            )
                        )

            self._tools_cache[server_name] = tools
            if self.on_tools_updated:
                self.on_tools_updated(server_name, tools)

            # Refresh resources
            resources_response = await session.list_resources()
            resources = []

            for resource in resources_response.resources:
                resources.append(
                    MCPResource(
                        uri=str(resource.uri),
                        name=resource.name or str(resource.uri),
                        description=resource.description or "",
                        mime_type=resource.mimeType,
                        server_name=server_name,
                    )
                )

            self._resources_cache[server_name] = resources
            if self.on_resources_updated:
                self.on_resources_updated(server_name, resources)

            logger.info(
                "Refreshed capabilities for server %s: %d tools, %d resources",
                server_name,
                len(tools),
                len(resources),
            )

        except Exception as e:
            logger.error(
                "Failed to refresh capabilities for server %s: %s", server_name, str(e)
            )

    def get_all_tools(self) -> List[MCPTool]:
        """Get all available tools from all connected servers"""
        all_tools = []
        for tools in self._tools_cache.values():
            all_tools.extend(tools)
        return all_tools

    def get_all_resources(self) -> List[MCPResource]:
        """Get all available resources from all connected servers"""
        all_resources = []
        for resources in self._resources_cache.values():
            all_resources.extend(resources)
        return all_resources

    def get_server_tools(self, server_name: str) -> List[MCPTool]:
        """Get tools for a specific server"""
        return self._tools_cache.get(server_name, [])

    def get_server_resources(self, server_name: str) -> List[MCPResource]:
        """Get resources for a specific server"""
        return self._resources_cache.get(server_name, [])

    def is_server_connected(self, server_name: str) -> bool:
        """Check if a server is connected"""
        return self._connection_status.get(server_name, False)

    def get_connected_servers(self) -> List[str]:
        """Get list of connected server names"""
        return [
            name for name, connected in self._connection_status.items() if connected
        ]

    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        server_name: Optional[str] = None,
    ) -> Any:
        """
        Call a tool on an MCP server.

        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool
            server_name: Specific server to call (if None, finds the tool)

        Returns:
            Tool execution result

        Raises:
            ValueError: If tool not found or server not available
        """
        # Find the tool if server not specified
        if server_name is None:
            tool = None
            for tools in self._tools_cache.values():
                for t in tools:
                    if t.name == tool_name:
                        tool = t
                        server_name = t.server_name
                        break
                if tool:
                    break

            if not tool:
                raise ValueError(
                    f"Tool '{tool_name}' not found in any connected server"
                )

        # Get the session
        session = self.servers.get(server_name)
        if not session:
            raise ValueError(f"Server '{server_name}' not connected")

        try:
            logger.info(
                "Calling tool %s on server %s with args: %s",
                tool_name,
                server_name,
                arguments,
            )
            result = await session.call_tool(tool_name, arguments)
            logger.info("Tool %s executed successfully", tool_name)
            return result
        except Exception as e:
            logger.error("Failed to call tool %s: %s", tool_name, str(e))
            raise

    async def read_resource(self, uri: str, server_name: Optional[str] = None) -> Any:
        """
        Read a resource from an MCP server.

        Args:
            uri: URI of the resource to read
            server_name: Specific server to read from (if None, finds the resource)

        Returns:
            Resource content

        Raises:
            ValueError: If resource not found or server not available
        """
        # Find the resource if server not specified
        if server_name is None:
            resource = None
            for resources in self._resources_cache.values():
                for r in resources:
                    if r.uri == uri:
                        resource = r
                        server_name = r.server_name
                        break
                if resource:
                    break

            if not resource:
                raise ValueError(f"Resource '{uri}' not found in any connected server")

        # Get the session
        session = self.servers.get(server_name)
        if not session:
            raise ValueError(f"Server '{server_name}' not connected")

        try:
            logger.info("Reading resource %s from server %s", uri, server_name)
            from pydantic import AnyUrl

            result = await session.read_resource(AnyUrl(uri))
            logger.info("Resource %s read successfully", uri)
            return result
        except Exception as e:
            logger.error("Failed to read resource %s: %s", uri, str(e))
            raise

    async def refresh_all_capabilities(self) -> None:
        """Refresh capabilities for all connected servers"""
        refresh_tasks = []

        for server_name in self.get_connected_servers():
            task = asyncio.create_task(
                self._refresh_server_capabilities(server_name),
                name=f"refresh_{server_name}",
            )
            refresh_tasks.append(task)

        if refresh_tasks:
            await asyncio.gather(*refresh_tasks, return_exceptions=True)

    async def add_server(self, config: MCPServerConfig) -> None:
        """
        Add and connect to a new MCP server.

        Args:
            config: Server configuration
        """
        self.server_configs[config.name] = config
        self._connection_status[config.name] = False

        if config.enabled:
            await self._connect_server(config.name, config)

        # Save configuration
        servers_config = self.config_manager.get("mcp.servers", {})
        servers_config[config.name] = {
            "transport": config.transport,
            "command": config.command,
            "args": config.args,
            "url": config.url,
            "env": config.env,
            "timeout": config.timeout,
            "enabled": config.enabled,
        }
        self.config_manager.set("mcp.servers", servers_config)

    async def remove_server(self, server_name: str) -> None:
        """
        Remove and disconnect from an MCP server.

        Args:
            server_name: Name of the server to remove
        """
        # Disconnect if connected
        if server_name in self.servers:
            del self.servers[server_name]

        # Clear cache
        self._tools_cache.pop(server_name, None)
        self._resources_cache.pop(server_name, None)
        self._connection_status.pop(server_name, None)

        # Remove from configuration
        if server_name in self.server_configs:
            del self.server_configs[server_name]

            servers_config = self.config_manager.get("mcp.servers", {})
            servers_config.pop(server_name, None)
            self.config_manager.set("mcp.servers", servers_config)

        if self.on_connection_status_changed:
            self.on_connection_status_changed(server_name, False)

    async def cleanup(self) -> None:
        """Clean up all connections and resources"""
        try:
            await self.exit_stack.aclose()
            self.servers.clear()
            self._tools_cache.clear()
            self._resources_cache.clear()
            self._connection_status.clear()
            logger.info("MCP Client Manager cleaned up successfully")
        except Exception as e:
            logger.error("Error during MCP Client Manager cleanup: %s", str(e))
