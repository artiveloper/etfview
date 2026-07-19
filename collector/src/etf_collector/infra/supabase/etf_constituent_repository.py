# etf_constituent 테이블 접근 리포지토리
from etf_collector.domain.etf.constituent import EtfConstituent
from supabase import Client

_TABLE = "etf_constituent"


class EtfConstituentRepository:
    def __init__(self, supabase: Client) -> None:
        self._supabase = supabase

    def upsert_many(self, rows: list[EtfConstituent]) -> int:
        if not rows:
            return 0
        payload = [row.model_dump(mode="json") for row in rows]
        self._supabase.table(_TABLE).upsert(
            payload, on_conflict="etf_short_code,constituent_short_code"
        ).execute()
        return len(payload)
