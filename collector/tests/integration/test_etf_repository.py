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
    supabase.table.assert_called_once_with("etf_info")
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
