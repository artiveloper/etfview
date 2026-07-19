from etf_collector.domain.etf.models import EtfPrice
from supabase import Client

_TABLE = "etf_price"
# 1년 백필은 종목당 최대 250여 행 × 1150종목 ≈ 수십만 행이 한 번에 모이므로,
# 단일 upsert 요청으로 보내면 Postgres statement_timeout에 걸린다. 청크로 나눠 보낸다.
_CHUNK_SIZE = 500


class EtfPriceRepository:
    def __init__(self, supabase: Client) -> None:
        self._supabase = supabase

    def upsert_many(self, rows: list[EtfPrice]) -> int:
        if not rows:
            return 0
        payload = [row.model_dump(mode="json") for row in rows]
        for i in range(0, len(payload), _CHUNK_SIZE):
            chunk = payload[i : i + _CHUNK_SIZE]
            self._supabase.table(_TABLE).upsert(
                chunk, on_conflict="short_code,trade_date"
            ).execute()
        return len(payload)
