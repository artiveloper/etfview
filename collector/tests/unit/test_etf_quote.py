from datetime import date

from etf_collector.infra.kis.etf_quote import map_to_etf_info_fields, map_to_etf_quote_fields


def test_maps_known_fields() -> None:
    quote = {
        "mbcr_name": "삼성자산운용(ETF)",
        "etf_cu_unit_scrt_cnt": "50000",
        "etf_trc_ert_mltp": "1.00",
        "etf_div_name": "수익증권형",
    }

    fields = map_to_etf_info_fields(quote)

    assert fields == {"tracking_multiplier": "1.00"}


def test_ignores_missing_fields() -> None:
    fields = map_to_etf_info_fields({})
    assert fields == {}


def test_maps_quote_fields() -> None:
    quote = {
        "stck_prpr": "35000",
        "prdy_vrss": "-150",
        "prdy_vrss_sign": "5",
        "prdy_ctrt": "-0.43",
        "acml_vol": "123456",
        "stck_oprc": "35100",
        "stck_hgpr": "35200",
        "stck_lwpr": "34900",
        "stck_dryy_hgpr": "40000",
        "dryy_hgpr_date": "20260315",
        "stck_dryy_lwpr": "30000",
        "dryy_lwpr_date": "20260102",
        "nav": "35010.50",
        "nav_prdy_vrss": "-140",
        "nav_prdy_vrss_sign": "5",
        "nav_prdy_ctrt": "-0.40",
        "trc_errt": "0.05",
        "dprt": "-0.03",
        "etf_ntas_ttam": "1234567890",
        "etf_cnfg_issu_cnt": "200",
        "etf_crcl_stcn": "226100000",
        "frgn_hldn_qty": "52396766",
        "frgn_hldn_qty_rate": "23.17",
    }

    fields = map_to_etf_quote_fields(quote)

    assert fields == {
        "current_price": 35000.0,
        "price_change": -150.0,
        "price_change_sign": "5",
        "price_change_rate": -0.43,
        "volume": 123456,
        "open_price": 35100.0,
        "high_price": 35200.0,
        "low_price": 34900.0,
        "year_high_price": 40000.0,
        "year_high_date": date(2026, 3, 15),
        "year_low_price": 30000.0,
        "year_low_date": date(2026, 1, 2),
        "nav": 35010.50,
        "nav_change": -140.0,
        "nav_change_sign": "5",
        "nav_change_rate": -0.40,
        "tracking_error_rate": 0.05,
        "disparity_rate": -0.03,
        "net_asset_total": 1234567890.0,
        "constituent_count": 200,
        "circulating_shares": 226100000,
        "foreign_holding_qty": 52396766,
        "foreign_holding_rate": 23.17,
    }


def test_quote_fields_ignores_missing_fields() -> None:
    fields = map_to_etf_quote_fields({})
    assert fields == {}
