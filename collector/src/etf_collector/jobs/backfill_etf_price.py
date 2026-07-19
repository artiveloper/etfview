"""1회성 온디맨드 백필: 최근 N일(기본 365일)치 일별 주가를 종목별로 소급 수집한다.

KIS API가 호출당 최대 약 100거래일치만 반환하므로, 종목별로 날짜 범위를
90일 단위 윈도우로 나눠 여러 번 호출한다. 정기 파이프라인(sync_etf_price)과
달리 이 잡은 CLI --backfill-price-history로만 실행되는 별도 온디맨드 작업이다.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import date, timedelta

from etf_collector.domain.etf.models import EtfInfo, EtfPrice
from etf_collector.infra.kis.auth import KisAuthManager
from etf_collector.infra.kis.client import KisApiClient
from etf_collector.infra.kis.price import fetch_price, map_to_price_rows
from etf_collector.infra.supabase.etf_price_repository import EtfPriceRepository
from etf_collector.infra.supabase.etf_repository import EtfInfoRepository

logger = logging.getLogger(__name__)

_WINDOW_DAYS = 90


def iter_backfill_windows(
    start_bound: date, today: date, window_days: int = _WINDOW_DAYS
) -> list[tuple[date, date]]:
    """today부터 start_bound까지 window_days일 단위로 역순 분할한 (시작일, 종료일) 목록."""
    if start_bound > today:
        return []
    windows: list[tuple[date, date]] = []
    window_end = today
    while window_end >= start_bound:
        window_start = max(window_end - timedelta(days=window_days - 1), start_bound)
        windows.append((window_start, window_end))
        window_end = window_start - timedelta(days=1)
    return windows


async def _backfill_one(
    api_client: KisApiClient, token: str, etf: EtfInfo, target_start: date, today: date
) -> list[EtfPrice]:
    start_bound = max(etf.listed_date, target_start) if etf.listed_date else target_start
    rows: list[EtfPrice] = []
    for window_start, window_end in iter_backfill_windows(start_bound, today):
        output2 = await fetch_price(api_client, token, etf.short_code, window_start, window_end)
        rows.extend(map_to_price_rows(etf.short_code, output2))
    return rows


async def backfill_etf_price(
    repository: EtfPriceRepository,
    etf_repository: EtfInfoRepository,
    auth_manager: KisAuthManager,
    api_client: KisApiClient,
    days_back: int = 365,
) -> int:
    universe = etf_repository.fetch_all()
    logger.info("주가 백필 대상 ETF %d건 (최근 %d일)", len(universe), days_back)
    if not universe:
        return 0

    token = await auth_manager.get_access_token()
    today = date.today()
    target_start = today - timedelta(days=days_back)

    results = await asyncio.gather(
        *(_backfill_one(api_client, token, etf, target_start, today) for etf in universe),
        return_exceptions=True,
    )

    rows: list[EtfPrice] = []
    for etf, result in zip(universe, results, strict=True):
        if isinstance(result, BaseException):
            logger.warning("종목 %s 주가 백필 실패: %s", etf.short_code, result)
            continue
        rows.extend(result)

    count = repository.upsert_many(rows)
    logger.info("Supabase etf_price 백필 %d건 upsert 완료", count)
    return count
