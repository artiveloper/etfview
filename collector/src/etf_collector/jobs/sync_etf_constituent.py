"""3단계: ETF 구성종목시세 API로 종목별 보유 바스켓을 조회해 upsert한다.

종목마다 1회 호출이 필요하므로 sync_etf_price와 동일하게 유니버스를
asyncio.gather로 병렬 조회하고(클라이언트가 유량을 페이싱한다), 개별 종목
실패는 경고만 남기고 나머지를 계속 적재한다.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import date

from etf_collector.domain.etf.constituent import EtfConstituent
from etf_collector.infra.kis.auth import KisAuthManager
from etf_collector.infra.kis.client import KisApiClient
from etf_collector.infra.kis.etf_constituent import fetch_constituents, map_to_constituent_rows
from etf_collector.infra.supabase.etf_constituent_repository import EtfConstituentRepository
from etf_collector.infra.supabase.etf_repository import EtfInfoRepository

logger = logging.getLogger(__name__)


async def _fetch_one(
    api_client: KisApiClient, token: str, short_code: str, reference_date: date
) -> list[EtfConstituent]:
    output2 = await fetch_constituents(api_client, token, short_code)
    return map_to_constituent_rows(short_code, reference_date, output2)


async def sync_etf_constituent(
    repository: EtfConstituentRepository,
    etf_repository: EtfInfoRepository,
    auth_manager: KisAuthManager,
    api_client: KisApiClient,
) -> int:
    universe = etf_repository.fetch_all()
    logger.info("구성종목 동기화 대상 ETF %d건", len(universe))
    if not universe:
        return 0

    token = await auth_manager.get_access_token()
    reference_date = date.today()

    results = await asyncio.gather(
        *(_fetch_one(api_client, token, etf.short_code, reference_date) for etf in universe),
        return_exceptions=True,
    )

    rows: list[EtfConstituent] = []
    for etf, result in zip(universe, results, strict=True):
        if isinstance(result, BaseException):
            logger.warning("종목 %s 구성종목 동기화 실패: %s", etf.short_code, result)
            continue
        rows.extend(result)

    count = repository.upsert_many(rows)
    logger.info("Supabase etf_constituent %d건 upsert 완료", count)
    return count
