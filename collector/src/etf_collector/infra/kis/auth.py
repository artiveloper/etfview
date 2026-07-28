"""KIS 접근토큰 발급, 캐싱, 폐기.

KIS는 토큰 재발급 빈도에 제한이 있어(분당 1회 수준) 컨테이너가 재시작될 때마다
새로 발급받으면 안 된다. 만료 시각보다 여유(_EXPIRY_SAFETY_MARGIN)를 두고
Supabase `kis_token_cache` 테이블에 저장된 토큰을 재사용해, 컨테이너 재시작에도
불필요한 재발급이 일어나지 않게 한다.

인스턴스가 여러 개로 늘어나는 상황을 대비해, 토큰 재발급 자체는 `kis_token_cache`
행에 대한 조건부 UPDATE 기반 리스(lease) 락으로 동시성을 제어한다. Supabase는
PostgREST 경유이고 흔히 pgbouncer transaction-mode 풀링을 쓰기 때문에 세션 단위인
`pg_advisory_lock`은 호출마다 다른 커넥션에 걸릴 수 있어 안전하지 않다 — 그래서
행 잠금(lease) 패턴을 쓴다.
"""

from __future__ import annotations

import asyncio
import os
import socket
from datetime import UTC, datetime, timedelta
from typing import Any, cast
from uuid import uuid4

from postgrest import APIError

from etf_collector.config import Settings
from etf_collector.infra.kis.client import KisApiClient
from supabase import Client

_TOKEN_CACHE_TABLE = "kis_token_cache"
_TOKEN_ROW_ID = 1
_EXPIRY_SAFETY_MARGIN = timedelta(minutes=10)

_LOCK_LEASE_DURATION = timedelta(seconds=30)
_LOCK_POLL_INTERVAL_SECONDS = 0.5
_LOCK_POLL_MAX_ATTEMPTS = 10  # 최대 5초 대기 후 락 재획득 시도


def _new_lock_owner_identifier() -> str:
    return f"{socket.gethostname()}:{os.getpid()}:{uuid4()}"


class KisAuthManager:
    def __init__(self, settings: Settings, supabase: Client, api_client: KisApiClient) -> None:
        self._settings = settings
        self._supabase = supabase
        self._api_client = api_client

    async def get_access_token(self) -> str:
        token = self._valid_cached_token()
        if token is not None:
            return token
        return await self._issue_and_cache_token_with_lock()

    async def revoke_token(self) -> None:
        """부여받은 접근토큰을 폐기하고 캐시에서 제거한다 (정상 종료 시 사용)."""
        cached = self._read_cache()
        if cached is None:
            return
        token, _ = cached
        await self._api_client.revoke_token(token)
        self._supabase.table(_TOKEN_CACHE_TABLE).delete().eq("id", _TOKEN_ROW_ID).execute()

    def _valid_cached_token(self) -> str | None:
        cached = self._read_cache()
        if cached is None:
            return None
        token, expires_at = cached
        if expires_at - _EXPIRY_SAFETY_MARGIN > datetime.now(UTC):
            return token
        return None

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
        if not access_token:
            return None
        return access_token, datetime.fromisoformat(expires_at)

    async def _issue_and_cache_token_with_lock(self) -> str:
        owner = _new_lock_owner_identifier()
        if self._acquire_lock(owner):
            try:
                return await self._issue_and_cache_token()
            finally:
                self._release_lock(owner)

        # 다른 프로세스가 락을 보유 중 — 그 프로세스가 곧 갱신할 캐시를 짧게 폴링한다.
        for _ in range(_LOCK_POLL_MAX_ATTEMPTS):
            await asyncio.sleep(_LOCK_POLL_INTERVAL_SECONDS)
            token = self._valid_cached_token()
            if token is not None:
                return token

        # 폴링이 끝나도 유효한 토큰이 없다 — 락 소유자가 비정상 종료됐을 가능성이 높으므로
        # 리스가 만료됐다면(_acquire_lock의 WHERE 조건) 직접 재획득을 한 번 더 시도한다.
        if self._acquire_lock(owner):
            try:
                return await self._issue_and_cache_token()
            finally:
                self._release_lock(owner)
        raise RuntimeError("KIS 접근토큰 발급 락을 획득하지 못했습니다")

    def _acquire_lock(self, owner: str) -> bool:
        now = datetime.now(UTC)
        lease_expires_at = now + _LOCK_LEASE_DURATION
        result = (
            self._supabase.table(_TOKEN_CACHE_TABLE)
            .update(
                {
                    "lock_owner_identifier": owner,
                    "lock_expiration_time": lease_expires_at.isoformat(),
                }
            )
            .eq("id", _TOKEN_ROW_ID)
            .or_(f"lock_expiration_time.is.null,lock_expiration_time.lt.{now.isoformat()}")
            .execute()
        )
        if result.data:
            return True

        # kis_token_cache에 행이 아직 없는 최초 실행 상황 — INSERT로 락을 선점한다.
        try:
            self._supabase.table(_TOKEN_CACHE_TABLE).insert(
                {
                    "id": _TOKEN_ROW_ID,
                    "access_token": "",
                    "expires_at": now.isoformat(),
                    "lock_owner_identifier": owner,
                    "lock_expiration_time": lease_expires_at.isoformat(),
                }
            ).execute()
            return True
        except APIError:
            # 동시에 다른 프로세스가 먼저 행을 만들었다 — 그쪽이 락을 가져간 것으로 본다.
            return False

    def _release_lock(self, owner: str) -> None:
        self._supabase.table(_TOKEN_CACHE_TABLE).update(
            {"lock_owner_identifier": None, "lock_expiration_time": None}
        ).eq("id", _TOKEN_ROW_ID).eq("lock_owner_identifier", owner).execute()

    async def _issue_and_cache_token(self) -> str:
        body = await self._api_client.issue_token()
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
