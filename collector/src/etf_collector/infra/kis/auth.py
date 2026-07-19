"""KIS 접근토큰 발급 및 캐싱.

KIS는 토큰 재발급 빈도에 제한이 있어(분당 1회 수준) 컨테이너가 재시작될 때마다
새로 발급받으면 안 된다. 만료 시각보다 여유(_EXPIRY_SAFETY_MARGIN)를 두고
Supabase `kis_token_cache` 테이블에 저장된 토큰을 재사용해, 컨테이너 재시작에도
불필요한 재발급이 일어나지 않게 한다.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any, cast

import httpx

from etf_collector.config import Settings
from supabase import Client

_TOKEN_CACHE_TABLE = "kis_token_cache"
_TOKEN_ROW_ID = 1
_EXPIRY_SAFETY_MARGIN = timedelta(minutes=10)


class KisAuthManager:
    def __init__(
        self, settings: Settings, supabase: Client, http_client: httpx.AsyncClient
    ) -> None:
        self._settings = settings
        self._supabase = supabase
        self._http = http_client

    async def get_access_token(self) -> str:
        cached = self._read_cache()
        if cached is not None:
            token, expires_at = cached
            if expires_at - _EXPIRY_SAFETY_MARGIN > datetime.now(UTC):
                return token
        return await self._issue_and_cache_token()

    def _read_cache(self) -> tuple[str, datetime] | None:
        result = (
            self._supabase.table(_TOKEN_CACHE_TABLE)
            .select("access_token, expires_at")
            .eq("id", _TOKEN_ROW_ID)
            .execute()
        )
        if not result.data:
            return None
        row = cast(dict[str, Any], result.data[0])
        access_token = row["access_token"]
        expires_at = row["expires_at"]
        assert isinstance(access_token, str)
        assert isinstance(expires_at, str)
        return access_token, datetime.fromisoformat(expires_at)

    async def _issue_and_cache_token(self) -> str:
        response = await self._http.post(
            f"{self._settings.kis_base_url}/oauth2/tokenP",
            json={
                "grant_type": "client_credentials",
                "appkey": self._settings.kis_app_key,
                "appsecret": self._settings.kis_app_secret,
            },
        )
        response.raise_for_status()
        body = response.json()
        access_token: str = body["access_token"]
        issued_at = datetime.now(UTC)
        expires_at = issued_at + timedelta(seconds=int(body["expires_in"]))

        self._supabase.table(_TOKEN_CACHE_TABLE).upsert(
            {
                "id": _TOKEN_ROW_ID,
                "access_token": access_token,
                "expires_at": expires_at.isoformat(),
                "updated_at": issued_at.isoformat(),
            }
        ).execute()

        return access_token
