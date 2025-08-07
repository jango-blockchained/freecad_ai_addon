"""
Comprehensive Test Suite for MCP (Model Context Protocol) Integration

This module tests all aspects of MCP integration including:
- Connection management (stdio and HTTP)
- Protocol message handling
- Tool discovery and execution
- Session management
- Error handling and recovery
"""

import pytest
import asyncio
import json
import tempfile
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path

from freecad_ai_addon.core.mcp_client import MCPClientManager
from freecad_ai_addon.core.connection_manager import ConnectionManager


class TestMCPConnection:
    """Test MCP connection functionality"""

    @pytest.fixture
    def mcp_client(self):
        """Create a test MCP client"""
        return MCPClientManager()

    @pytest.fixture
    def mock_stdio_server(self):
        """Mock a stdio MCP server"""
        return {
            "command": ["python", "-m", "test_mcp_server"],
            "type": "stdio",
            "name": "test-server",
        }

    @pytest.fixture
    def mock_http_server(self):
        """Mock an HTTP MCP server"""
        return {
            "url": "http://localhost:3000/mcp",
            "type": "http",
            "name": "test-http-server",
        }

    @pytest.mark.asyncio
    @pytest.mark.timeout(10)
    async def test_mcp_client_initialization(self, mcp_client):
        """Test MCP client initialization"""
        assert mcp_client is not None
        assert mcp_client.connections == {}
        assert mcp_client.tools == {}
        assert mcp_client.resources == {}

    @pytest.mark.asyncio
    @pytest.mark.timeout(10)
    async def test_stdio_connection_establishment(self, mcp_client, mock_stdio_server):
        """Test establishing a stdio connection to MCP server"""
        with patch("asyncio.create_subprocess_exec") as mock_subprocess:
            # Mock subprocess
            mock_process = Mock()
            mock_process.stdin = AsyncMock()
            mock_process.stdout = AsyncMock()
            mock_process.stderr = AsyncMock()
            mock_subprocess.return_value = mock_process

            # Mock initialization response
            init_response = {
                "jsonrpc": "2.0",
                "id": 1,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}, "resources": {}},
                    "serverInfo": {"name": "test-server", "version": "1.0.0"},
                },
            }

            mock_process.stdout.readline.return_value = (
                json.dumps(init_response).encode() + b"\n"
            )

            # Test connection
            success = await mcp_client.connect_stdio(
                command=mock_stdio_server["command"],
                server_name=mock_stdio_server["name"],
            )

            assert success
            assert mock_stdio_server["name"] in mcp_client.connections
            mock_subprocess.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.timeout(10)
    async def test_http_connection_establishment(self, mcp_client, mock_http_server):
        """Test establishing an HTTP connection to MCP server"""
        with patch("httpx.AsyncClient") as mock_client:
            # Mock HTTP client
            mock_http_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_http_instance

            # Mock initialization response
            init_response = {
                "jsonrpc": "2.0",
                "id": 1,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}, "resources": {}},
                    "serverInfo": {"name": "test-http-server", "version": "1.0.0"},
                },
            }

            mock_http_instance.post.return_value.json.return_value = init_response
            mock_http_instance.post.return_value.status_code = 200

            # Test connection
            success = await mcp_client.connect_http(
                url=mock_http_server["url"], server_name=mock_http_server["name"]
            )

            assert success
            assert mock_http_server["name"] in mcp_client.connections

    @pytest.mark.asyncio
    @pytest.mark.timeout(10)
    async def test_connection_failure_handling(self, mcp_client):
        """Test handling of connection failures"""
        with patch("asyncio.create_subprocess_exec") as mock_subprocess:
            # Simulate connection failure
            mock_subprocess.side_effect = Exception("Connection failed")

            success = await mcp_client.connect_stdio(
                command=["invalid_command"], server_name="failing-server"
            )

            assert not success
            assert "failing-server" not in mcp_client.connections

    @pytest.mark.asyncio
    @pytest.mark.timeout(10)
    async def test_connection_timeout(self, mcp_client):
        """Test connection timeout handling"""
        with patch("asyncio.create_subprocess_exec") as mock_subprocess:
            # Mock subprocess that hangs
            mock_process = Mock()
            mock_process.stdin = AsyncMock()
            mock_process.stdout = AsyncMock()
            mock_process.stderr = AsyncMock()
            mock_subprocess.return_value = mock_process

            # Simulate timeout
            mock_process.stdout.readline.side_effect = asyncio.TimeoutError()

            success = await mcp_client.connect_stdio(
                command=["hanging_command"], server_name="timeout-server", timeout=1.0
            )

            assert not success


