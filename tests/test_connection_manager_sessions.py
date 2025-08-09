import pytest

from freecad_ai_addon.core.connection_manager import ConnectionManager, ConnectionConfig


@pytest.mark.asyncio
async def test_session_lifecycle(monkeypatch):
    cm = ConnectionManager(config=ConnectionConfig())

    # Stub connection always returns True
    monkeypatch.setattr(cm, "_connect_to_server", lambda name, cfg: True, raising=True)

    session_id = await cm.create_session("serverA", {"url": "http://localhost"})
    assert session_id in cm.sessions

    # Execute within session
    result = await cm.execute_in_session(session_id, "echo", {"x": 1})
    assert result["ok"] is True
    assert result["tool"] == "echo"
    assert result["arguments"] == {"x": 1}

    # Close session
    await cm.close_session(session_id)
    assert session_id not in cm.sessions
