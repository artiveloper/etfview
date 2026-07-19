# 국내주식기간별시세 API로 ETF 종목의 일별 주가(OHLCV) 시계열을 조회하는 모듈
from __future__ import annotations

from datetime import date
from typing import Any

from etf_collector.domain.etf.models import EtfPrice
from etf_collector.infra.kis.client import KisApiClient

_PATH = "/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice"
_TR_ID = "FHKST03010100"
_MARKET_DIV_CODE = "J"
_PERIOD_DIV_CODE = "D"
_ORG_ADJ_PRC = "0"


def _format_date(value: date) -> str:
    return value.strftime("%Y%m%d")


def _parse_yyyymmdd(raw: str) -> date | None:
    raw = raw.strip()
    if len(raw) != 8 or not raw.isdigit():
        return None
    return date(int(raw[0:4]), int(raw[4:6]), int(raw[6:8]))


async def fetch_price(
    client: KisApiClient, token: str, short_code: str, date_from: date, date_to: date
) -> list[dict[str, Any]]:
    """지정한 기간(최대 약 100거래일치)의 일별 주가 배열(output2)을 조회한다."""
    result = await client.get(
        _PATH,
        _TR_ID,
        token,
        {
            "fid_cond_mrkt_div_code": _MARKET_DIV_CODE,
            "fid_input_iscd": short_code,
            "fid_input_date_1": _format_date(date_from),
            "fid_input_date_2": _format_date(date_to),
            "fid_period_div_code": _PERIOD_DIV_CODE,
            "fid_org_adj_prc": _ORG_ADJ_PRC,
        },
    )
    output2: list[dict[str, Any]] = result["output2"]
    return output2


def map_to_price_rows(short_code: str, output2: list[dict[str, Any]]) -> list[EtfPrice]:
    """국내주식기간별시세 응답(output2)을 EtfPrice 행 목록으로 변환한다.

    trade_date를 파싱할 수 없는 행(거래일자 누락)은 건너뛴다.
    """
    rows: list[EtfPrice] = []
    for item in output2:
        trade_date = _parse_yyyymmdd(item.get("stck_bsop_date", ""))
        if trade_date is None:
            continue
        rows.append(
            EtfPrice(
                short_code=short_code,
                trade_date=trade_date,
                open_price=float(item["stck_oprc"]) if item.get("stck_oprc") else None,
                high_price=float(item["stck_hgpr"]) if item.get("stck_hgpr") else None,
                low_price=float(item["stck_lwpr"]) if item.get("stck_lwpr") else None,
                close_price=float(item["stck_clpr"]) if item.get("stck_clpr") else None,
                volume=int(item["acml_vol"]) if item.get("acml_vol") else None,
                trading_value=float(item["acml_tr_pbmn"]) if item.get("acml_tr_pbmn") else None,
                price_change=float(item["prdy_vrss"]) if item.get("prdy_vrss") else None,
                price_change_sign=item.get("prdy_vrss_sign") or None,
                corporate_action_code=item.get("flng_cls_code") or None,
            )
        )
    return rows
