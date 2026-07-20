# ETF 구성종목시세 API로 ETF가 보유한 구성종목(바스켓) 현황을 조회하는 모듈
from __future__ import annotations

from datetime import date
from typing import Any

from etf_collector.domain.etf.constituent import EtfConstituent
from etf_collector.infra.kis.client import KisApiClient

_PATH = "/uapi/etfetn/v1/quotations/inquire-component-stock-price"
_TR_ID = "FHKST121600C0"
_MARKET_DIV_CODE = "J"
_SCR_DIV_CODE = "11216"


async def fetch_constituents(
    client: KisApiClient, token: str, short_code: str
) -> list[dict[str, Any]]:
    """단일 ETF 종목의 구성종목 배열(output2)을 조회한다."""
    result = await client.get(
        _PATH,
        _TR_ID,
        token,
        {
            "fid_cond_mrkt_div_code": _MARKET_DIV_CODE,
            "fid_input_iscd": short_code,
            "fid_cond_scr_div_code": _SCR_DIV_CODE,
        },
    )
    output2: list[dict[str, Any]] = result["output2"]
    return output2


def map_to_constituent_rows(
    etf_short_code: str, output2: list[dict[str, Any]], reference_date: date
) -> list[EtfConstituent]:
    """구성종목시세 응답(output2)을 EtfConstituent 행 목록으로 변환한다.

    이 API는 구성종목의 표준코드(ISIN)와 보유수량을 제공하지 않아
    constituent_standard_code/held_quantity는 항상 None으로 남는다.
    """
    rows: list[EtfConstituent] = []
    for item in output2:
        constituent_short_code = item.get("stck_shrn_iscd")
        if not constituent_short_code:
            continue
        rows.append(
            EtfConstituent(
                etf_short_code=etf_short_code,
                constituent_short_code=constituent_short_code,
                constituent_name=item.get("hts_kor_isnm") or None,
                weight_percentage=(
                    float(item["etf_cnfg_issu_rlim"]) if item.get("etf_cnfg_issu_rlim") else None
                ),
                market_value_amount=(
                    float(item["etf_vltn_amt"]) if item.get("etf_vltn_amt") else None
                ),
                reference_date=reference_date,
            )
        )
    return rows