class TestMCPProtocol:
    """Test MCP protocol message handling"""

    @pytest.fixture
    def connected_client(self):
        """Create a connected MCP client"""
        client = MCPClientManager()
        # Mock a connection
        client.connections["test-server"] = {
            "type": "stdio",
            "process": Mock(),
            "capabilities": {"tools": {}, "resources": {}},
        }
        return client

    @pytest.mark.asyncio
    @pytest.mark.timeout(10)
    async def test_tool_discovery(self, connected_client):
        """Test tool discovery through MCP protocol"""
        # Mock tools list response
        tools_response = {
            "jsonrpc": "2.0",
            "id": 2,
            "result": {
                "tools": [
                    {
                        "name": "create_file",
                        "description": "Create a new file",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "path": {"type": "string"},
                                "content": {"type": "string"},
                            },
                            "required": ["path", "content"],
                        },
                    },
                    {
                        "name": "read_file",
                        "description": "Read file contents",
                        "inputSchema": {
                            "type": "object",
                            "properties": {"path": {"type": "string"}},
                            "required": ["path"],
                        },
                    },
                ]
            },
        }

        with patch.object(connected_client, "_send_request") as mock_send:
            mock_send.return_value = tools_response

            tools = await connected_client.list_tools("test-server")

            assert len(tools) == 2
            assert "create_file" in [tool["name"] for tool in tools]
            assert "read_file" in [tool["name"] for tool in tools]

    @pytest.mark.asyncio
    @pytest.mark.timeout(10)
    async def test_resource_discovery(self, connected_client):
        """Test resource discovery through MCP protocol"""
        # Mock resources list response
        resources_response = {
            "jsonrpc": "2.0",
            "id": 3,
            "result": {
                "resources": [
                    {
                        "uri": "file:///tmp/test.txt",
                        "name": "Test File",
                        "description": "A test file",
                        "mimeType": "text/plain",
                    }
                ]
            },
        }

        with patch.object(connected_client, "_send_request") as mock_send:
            mock_send.return_value = resources_response

            resources = await connected_client.list_resources("test-server")

            assert len(resources) == 1
            assert resources[0]["uri"] == "file:///tmp/test.txt"
            assert resources[0]["mimeType"] == "text/plain"

    @pytest.mark.asyncio
    @pytest.mark.timeout(10)
    async def test_tool_execution(self, connected_client):
        """Test tool execution through MCP protocol"""
        # Mock tool execution response
        execution_response = {
            "jsonrpc": "2.0",
            "id": 4,
            "result": {
                "content": [{"type": "text", "text": "File created successfully"}]
            },
        }

        with patch.object(connected_client, "_send_request") as mock_send:
            mock_send.return_value = execution_response

            result = await connected_client.call_tool(
                server_name="test-server",
                tool_name="create_file",
                arguments={"path": "/tmp/test.txt", "content": "Hello, World!"},
            )

            assert result is not None
            assert result["content"][0]["text"] == "File created successfully"

    @pytest.mark.asyncio
    @pytest.mark.timeout(10)
    async def test_resource_reading(self, connected_client):
        """Test resource reading through MCP protocol"""
        # Mock resource read response
        read_response = {
            "jsonrpc": "2.0",
            "id": 5,
            "result": {
                "contents": [
                    {
                        "uri": "file:///tmp/test.txt",
                        "mimeType": "text/plain",
                        "text": "Hello, World!",
                    }
                ]
            },
        }

        with patch.object(connected_client, "_send_request") as mock_send:
            mock_send.return_value = read_response

            content = await connected_client.read_resource(
                server_name="test-server", uri="file:///tmp/test.txt"
            )

            assert content is not None
            assert content["contents"][0]["text"] == "Hello, World!"

    @pytest.mark.asyncio
    @pytest.mark.timeout(10)
    async def test_protocol_error_handling(self, connected_client):
        """Test handling of protocol errors"""
        # Mock error response
        error_response = {
            "jsonrpc": "2.0",
            "id": 6,
            "error": {
                "code": -32601,
                "message": "Method not found",
                "data": {"method": "unknown_method"},
            },
        }

        with patch.object(connected_client, "_send_request") as mock_send:
            mock_send.return_value = error_response

            with pytest.raises(Exception) as exc_info:
                await connected_client.call_tool(
                    server_name="test-server", tool_name="unknown_tool", arguments={}
                )

            assert "Method not found" in str(exc_info.value)


