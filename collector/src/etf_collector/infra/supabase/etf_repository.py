from datetime import date
from typing import Any

from etf_collector.domain.etf.models import EtfInfo
from supabase import Client

_TABLE = "etf"
# PostgREST 기본 max_rows(1000)를 넘으면 select("*")만으로는 앞 1000행에서
# 조용히 잘린다. .range()로 페이지 단위로 반복 조회해 전체를 모은다.
_PAGE_SIZE = 1000


class EtfInfoRepository:
    def __init__(self, supabase: Client) -> None:
        self._supabase = supabase

    def upsert_many(self, rows: list[EtfInfo]) -> int:
        if not rows:
            return 0
        payload = [row.model_dump(mode="json") for row in rows]
        self._supabase.table(_TABLE).upsert(payload, on_conflict="short_code").execute()
        return len(payload)

    def fetch_all(self) -> list[EtfInfo]:
        rows: list[Any] = []
        offset = 0
        while True:
            page = (
                self._supabase.table(_TABLE)
                .select("*")
                .range(offset, offset + _PAGE_SIZE - 1)
                .execute()
            )
            rows.extend(page.data)
            if len(page.data) < _PAGE_SIZE:
                break
            offset += _PAGE_SIZE
        return [EtfInfo.model_validate(row) for row in rows]

    def mark_delisted(self, short_codes: list[str], as_of: date) -> int:
        """delisted_at이 비어있는 종목만 채운다.

        최초 감지일을 보존하고 이후 sync에서 덮어쓰지 않는다.
        """
        if not short_codes:
            return 0
        result = (
            self._supabase.table(_TABLE)
            .update({"delisted_at": as_of.isoformat()})
            .in_("short_code", short_codes)
            .is_("delisted_at", "null")
            .execute()
        )
        return len(result.data)
