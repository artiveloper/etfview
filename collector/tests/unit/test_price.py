from datetime import date

from etf_collector.infra.kis.price import map_to_price_rows
from etf_collector.jobs.backfill_etf_price import iter_backfill_windows


def test_maps_output2_rows() -> None:
    output2 = [
        {
            "stck_bsop_date": "20260318",
            "stck_oprc": "35100",
            "stck_hgpr": "35200",
            "stck_lwpr": "34900",
            "stck_clpr": "35000",
            "acml_vol": "123456",
            "acml_tr_pbmn": "4321000000",
            "prdy_vrss": "-150",
            "prdy_vrss_sign": "5",
            "flng_cls_code": "00",
        },
        {
            "stck_bsop_date": "20260317",
            "stck_oprc": "35300",
            "stck_hgpr": "35400",
            "stck_lwpr": "35000",
            "stck_clpr": "35150",
            "acml_vol": "98765",
            "acml_tr_pbmn": "3456000000",
            "prdy_vrss": "100",
            "prdy_vrss_sign": "2",
            "flng_cls_code": "00",
        },
    ]

    rows = map_to_price_rows("069500", output2)

    assert len(rows) == 2
    first = rows[0]
    assert first.short_code == "069500"
    assert first.trade_date == date(2026, 3, 18)
    assert first.open_price == 35100.0
    assert first.high_price == 35200.0
    assert first.low_price == 34900.0
    assert first.close_price == 35000.0
    assert first.volume == 123456
    assert first.trading_value == 4321000000.0
    assert first.price_change == -150.0
    assert first.price_change_sign == "5"
    assert first.corporate_action_code == "00"


def test_skips_rows_without_trade_date() -> None:
    rows = map_to_price_rows("069500", [{"stck_bsop_date": ""}])
    assert rows == []


def test_iter_backfill_windows_single_day() -> None:
    windows = iter_backfill_windows(date(2026, 3, 18), date(2026, 3, 18))
    assert windows == [(date(2026, 3, 18), date(2026, 3, 18))]


def test_iter_backfill_windows_splits_by_window_size() -> None:
    windows = iter_backfill_windows(date(2026, 1, 1), date(2026, 3, 18), window_days=30)

    assert windows[0] == (date(2026, 2, 17), date(2026, 3, 18))
    assert windows[-1][0] == date(2026, 1, 1)
    for window_start, window_end in windows:
        assert window_start <= window_end


def test_iter_backfill_windows_empty_when_start_after_today() -> None:
    windows = iter_backfill_windows(date(2026, 3, 20), date(2026, 3, 18))
    assert windows == []
