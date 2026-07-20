from datetime import date

from etf_collector.infra.kis.etf_constituent import map_to_constituent_rows

_OUTPUT2 = [
    {
        "stck_shrn_iscd": "005930",
        "hts_kor_isnm": "삼성전자",
        "etf_cnfg_issu_rlim": "32.65",
        "etf_vltn_amt": "604174400",
    },
    {
        "stck_shrn_iscd": "000660",
        "hts_kor_isnm": "SK하이닉스",
        "etf_cnfg_issu_rlim": "8.69",
        "etf_vltn_amt": "160893600",
    },
]


def test_map_to_constituent_rows_maps_known_fields() -> None:
    rows = map_to_constituent_rows("069500", _OUTPUT2, date(2026, 7, 20))

    assert len(rows) == 2
    first = rows[0]
    assert first.etf_short_code == "069500"
    assert first.constituent_short_code == "005930"
    assert first.constituent_name == "삼성전자"
    assert first.weight_percentage == 32.65
    assert first.market_value_amount == 604174400.0
    assert first.reference_date == date(2026, 7, 20)
    assert first.constituent_standard_code is None
    assert first.held_quantity is None


def test_map_to_constituent_rows_skips_rows_without_short_code() -> None:
    rows = map_to_constituent_rows("069500", [{"hts_kor_isnm": "이름만있음"}], date(2026, 7, 20))

    assert rows == []


def test_map_to_constituent_rows_returns_empty_for_empty_output() -> None:
    assert map_to_constituent_rows("069500", [], date(2026, 7, 20)) == []
