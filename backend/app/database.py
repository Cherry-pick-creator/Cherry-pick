from supabase import create_client, Client

from app.config import settings

_client: Client | None = None


def get_supabase() -> Client:
    """Lazy-init Supabase client (avoids crash at import with placeholder keys)."""
    global _client
    if _client is None:
        _client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    return _client


class _LazySupabase:
    """Proxy that defers Supabase client creation to first attribute access."""

    def __getattr__(self, name: str):
        return getattr(get_supabase(), name)


supabase: Client = _LazySupabase()  # type: ignore[assignment]
