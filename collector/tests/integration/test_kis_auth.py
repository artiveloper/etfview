from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from postgrest import APIError

from etf_collector.config import Settings
from etf_collector.infra.kis.auth import KisAuthManager


def _settings() -> Settings:
    return Settings(
        kis_app_key="key",
        kis_app_secret="secret",
        supabase_url="https://x.supabase.co",
        supabase_secret_key="secret",
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


async def test_acquires_lock_issues_token_and_releases_lock() -> None:
    supabase = MagicMock()
    supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
    update_eq = supabase.table.return_value.update.return_value.eq
    update_eq.return_value.or_.return_value.execute.return_value.data = [{"id": 1}]

    http_client = AsyncMock()
    response = MagicMock()
    response.json.return_value = {"access_token": "new-token", "expires_in": 86400}
    http_client.post.return_value = response

    manager = KisAuthManager(_settings(), supabase, http_client)
    token = await manager.get_access_token()

    assert token == "new-token"
    update_calls = supabase.table.return_value.update.call_args_list
    acquire_payload = update_calls[0].args[0]
    assert acquire_payload["lock_owner_identifier"]
    release_payload = update_calls[-1].args[0]
    assert release_payload["lock_owner_identifier"] is None
    assert release_payload["lock_expiration_time"] is None


async def test_polls_cache_when_lock_held_by_another_process() -> None:
    supabase = MagicMock()

    empty_result = MagicMock(data=[])
    other_process_expires_at = datetime.now(UTC) + timedelta(hours=1)
    valid_result = MagicMock(
        data=[
            {
                "access_token": "other-process-token",
                "expires_at": other_process_expires_at.isoformat(),
            }
        ]
    )
    select_execute = supabase.table.return_value.select.return_value.eq.return_value.execute
    select_execute.side_effect = [empty_result, empty_result, valid_result]

    # 다른 프로세스가 이미 락을 보유 중 — UPDATE where 조건이 매치되지 않는다.
    lock_update_eq = supabase.table.return_value.update.return_value.eq
    lock_update_eq.return_value.or_.return_value.execute.return_value.data = []
    supabase.table.return_value.insert.return_value.execute.side_effect = APIError(
        {"message": "duplicate key value", "code": "23505"}
    )

    http_client = AsyncMock()

    manager = KisAuthManager(_settings(), supabase, http_client)
    with patch("etf_collector.infra.kis.auth.asyncio.sleep", new=AsyncMock()):
        token = await manager.get_access_token()

    assert token == "other-process-token"
    http_client.post.assert_not_called()
