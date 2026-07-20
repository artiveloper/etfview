from datetime import UTC, date, datetime
from unittest.mock import MagicMock

from etf_collector.domain.etf.models import EtfInfo
from etf_collector.infra.supabase.etf_repository import EtfInfoRepository


def _row() -> EtfInfo:
    return EtfInfo(
        short_code="069500",
        standard_code="KR7069500007",
        name="KODEX 200",
        listed_date=date(2002, 10, 14),
        listed_shares=223650,
        updated_at=datetime(2026, 1, 1, tzinfo=UTC),
    )


def test_upsert_many_sends_payload_with_on_conflict() -> None:
    supabase = MagicMock()
    repository = EtfInfoRepository(supabase)

    count = repository.upsert_many([_row()])

    assert count == 1
    supabase.table.assert_called_once_with("etf")
    table = supabase.table.return_value
    args, kwargs = table.upsert.call_args
    assert args[0][0]["short_code"] == "069500"
    assert kwargs["on_conflict"] == "short_code"
    table.upsert.return_value.execute.assert_called_once()


def test_upsert_many_returns_zero_for_empty_list() -> None:
    supabase = MagicMock()
    repository = EtfInfoRepository(supabase)

    count = repository.upsert_many([])

    assert count == 0
    supabase.table.assert_not_called()


def test_fetch_all_paginates_past_page_size() -> None:
    # 1000행 상한을 넘는 유니버스를 range로 나눠 모두 가져오는지 검증한다.
    from etf_collector.infra.supabase import etf_repository as module

    monkey_page = 2
    original = module._PAGE_SIZE
    module._PAGE_SIZE = monkey_page
    try:
        pages = [
            [_row_dict("069500"), _row_dict("069501")],  # 가득 찬 페이지 → 다음 조회
            [_row_dict("069502")],  # 미만 페이지 → 종료
        ]
        supabase = MagicMock()
        query = supabase.table.return_value.select.return_value.order.return_value
        query.range.return_value.execute.side_effect = [
            MagicMock(data=pages[0]),
            MagicMock(data=pages[1]),
        ]

        repository = EtfInfoRepository(supabase)
        result = repository.fetch_all()

        assert [etf.short_code for etf in result] == ["069500", "069501", "069502"]
        assert query.range.call_args_list[0].args == (0, 1)
        assert query.range.call_args_list[1].args == (2, 3)
    finally:
        module._PAGE_SIZE = original


def _row_dict(short_code: str) -> dict[str, object]:
    return {
        "short_code": short_code,
        "standard_code": "KR7069500007",
        "name": "KODEX 200",
        "listed_date": "2002-10-14",
        "listed_shares": 223650,
        "updated_at": "2026-01-01T00:00:00+00:00",
    }
