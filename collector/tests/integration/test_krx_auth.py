from unittest.mock import AsyncMock, MagicMock

import pytest

from etf_collector.config import Settings
from etf_collector.infra.krx.auth import login


def _settings() -> Settings:
    return Settings(
        kis_app_key="key",
        kis_app_secret="secret",
        krx_username="krx-id",
        krx_password="krx-pw",
        supabase_url="https://x.supabase.co",
        supabase_secret_key="secret",
    )


def _response(error_code: str, error_message: str = "") -> MagicMock:
    response = MagicMock()
    response.raise_for_status.return_value = None
    response.json.return_value = {"_error_code": error_code, "_error_message": error_message}
    return response


async def test_login_succeeds_on_cd001() -> None:
    http_client = AsyncMock()
    http_client.post.return_value = _response("CD001", "정상")

    await login(http_client, _settings())

    http_client.get.assert_called_once()
    http_client.post.assert_called_once()
    _, kwargs = http_client.post.call_args
    assert kwargs["data"]["mbrId"] == "krx-id"
    assert kwargs["data"]["pw"] == "krx-pw"


async def test_login_raises_on_duplicate_login() -> None:
    http_client = AsyncMock()
    http_client.post.return_value = _response("CD011", "중복 로그인")

    with pytest.raises(RuntimeError, match="중복 로그인"):
        await login(http_client, _settings())
