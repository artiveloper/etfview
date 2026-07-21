"""KRX 데이터포털 ETF 전종목 기본정보 → EtfInfo → Supabase etf upsert.

기초지수/지수산출기관/추적배수/복제방법/운용사/CU수량/총보수/과세유형 등 정적
필드가 이 한 번의 조회로 함께 채워진다. KRX가 이번 조회에 더는 반환하지 않는
기존 종목은 상장폐지된 것으로 보고 delisted_at을 채운다.
"""

import logging
from datetime import date

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

    krx_codes = {etf.short_code for etf in etfs}
    existing = repository.fetch_all()
    delisted_codes = [etf.short_code for etf in existing if etf.short_code not in krx_codes]
    if delisted_codes:
        marked = repository.mark_delisted(delisted_codes, date.today())
        logger.info("상장폐지 감지 %d건 (delisted_at 기록)", marked)

    return count
