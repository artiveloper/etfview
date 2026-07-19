"""KIS 인증 API 호출용 httpx 래퍼.

종목별 상세정보(enrichment) 단계에서 종목 수만큼 호출이 반복되므로,
세마포어로 동시 요청 수를 제한해 KIS 초당 호출 제한을 넘지 않도록 한다.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx

from etf_collector.config import Settings

logger = logging.getLogger(__name__)

# KIS 실전 계좌 기준 초당 호출 제한(약 20건/초)에 여유를 두고 동시 요청 수를 제한한다.
_MAX_CONCURRENT_REQUESTS = 15
_MAX_RETRIES = 2


class KisApiClient:
    def __init__(self, settings: Settings, http_client: httpx.AsyncClient) -> None:
        self._settings = settings
        self._http = http_client
        self._semaphore = asyncio.Semaphore(_MAX_CONCURRENT_REQUESTS)

    async def get(
        self, path: str, tr_id: str, token: str, params: dict[str, str]
    ) -> dict[str, Any]:
        headers = {
            "content-type": "application/json; charset=utf-8",
            "authorization": f"Bearer {token}",
            "appkey": self._settings.kis_app_key,
            "appsecret": self._settings.kis_app_secret,
            "tr_id": tr_id,
        }
        url = f"{self._settings.kis_base_url}{path}"

        async with self._semaphore:
            last_error: httpx.HTTPError | None = None
            for attempt in range(1, _MAX_RETRIES + 2):
                try:
                    response = await self._http.get(url, headers=headers, params=params)
                    response.raise_for_status()
                    result: dict[str, Any] = response.json()
                    return result
                except httpx.HTTPError as exc:
                    last_error = exc
                    logger.warning(
                        "KIS API 호출 실패 (attempt=%d/%d, tr_id=%s): %s",
                        attempt,
                        _MAX_RETRIES + 1,
                        tr_id,
                        exc,
                    )
            assert last_error is not None
            raise last_error
