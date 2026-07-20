from datetime import UTC, date, datetime
from unittest.mock import MagicMock, call

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


def test_fetch_all_stops_at_partial_page() -> None:
    supabase = MagicMock()
    repository = EtfInfoRepository(supabase)
    page = supabase.table.return_value.select.return_value.range.return_value.execute
    page.return_value = MagicMock(data=[_row().model_dump(mode="json")])

    rows = repository.fetch_all()

    assert len(rows) == 1
    page.assert_called_once()


def test_fetch_all_paginates_past_page_size() -> None:
    supabase = MagicMock()
    repository = EtfInfoRepository(supabase)
    first_page = MagicMock(data=[_row().model_dump(mode="json") for _ in range(1000)])
    second_page = MagicMock(data=[_row().model_dump(mode="json")])
    execute = supabase.table.return_value.select.return_value.range.return_value.execute
    execute.side_effect = [first_page, second_page]

    rows = repository.fetch_all()

    assert len(rows) == 1001
    range_ = supabase.table.return_value.select.return_value.range
    assert range_.call_args_list == [call(0, 999), call(1000, 1999)]
