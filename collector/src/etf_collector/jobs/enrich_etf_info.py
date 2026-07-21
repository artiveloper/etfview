"""2단계: sync_etf_info로 채워진 ETF 유니버스에 KIS 현재가 API로 시세 스냅샷을 채운다.

종목별 API 호출은 KisApiClient 내부 세마포어로 동시성이 제한되지만, Supabase
upsert는 종목마다 개별 호출하지 않고 전체 결과를 모아 한 번에 배치 upsert한다
(N+1 방지, db-architecture 원칙).
"""

from __future__ import annotations

import asyncio
import logging

from etf_collector.domain.etf.models import EtfQuote
from etf_collector.infra.kis.auth import KisAuthManager
from etf_collector.infra.kis.client import KisApiClient
from etf_collector.infra.kis.etf_quote import fetch_etf_quote, map_to_etf_quote_fields
from etf_collector.infra.supabase.etf_quote_repository import EtfQuoteRepository
from etf_collector.infra.supabase.etf_repository import EtfInfoRepository

logger = logging.getLogger(__name__)


async def _fetch_one(api_client: KisApiClient, token: str, short_code: str) -> EtfQuote:
    quote = await fetch_etf_quote(api_client, token, short_code)
    quote_fields = map_to_etf_quote_fields(quote)
    return EtfQuote(short_code=short_code, **quote_fields)


async def enrich_etf_info(
    repository: EtfInfoRepository,
    quote_repository: EtfQuoteRepository,
    auth_manager: KisAuthManager,
    api_client: KisApiClient,
) -> int:
    universe = repository.fetch_all()
    logger.info("enrichment 대상 ETF %d건", len(universe))
    if not universe:
        return 0

    token = await auth_manager.get_access_token()

    results = await asyncio.gather(
        *(_fetch_one(api_client, token, etf.short_code) for etf in universe),
        return_exceptions=True,
    )

    quote_rows: list[EtfQuote] = []
    for etf, result in zip(universe, results, strict=True):
        if isinstance(result, BaseException):
            logger.warning("종목 %s enrichment 실패: %s", etf.short_code, result)
            continue
        quote_rows.append(result)

    quote_count = quote_repository.upsert_many(quote_rows)
    logger.info("Supabase etf_quote %d건 upsert 완료", quote_count)

    return quote_count
