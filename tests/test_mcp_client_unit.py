import pytest

from freecad_ai_addon.core.mcp_client import MCPClientManager


@pytest.mark.asyncio
async def test_list_tools_and_cache(monkeypatch):
    m = MCPClientManager()
    server = "s1"
    # Pretend a lightweight connection exists
    m.connections[server] = {"type": "http", "url": "http://dummy"}

    async def fake_send(_server, method, params):  # noqa: ARG001
        assert method == "tools/list"
        return {
            "result": {
                "tools": [
                    {"name": "echo", "description": "Echo tool", "input_schema": {}},
                ]
            }
        }

    monkeypatch.setattr(m, "_send_request", fake_send, raising=True)

    tools = await m.list_tools(server)
    assert tools and tools[0]["name"] == "echo"
    assert server in m.tools and m.tools[server] == tools


@pytest.mark.asyncio
async def test_call_tool_via_jsonrpc(monkeypatch):
    m = MCPClientManager()
    server = "s2"
    m.connections[server] = {"type": "stdio", "process": object()}

    async def fake_send(_server, method, params):
        assert method == "tools/call"
        assert params["name"] == "echo"
        assert params["arguments"] == {"x": 1}
        return {"result": {"ok": True, "echo": params["arguments"]}}

    monkeypatch.setattr(m, "_send_request", fake_send, raising=True)

    result = await m.call_tool(server_name=server, tool_name="echo", arguments={"x": 1})
    assert result["ok"] is True
    assert result["echo"] == {"x": 1}


@pytest.mark.asyncio
async def test_read_resource_simple(monkeypatch):
    m = MCPClientManager()
    server = "s3"
    m.connections[server] = {"type": "http", "url": "http://dummy"}

    async def fake_send(_server, method, params):
        assert method == "resources/read"
        assert params["uri"] == "file://doc.txt"
        return {"result": {"mimeType": "text/plain", "data": "hello"}}

    monkeypatch.setattr(m, "_send_request", fake_send, raising=True)

    result = await m.read_resource_simple(server, "file://doc.txt")
    assert result["mimeType"] == "text/plain"
    assert result["data"] == "hello"


@pytest.mark.asyncio
async def test_reconnect_server(monkeypatch):
    m = MCPClientManager()
    server = "s4"
    calls = {"n": 0}

    async def fake_connect_stdio(cmd, name, timeout=5.0):  # noqa: ARG001
        calls["n"] += 1
        return calls["n"] == 1

    monkeypatch.setattr(m, "connect_stdio", fake_connect_stdio, raising=True)

    ok = await m.reconnect_server(server)
    assert ok is True
    assert calls["n"] >= 1
