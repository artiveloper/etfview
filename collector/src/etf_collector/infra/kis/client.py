"""KIS 인증 API 호출용 httpx 래퍼.

종목별 상세정보(enrichment) 단계에서 종목 수만큼 호출이 반복되므로,
세마포어로 동시 요청 수를 제한하고, 실제 호출 시점 사이에도 최소 간격을
둬 KIS 공식 유량 제한(REST 실전 1초당 18건, 2023-10-27 변경)을 넘지
않도록 한다. 세마포어만으로는 동시에 들어온 짧은 응답들이 순간적으로
초당 건수를 넘길 수 있어(응답이 빠르면 세마포어 슬롯이 곧바로 재사용됨),
KIS 공지에서 권장하는 "동시 호출 시 100~150ms 텀"을 실제 디스패치
시점에 강제하는 페이싱(pacing) 락을 함께 둔다.

KIS는 초당 호출 제한 초과 등 비즈니스 레벨 에러도 HTTP 200과 함께 응답 바디의
rt_cd(!='0')/msg_cd로 표현하므로, httpx.HTTPError(전송 계층 에러)만으로는
이를 감지할 수 없다. 그래서 응답 바디를 항상 파싱해 rt_cd를 확인하고,
msg_cd에 따라 재시도 가능한 rate limit 에러와 즉시 실패해야 할 비즈니스
에러를 구분한다. KIS 공지에 따르면 서버 내 분산 정책으로 정상 유량 이내의
호출도 간헐적으로 거부될 수 있어 "즉시 재호출"을 권장하므로, 첫 재시도는
거의 지연 없이 수행하고 반복될 때만 대기 시간을 늘린다.
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

import httpx

from etf_collector.config import Settings
from etf_collector.infra.kis.errors import KisApiError, KisAuthenticationError, KisRateLimitError

logger = logging.getLogger(__name__)

# KIS 실전 계좌 기준 초당 호출 제한은 18건(2023-10-27 변경, 계좌=앱키 단위)이다.
# 동시 요청 수 자체는 여유 있게 두되(응답 대기 구간의 오버랩 허용), 실제
# 디스패치 간격은 아래 _MIN_REQUEST_INTERVAL_SECONDS로 별도 통제한다.
_MAX_CONCURRENT_REQUESTS = 15
# KIS 공지 권장 동시 호출 텀(100~150ms)의 중간값. 이 간격을 강제하면
# 처리량은 최대 초당 약 8건으로 제한되어 18건/초 한도에 충분한 여유를 둔다.
_MIN_REQUEST_INTERVAL_SECONDS = 0.12
_MAX_TRANSPORT_RETRIES = 2
_MAX_RATE_LIMIT_RETRIES = 3
# 첫 재시도는 "서버 내 분산 정책" 오탈락을 가정해 거의 즉시 재호출하고,
# 반복되면 실제 유량 초과로 보고 대기 시간을 늘린다.
_RATE_LIMIT_BACKOFF_SECONDS = (0.1, 0.5, 1.5)

# 정확한 코드/문구는 제공된 docs에는 없고 KIS 개발자포럼에 공개된 값이다 —
# 실제 연동 전 최신 공지로 재확인이 필요하다.
_RATE_LIMIT_MSG_CODES = frozenset({"EGW00201"})
_TOKEN_ERROR_KEYWORDS = ("접근토큰", "token이 유효하지", "기간이 만료")

# /oauth2/tokenP는 KIS 공지(2023-10-27)상 초당 1건 제한이다. 호출측(KisAuthManager)의
# 리스 락으로 인스턴스 간 동시 재발급 자체를 막지만, 그럼에도 KIS 쪽 분산 정책 등으로
# 간헐적 403이 관측돼(2026-07-28) 짧은 대기 후 재시도한다.
_TOKEN_ISSUE_MAX_RETRIES = 2
_TOKEN_ISSUE_BACKOFF_SECONDS = (3.0, 10.0)


class KisApiClient:
    def __init__(self, settings: Settings, http_client: httpx.AsyncClient) -> None:
        self._settings = settings
        self._http = http_client
        self._semaphore = asyncio.Semaphore(_MAX_CONCURRENT_REQUESTS)
        self._pacing_lock = asyncio.Lock()
        self._last_dispatch_time: float = 0.0

    async def _wait_for_pacing_slot(self) -> None:
        """직전 디스패치로부터 최소 간격이 지날 때까지 대기한 뒤 디스패치 시각을 갱신한다.

        이 락은 세마포어로 허용된 동시 요청들 사이에서도 실제 HTTP 호출 시점
        자체가 몰리지 않도록 직렬화한다 — 계좌(앱키) 단위 유량 제한이므로
        인스턴스 내 모든 호출이 이 하나의 게이트를 공유해야 한다.
        """
        async with self._pacing_lock:
            now = time.monotonic()
            wait_seconds = self._last_dispatch_time + _MIN_REQUEST_INTERVAL_SECONDS - now
            if wait_seconds > 0:
                await asyncio.sleep(wait_seconds)
            self._last_dispatch_time = time.monotonic()

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
            transport_attempt = 0
            rate_limit_attempt = 0
            while True:
                await self._wait_for_pacing_slot()
                try:
                    response = await self._http.get(url, headers=headers, params=params)
                    response.raise_for_status()
                except httpx.HTTPError as exc:
                    transport_attempt += 1
                    if transport_attempt > _MAX_TRANSPORT_RETRIES:
                        raise
                    logger.warning(
                        "KIS API 전송 실패 (attempt=%d/%d, tr_id=%s): %s",
                        transport_attempt,
                        _MAX_TRANSPORT_RETRIES,
                        tr_id,
                        exc,
                    )
                    continue

                result: dict[str, Any] = response.json()
                if result.get("rt_cd") == "0":
                    return result

                msg_cd = str(result.get("msg_cd", ""))
                msg1 = str(result.get("msg1", ""))

                if msg_cd in _RATE_LIMIT_MSG_CODES:
                    rate_limit_attempt += 1
                    if rate_limit_attempt > _MAX_RATE_LIMIT_RETRIES:
                        raise KisRateLimitError(msg_cd, msg1)
                    backoff = _RATE_LIMIT_BACKOFF_SECONDS[
                        min(rate_limit_attempt, len(_RATE_LIMIT_BACKOFF_SECONDS)) - 1
                    ]
                    logger.warning(
                        "KIS rate limit 감지, %.1fs 대기 후 재시도 (attempt=%d/%d, tr_id=%s): %s",
                        backoff,
                        rate_limit_attempt,
                        _MAX_RATE_LIMIT_RETRIES,
                        tr_id,
                        msg1,
                    )
                    await asyncio.sleep(backoff)
                    continue

                if any(keyword in msg1 for keyword in _TOKEN_ERROR_KEYWORDS):
                    raise KisAuthenticationError(msg_cd, msg1)

                raise KisApiError(msg_cd, msg1)

    async def issue_token(self) -> dict[str, Any]:
        url = f"{self._settings.kis_base_url}/oauth2/tokenP"
        payload = {
            "grant_type": "client_credentials",
            "appkey": self._settings.kis_app_key,
            "appsecret": self._settings.kis_app_secret,
        }
        attempt = 0
        while True:
            response = await self._http.post(url, json=payload)
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError:
                attempt += 1
                logger.error(
                    "KIS 접근토큰 발급 실패 (attempt=%d/%d, status=%d): %s",
                    attempt,
                    _TOKEN_ISSUE_MAX_RETRIES,
                    response.status_code,
                    response.text,
                )
                if attempt > _TOKEN_ISSUE_MAX_RETRIES:
                    raise
                await asyncio.sleep(_TOKEN_ISSUE_BACKOFF_SECONDS[attempt - 1])
                continue
            body: dict[str, Any] = response.json()
            return body

    async def revoke_token(self, token: str) -> None:
        response = await self._http.post(
            f"{self._settings.kis_base_url}/oauth2/revokeP",
            json={
                "appkey": self._settings.kis_app_key,
                "appsecret": self._settings.kis_app_secret,
                "token": token,
            },
        )
        response.raise_for_status()
