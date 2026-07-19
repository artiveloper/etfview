from datetime import UTC, date, datetime
from unittest.mock import MagicMock

from etf_collector.domain.etf.models import EtfPrice
from etf_collector.infra.supabase.etf_price_repository import EtfPriceRepository


def _row() -> EtfPrice:
    return EtfPrice(
        short_code="069500",
        trade_date=date(2026, 3, 18),
        close_price=35000.0,
        volume=123456,
        updated_at=datetime(2026, 1, 1, tzinfo=UTC),
    )


def test_upsert_many_sends_payload_with_composite_on_conflict() -> None:
    supabase = MagicMock()
    repository = EtfPriceRepository(supabase)

    count = repository.upsert_many([_row()])

    assert count == 1
    supabase.table.assert_called_once_with("etf_price")
    table = supabase.table.return_value
    args, kwargs = table.upsert.call_args
    assert args[0][0]["short_code"] == "069500"
    assert args[0][0]["trade_date"] == "2026-03-18"
    assert kwargs["on_conflict"] == "short_code,trade_date"
    table.upsert.return_value.execute.assert_called_once()


def test_upsert_many_returns_zero_for_empty_list() -> None:
    supabase = MagicMock()
    repository = EtfPriceRepository(supabase)

    count = repository.upsert_many([])

    assert count == 0
    supabase.table.assert_not_called()


def test_upsert_many_sends_multiple_chunks_for_large_row_count() -> None:
    supabase = MagicMock()
    repository = EtfPriceRepository(supabase)
    rows = [_row() for _ in range(501)]

    count = repository.upsert_many(rows)

    assert count == 501
    table = supabase.table.return_value
    assert table.upsert.call_count == 2
    first_chunk = table.upsert.call_args_list[0][0][0]
    second_chunk = table.upsert.call_args_list[1][0][0]
    assert len(first_chunk) == 500
    assert len(second_chunk) == 1
