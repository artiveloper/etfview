from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

from etf_collector.config import Settings
from etf_collector.infra.kis.auth import KisAuthManager


def _settings() -> Settings:
    return Settings(
        kis_app_key="key",
        kis_app_secret="secret",
        supabase_url="https://x.supabase.co",
        supabase_service_role_key="secret",
    )


async def test_returns_cached_token_when_still_valid() -> None:
    supabase = MagicMock()
    expires_at = datetime.now(UTC) + timedelta(hours=1)
    supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
        {"access_token": "cached-token", "expires_at": expires_at.isoformat()}
    ]
    http_client = AsyncMock()

    manager = KisAuthManager(_settings(), supabase, http_client)
    token = await manager.get_access_token()

    assert token == "cached-token"
    http_client.post.assert_not_called()


async def test_issues_and_caches_new_token_when_cache_empty() -> None:
    supabase = MagicMock()
    supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []

    http_client = AsyncMock()
    response = MagicMock()
    response.json.return_value = {"access_token": "new-token", "expires_in": 86400}
    http_client.post.return_value = response

    manager = KisAuthManager(_settings(), supabase, http_client)
    token = await manager.get_access_token()

    assert token == "new-token"
    http_client.post.assert_called_once()
    supabase.table.return_value.upsert.assert_called_once()
