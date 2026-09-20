import os

# Must be set before any app import — Settings() runs at module import time.
os.environ.setdefault("SUPABASE_URL", "http://test.local")
os.environ.setdefault("SUPABASE_ANON_KEY", "test")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "test")
os.environ.setdefault("GEMINI_API_KEY", "test")

import pytest
from fastapi.testclient import TestClient

from app.core.security import get_current_user_id
from app.main import app

TEST_USER_ID = "00000000-0000-0000-0000-000000000001"


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def authed_client():
    app.dependency_overrides[get_current_user_id] = lambda: TEST_USER_ID
    yield TestClient(app)
    app.dependency_overrides.clear()
