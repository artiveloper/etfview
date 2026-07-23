from datetime import date

from etf_collector.infra.kis.etf_constituent import map_to_constituent_rows


def test_map_to_constituent_rows_maps_output2_fields() -> None:
    output2 = [
        {
            "stck_shrn_iscd": "005930",
            "hts_kor_isnm": "삼성전자",
            "stck_prpr": "83700",
            "prdy_vrss": "-400",
            "prdy_vrss_sign": "5",
            "prdy_ctrt": "-0.48",
            "acml_vol": "16967184",
            "acml_tr_pbmn": "1421776834400",
            "tday_rsfl_rate": "2.02",
            "prdy_vrss_vol": "-8570824",
            "tr_pbmn_tnrt": "0.28",
            "hts_avls": "601300800",
            "etf_cnfg_issu_avls": "4996708",
            "etf_cnfg_issu_rlim": "32.65",
            "etf_vltn_amt": "604174400",
        }
    ]

    rows = map_to_constituent_rows("069500", date(2026, 7, 20), output2)

    assert len(rows) == 1
    row = rows[0]
    assert row.etf_short_code == "069500"
    assert row.constituent_short_code == "005930"
    assert row.constituent_name == "삼성전자"
    assert row.weight_percentage == 32.65
    assert row.market_value_amount == 604174400
    assert row.current_price == 83700
    assert row.price_change == -400
    assert row.price_change_sign == "5"
    assert row.price_change_rate == -0.48
    assert row.volume == 16967184
    assert row.trade_amount == 1421776834400
    assert row.today_change_rate == 2.02
    assert row.volume_vs_prev_day == -8570824
    assert row.trade_turnover_rate == 0.28
    assert row.market_cap == 601300800
    assert row.constituent_market_cap == 4996708
    assert row.reference_date == date(2026, 7, 20)
    # 이 API 응답에 없는 필드는 채우지 않는다.
    assert row.held_quantity is None
    assert row.constituent_standard_code is None


def test_map_to_constituent_rows_skips_rows_without_short_code() -> None:
    output2 = [
        {"stck_shrn_iscd": "", "hts_kor_isnm": "빈코드"},
        {"hts_kor_isnm": "코드없음"},
        {"stck_shrn_iscd": "000660", "hts_kor_isnm": "SK하이닉스"},
    ]

    rows = map_to_constituent_rows("069500", date(2026, 7, 20), output2)

    assert [row.constituent_short_code for row in rows] == ["000660"]


def test_map_to_constituent_rows_handles_missing_numeric_fields() -> None:
    output2 = [{"stck_shrn_iscd": "005930", "hts_kor_isnm": "삼성전자"}]

    rows = map_to_constituent_rows("069500", date(2026, 7, 20), output2)

    assert rows[0].weight_percentage is None
    assert rows[0].market_value_amount is None
    assert rows[0].current_price is None
    assert rows[0].volume is None
    assert rows[0].market_cap is None
