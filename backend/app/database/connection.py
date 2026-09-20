from functools import lru_cache
from supabase import create_client, Client
from app.core.config import settings

@lru_cache
def get_supabase() -> Client:
    """Service-role client — bypasses RLS. Server-side only."""
    return create_client(settings.supabase_url, settings.supabase_service_role_key)
