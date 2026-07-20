from datetime import date

from etf_collector.infra.krx.etf_info import map_to_etf_info, parse_etf_universe


def _row(**overrides: str) -> dict[str, str]:
    row = {
        "ISU_CD": "KR7466810009",
        "ISU_SRT_CD": "466810",
        "ISU_NM": "BNK BNK 2차전지양극재증권상장지수투자신탁(주식)",
        "ISU_ABBRV": "BNK 2차전지양극재",
        "ISU_ENG_NM": "BNK BNK Secondary Battery Cathode Materials ETF",
        "LIST_DD": "2023/10/19",
        "ETF_OBJ_IDX_NM": "iSelect 2차전지양극재 지수",
        "IDX_CALC_INST_NM1": "NH투자증권",
        "ETF_REPLICA_METHD_TP_CD": "실물(패시브)",
        "IDX_MKT_CLSS_NM": "국내",
        "IDX_ASST_CLSS_NM": "주식",
        "LIST_SHRS": "1,450,000",
        "COM_ABBRV": "비엔케이자산운용",
        "CU_QTY": "50,000",
        "ETF_TOT_FEE": "0.395000",
        "TAX_TP_CD": "비과세",
    }
    row.update(overrides)
    return row


def test_maps_row_to_etf_info() -> None:
    etf = map_to_etf_info(_row())

    assert etf.short_code == "466810"
    assert etf.standard_code == "KR7466810009"
    assert etf.name == "BNK BNK 2차전지양극재증권상장지수투자신탁(주식)"
    assert etf.abbreviated_name == "BNK 2차전지양극재"
    assert etf.english_name == "BNK BNK Secondary Battery Cathode Materials ETF"
    assert etf.listed_date == date(2023, 10, 19)
    assert etf.base_index_name == "iSelect 2차전지양극재 지수"
    assert etf.index_provider == "NH투자증권"
    assert etf.replication_method == "실물(패시브)"
    assert etf.base_market_class == "국내"
    assert etf.base_asset_class == "주식"
    assert etf.listed_shares == 1_450_000
    assert etf.manager == "비엔케이자산운용"
    assert etf.creation_unit_quantity == 50_000
    assert etf.total_fee == 0.395
    assert etf.tax_type == "비과세"


def test_maps_missing_optional_fields_to_none() -> None:
    row = _row(LIST_DD="", LIST_SHRS="", CU_QTY="", ETF_TOT_FEE="")

    etf = map_to_etf_info(row)

    assert etf.listed_date is None
    assert etf.listed_shares is None
    assert etf.creation_unit_quantity is None
    assert etf.total_fee is None


def test_parse_etf_universe_maps_multiple_rows() -> None:
    rows = [_row(), _row(ISU_SRT_CD="069500", ISU_CD="KR7069500007")]

    etfs = parse_etf_universe(rows)

    assert [etf.short_code for etf in etfs] == ["466810", "069500"]
