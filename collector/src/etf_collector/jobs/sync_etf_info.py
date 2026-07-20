"""KRX 데이터포털 ETF 전종목 기본정보 → EtfInfo → Supabase etf upsert.

기초지수/지수산출기관/복제방법/운용사/CU수량/총보수/과세유형 등 정적 필드가 이
한 번의 조회로 함께 채워진다. 추적배수(tracking_multiplier)만 이 응답에 없어
enrich_etf_info(KIS 현재가 API)에서 보강한다.
"""

import logging

import httpx

from etf_collector.config import Settings
from etf_collector.infra.krx.auth import login
from etf_collector.infra.krx.etf_info import fetch_etf_universe
from etf_collector.infra.supabase.etf_repository import EtfInfoRepository

logger = logging.getLogger(__name__)


async def sync_etf_info(
    repository: EtfInfoRepository, settings: Settings, http_client: httpx.AsyncClient
) -> int:
    await login(http_client, settings)
    etfs = await fetch_etf_universe(http_client)
    logger.info("KRX에서 ETF %d건 조회", len(etfs))

    count = repository.upsert_many(etfs)
    logger.info("Supabase etf %d건 upsert 완료", count)
    return count
