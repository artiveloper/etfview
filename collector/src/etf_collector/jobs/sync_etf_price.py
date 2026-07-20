"""3단계: 국내주식기간별시세 API로 최근 며칠치 일별 주가(OHLCV)를 upsert한다.

날짜 범위를 최근 7일로 잡아 주말·공휴일 이후에도 놓치는 거래일 없이
자연스럽게 재보정되도록 한다. 같은 (short_code, trade_date) 조합은
upsert라 중복 호출해도 안전하다.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import date, timedelta

from etf_collector.domain.etf.models import EtfPrice
from etf_collector.infra.kis.auth import KisAuthManager
from etf_collector.infra.kis.client import KisApiClient
from etf_collector.infra.kis.price import fetch_price, map_to_price_rows
from etf_collector.infra.supabase.etf_price_repository import EtfPriceRepository
from etf_collector.infra.supabase.etf_repository import EtfInfoRepository

logger = logging.getLogger(__name__)

_SYNC_WINDOW_DAYS = 7


async def _fetch_one(
    api_client: KisApiClient, token: str, short_code: str, date_from: date, date_to: date
) -> list[EtfPrice]:
    output2 = await fetch_price(api_client, token, short_code, date_from, date_to)
    return map_to_price_rows(short_code, output2)


async def sync_etf_price(
    repository: EtfPriceRepository,
    etf_repository: EtfInfoRepository,
    auth_manager: KisAuthManager,
    api_client: KisApiClient,
    window_days: int = _SYNC_WINDOW_DAYS,
) -> int:
    """최근 window_days일치 일별 주가를 동기화한다.

    장 마감 후 정기 실행은 기본 7일 창으로 주말·공휴일 이후 누락을 재보정하고,
    장중 30분 주기 실행은 window_days=0으로 오늘 하루만 좁혀 미완성 봉만 갱신한다.
    """
    universe = etf_repository.fetch_all()
    logger.info("주가 동기화 대상 ETF %d건 (최근 %d일)", len(universe), window_days)
    if not universe:
        return 0

    token = await auth_manager.get_access_token()
    date_to = date.today()
    date_from = date_to - timedelta(days=window_days)

    results = await asyncio.gather(
        *(_fetch_one(api_client, token, etf.short_code, date_from, date_to) for etf in universe),
        return_exceptions=True,
    )

    rows: list[EtfPrice] = []
    for etf, result in zip(universe, results, strict=True):
        if isinstance(result, BaseException):
            logger.warning("종목 %s 주가 동기화 실패: %s", etf.short_code, result)
            continue
        rows.extend(result)

    count = repository.upsert_many(rows)
    logger.info("Supabase etf_price %d건 upsert 완료", count)
    return count
