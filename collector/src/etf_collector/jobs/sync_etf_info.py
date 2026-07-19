"""1차 스코프: KIS 마스터파일 → EtfInfo(부분 필드) → Supabase etf_info upsert.

기초지수/지수산출기관/복제방법/운용사/CU수량/총보수/과세유형 등 나머지 필드는
종목별 KIS 상세 API를 붙이는 후속 enrichment job에서 채운다.
"""

import logging

from etf_collector.infra.kis.master_file import fetch_etf_universe
from etf_collector.infra.supabase.etf_repository import EtfInfoRepository

logger = logging.getLogger(__name__)


async def sync_etf_info(repository: EtfInfoRepository) -> int:
    etfs = await fetch_etf_universe()
    logger.info("KIS 마스터파일에서 ETF %d건 조회", len(etfs))

    count = repository.upsert_many(etfs)
    logger.info("Supabase etf_info %d건 upsert 완료", count)
    return count
