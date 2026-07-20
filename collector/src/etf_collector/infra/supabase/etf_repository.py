from etf_collector.domain.etf.models import EtfInfo
from supabase import Client

_TABLE = "etf"
# PostgREST가 요청당 반환하는 기본 상한(1000행)에 맞춘 페이지 크기. 유니버스가
# 1000종목을 넘으면 한 번의 select로는 잘리므로 range로 나눠 전부 가져온다.
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
        etfs: list[EtfInfo] = []
        offset = 0
        while True:
            # short_code(PK) 정렬로 페이지 경계를 안정화한다 — 정렬이 없으면
            # 페이지 간 순서가 어긋나 누락·중복이 생길 수 있다.
            result = (
                self._supabase.table(_TABLE)
                .select("*")
                .order("short_code")
                .range(offset, offset + _PAGE_SIZE - 1)
                .execute()
            )
            etfs.extend(EtfInfo.model_validate(row) for row in result.data)
            if len(result.data) < _PAGE_SIZE:
                break
            offset += _PAGE_SIZE
        return etfs
