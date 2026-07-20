"""3단계: ETF 구성종목시세 API로 ETF별 보유종목 현황을 upsert한다.

조회 대상 ETF 목록은 별도 마스터파일이 아니라 이미 수집된 Supabase etf
테이블(EtfInfoRepository.fetch_all)에서 가져온다 — 이 API는 종목코드 하나당
1회 호출하는 구조라 sync_etf_price.py와 동일한 universe-순회 패턴을 따른다.
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
    return map_to_constituent_rows(short_code, output2, reference_date)


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
