from etf_collector.infra.kis.etf_quote import map_to_etf_info_fields


def test_maps_known_fields() -> None:
    quote = {
        "mbcr_name": "삼성자산운용(ETF)",
        "etf_cu_unit_scrt_cnt": "50000",
        "etf_trc_ert_mltp": "1.00",
        "etf_div_name": "수익증권형",
    }

    fields = map_to_etf_info_fields(quote)

    assert fields == {
        "manager": "삼성자산운용(ETF)",
        "creation_unit_quantity": 50000,
        "tracking_multiplier": "1.00",
        "replication_method": "수익증권형",
    }


def test_ignores_missing_fields() -> None:
    fields = map_to_etf_info_fields({})
    assert fields == {}
