from unittest.mock import MagicMock


def test_sessions_requires_auth(client):
    assert client.get("/api/v1/chat/sessions").status_code == 401


def test_list_sessions(authed_client, monkeypatch):
    fake = MagicMock()
    (fake.table.return_value
        .select.return_value
        .eq.return_value
        .order.return_value
        .limit.return_value
        .execute.return_value.data) = [{
        "id": "22222222-2222-2222-2222-222222222222",
        "title": "Optics Q&A",
        "created_at": "2026-01-01T00:00:00+00:00",
        "updated_at": "2026-01-01T01:00:00+00:00",
    }]
    monkeypatch.setattr("app.services.chat_service.get_supabase", lambda: fake)

    r = authed_client.get("/api/v1/chat/sessions")
    assert r.status_code == 200
    assert r.json()[0]["title"] == "Optics Q&A"
