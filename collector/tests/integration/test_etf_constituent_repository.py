from datetime import UTC, date, datetime
from unittest.mock import MagicMock

from etf_collector.domain.etf.constituent import EtfConstituent
from etf_collector.infra.supabase.etf_constituent_repository import EtfConstituentRepository


def _row() -> EtfConstituent:
    return EtfConstituent(
        etf_short_code="069500",
        constituent_short_code="005930",
        constituent_name="삼성전자",
        held_quantity=1000,
        weight_percentage=25.5,
        market_value_amount=75000000,
        reference_date=date(2026, 7, 18),
        updated_at=datetime(2026, 1, 1, tzinfo=UTC),
    )


def test_upsert_many_sends_payload_with_on_conflict() -> None:
    supabase = MagicMock()
    repository = EtfConstituentRepository(supabase)

    count = repository.upsert_many([_row()])

    assert count == 1
    supabase.table.assert_called_once_with("etf_constituent")
    table = supabase.table.return_value
    args, kwargs = table.upsert.call_args
    assert args[0][0]["etf_short_code"] == "069500"
    assert kwargs["on_conflict"] == "etf_short_code,constituent_short_code"
    table.upsert.return_value.execute.assert_called_once()


def test_upsert_many_returns_zero_for_empty_list() -> None:
    supabase = MagicMock()
    repository = EtfConstituentRepository(supabase)

    count = repository.upsert_many([])

    assert count == 0
    supabase.table.assert_not_called()
