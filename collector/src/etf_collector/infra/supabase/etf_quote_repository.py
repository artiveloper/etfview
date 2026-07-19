from etf_collector.domain.etf.models import EtfQuote
from supabase import Client

_TABLE = "etf_quote"


class EtfQuoteRepository:
    def __init__(self, supabase: Client) -> None:
        self._supabase = supabase

    def upsert_many(self, rows: list[EtfQuote]) -> int:
        if not rows:
            return 0
        payload = [row.model_dump(mode="json") for row in rows]
        self._supabase.table(_TABLE).upsert(payload, on_conflict="short_code").execute()
        return len(payload)
