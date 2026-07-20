from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from etf_collector.config import Settings
from etf_collector.infra.kis.client import KisApiClient
from etf_collector.infra.kis.errors import KisApiError, KisRateLimitError


def _settings() -> Settings:
    return Settings(
        kis_app_key="key",
        kis_app_secret="secret",
        krx_username="krx-id",
        krx_password="krx-pw",
        supabase_url="https://x.supabase.co",
        supabase_secret_key="secret",
    )


def _response(
    rt_cd: str, msg_cd: str = "", msg1: str = "", output: dict | None = None
) -> MagicMock:
    response = MagicMock()
    response.raise_for_status.return_value = None
    response.json.return_value = {
        "rt_cd": rt_cd,
        "msg_cd": msg_cd,
        "msg1": msg1,
        "output": output or {},
    }
    return response


async def test_get_returns_output_on_success() -> None:
    http_client = AsyncMock()
    http_client.get.return_value = _response("0", output={"stck_prpr": "36090"})

    client = KisApiClient(_settings(), http_client)
    result = await client.get("/path", "TR001", "token", {})

    assert result["output"]["stck_prpr"] == "36090"
    http_client.get.assert_called_once()


async def test_get_retries_on_rate_limit_then_succeeds() -> None:
    http_client = AsyncMock()
    http_client.get.side_effect = [
        _response("1", "EGW00201", "초당 거래건수를 초과하였습니다"),
        _response("0", output={"stck_prpr": "36090"}),
    ]

    client = KisApiClient(_settings(), http_client)
    with patch("etf_collector.infra.kis.client.asyncio.sleep", new=AsyncMock()):
        result = await client.get("/path", "TR001", "token", {})

    assert result["output"]["stck_prpr"] == "36090"
    assert http_client.get.call_count == 2


async def test_get_raises_rate_limit_error_after_max_retries() -> None:
    http_client = AsyncMock()
    http_client.get.return_value = _response("1", "EGW00201", "초당 거래건수를 초과하였습니다")

    client = KisApiClient(_settings(), http_client)
    with (
        patch("etf_collector.infra.kis.client.asyncio.sleep", new=AsyncMock()),
        pytest.raises(KisRateLimitError),
    ):
        await client.get("/path", "TR001", "token", {})


async def test_get_raises_business_error_without_retry() -> None:
    http_client = AsyncMock()
    http_client.get.return_value = _response("1", "APBK0919", "존재하지 않는 종목입니다")

    client = KisApiClient(_settings(), http_client)
    with pytest.raises(KisApiError):
        await client.get("/path", "TR001", "token", {})

    http_client.get.assert_called_once()