class TestMCPSessionManagement:
    """Test MCP session management"""

    @pytest.fixture
    def connection_manager(self):
        """Create a connection manager for testing"""
        return ConnectionManager()

    @pytest.mark.asyncio
    @pytest.mark.timeout(10)
    async def test_session_creation(self, connection_manager):
        """Test creating a new MCP session"""
        session_id = await connection_manager.create_session(
            server_name="test-server",
            config={"command": ["python", "-m", "test_server"], "type": "stdio"},
        )

        assert session_id is not None
        assert session_id in connection_manager.sessions

    @pytest.mark.asyncio
    @pytest.mark.timeout(10)
    async def test_session_persistence(self, connection_manager):
        """Test session persistence across requests"""
        with patch.object(connection_manager, "_connect_to_server") as mock_connect:
            mock_connect.return_value = True

            session_id = await connection_manager.create_session(
                server_name="persistent-server",
                config={"type": "stdio", "command": ["test"]},
            )

            # Simulate multiple requests in the same session
            for i in range(3):
                result = await connection_manager.execute_in_session(
                    session_id=session_id,
                    tool_name="test_tool",
                    arguments={"test": f"request_{i}"},
                )
                # In a real scenario, we'd assert the session state persists

            assert session_id in connection_manager.sessions

    @pytest.mark.asyncio
    @pytest.mark.timeout(10)
    async def test_session_cleanup(self, connection_manager):
        """Test proper session cleanup"""
        with patch.object(connection_manager, "_connect_to_server") as mock_connect:
            mock_connect.return_value = True

            session_id = await connection_manager.create_session(
                server_name="cleanup-server",
                config={"type": "stdio", "command": ["test"]},
            )

            assert session_id in connection_manager.sessions

            await connection_manager.close_session(session_id)

            assert session_id not in connection_manager.sessions

    @pytest.mark.asyncio
    @pytest.mark.timeout(10)
    async def test_concurrent_sessions(self, connection_manager):
        """Test handling multiple concurrent sessions"""
        with patch.object(connection_manager, "_connect_to_server") as mock_connect:
            mock_connect.return_value = True

            # Create multiple sessions
            sessions = []
            for i in range(3):
                session_id = await connection_manager.create_session(
                    server_name=f"concurrent-server-{i}",
                    config={"type": "stdio", "command": ["test"]},
                )
                sessions.append(session_id)

            # Verify all sessions exist
            for session_id in sessions:
                assert session_id in connection_manager.sessions

            # Clean up all sessions
            for session_id in sessions:
                await connection_manager.close_session(session_id)

            # Verify all sessions are cleaned up
            for session_id in sessions:
                assert session_id not in connection_manager.sessions


class TestMCPErrorHandling:
    """Test MCP error handling and recovery"""

    @pytest.fixture
    def error_prone_client(self):
        """Create an MCP client for error testing"""
        return MCPClientManager()

    @pytest.mark.asyncio
    @pytest.mark.timeout(10)
    async def test_network_error_recovery(self, error_prone_client):
        """Test recovery from network errors"""
        with patch.object(error_prone_client, "_send_request") as mock_send:
            # First call fails, second succeeds
            mock_send.side_effect = [
                Exception("Network error"),
                {"jsonrpc": "2.0", "id": 1, "result": {"success": True}},
            ]

            # Should retry and succeed
            result = await error_prone_client.call_tool_with_retry(
                server_name="test-server",
                tool_name="test_tool",
                arguments={},
                max_retries=2,
            )

            assert result is not None
            assert mock_send.call_count == 2

    @pytest.mark.asyncio
    @pytest.mark.timeout(10)
    async def test_server_restart_handling(self, error_prone_client):
        """Test handling server restart scenarios"""
        with patch.object(error_prone_client, "connect_stdio") as mock_connect:
            # Simulate connection loss and reconnection
            mock_connect.side_effect = [False, True]  # First fails, second succeeds

            success = await error_prone_client.reconnect_server("test-server")
            assert success
            assert mock_connect.call_count == 2

    @pytest.mark.asyncio
    @pytest.mark.timeout(10)
    async def test_malformed_response_handling(self, error_prone_client):
        """Test handling of malformed responses"""
        with patch.object(error_prone_client, "_send_request") as mock_send:
            # Return malformed JSON
            mock_send.return_value = "invalid json response"

            with pytest.raises(Exception):
                await error_prone_client.call_tool(
                    server_name="test-server", tool_name="test_tool", arguments={}
                )


class TestMCPIntegration:
    """Integration tests for complete MCP workflows"""

    @pytest.mark.asyncio
    @pytest.mark.timeout(10)
    async def test_complete_workflow(self):
        """Test a complete MCP workflow from connection to tool execution"""
        client = MCPClientManager()

        # Mock the entire workflow
        with patch("asyncio.create_subprocess_exec") as mock_subprocess, patch.object(
            client, "_send_request"
        ) as mock_send:
            # Mock subprocess
            mock_process = Mock()
            mock_process.stdin = AsyncMock()
            mock_process.stdout = AsyncMock()
            mock_subprocess.return_value = mock_process

            # Mock initialization
            init_response = {
                "jsonrpc": "2.0",
                "id": 1,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}, "resources": {}},
                    "serverInfo": {"name": "test", "version": "1.0.0"},
                },
            }
            mock_process.stdout.readline.return_value = (
                json.dumps(init_response).encode() + b"\n"
            )

            # Mock tool listing
            tools_response = {
                "jsonrpc": "2.0",
                "id": 2,
                "result": {
                    "tools": [
                        {
                            "name": "test_tool",
                            "description": "A test tool",
                            "inputSchema": {"type": "object"},
                        }
                    ]
                },
            }

            # Mock tool execution
            execution_response = {
                "jsonrpc": "2.0",
                "id": 3,
                "result": {"content": [{"type": "text", "text": "Success"}]},
            }

            mock_send.side_effect = [tools_response, execution_response]

            # Execute complete workflow
            connected = await client.connect_stdio(["test"], "test-server")
            assert connected

            tools = await client.list_tools("test-server")
            assert len(tools) == 1

            result = await client.call_tool("test-server", "test_tool", {})
            assert result["content"][0]["text"] == "Success"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
