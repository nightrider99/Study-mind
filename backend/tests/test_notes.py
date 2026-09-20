from unittest.mock import MagicMock


def test_notes_requires_auth(client):
    r = client.get("/api/v1/notes")
    assert r.status_code == 401
    # error taxonomy shape
    assert "error" in r.json() or "detail" in r.json()


def test_list_notes(authed_client, monkeypatch):
    row = {
        "id": "11111111-1111-1111-1111-111111111111",
        "user_id": "00000000-0000-0000-0000-000000000001",
        "title": "Kinematics",
        "content": "v = u + at",
        "tags": ["physics"],
        "created_at": "2026-01-01T00:00:00+00:00",
        "updated_at": "2026-01-01T00:00:00+00:00",
    }
    fake = MagicMock()
    (fake.table.return_value
        .select.return_value
        .eq.return_value
        .order.return_value
        .execute.return_value.data) = [row]

    monkeypatch.setattr("app.api.routes.notes.get_supabase", lambda: fake)

    r = authed_client.get("/api/v1/notes")
    assert r.status_code == 200
    assert len(r.json()) == 1
    assert r.json()[0]["title"] == "Kinematics"
