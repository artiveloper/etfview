"""3단계: KIS 구성종목 데이터 소스 → EtfConstituent 목록 → Supabase upsert.

infra/kis/etf_constituent.py의 다운로드/파서가 아직 미구현(NotImplementedError)이므로,
실제 스펙이 확보되기 전까지 이 job은 예외를 그대로 전파한다. 파서만 채워지면
이 job은 변경 없이 그대로 동작한다.
"""

import logging

from etf_collector.infra.kis.etf_constituent import fetch_etf_constituents
from etf_collector.infra.supabase.etf_constituent_repository import EtfConstituentRepository

logger = logging.getLogger(__name__)


async def sync_etf_constituent(repository: EtfConstituentRepository) -> int:
    constituents = await fetch_etf_constituents()
    logger.info("구성종목 %d건 조회", len(constituents))

    count = repository.upsert_many(constituents)
    logger.info("Supabase etf_constituent %d건 upsert 완료", count)
    return count
